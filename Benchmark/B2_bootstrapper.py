import random
from utils import log
from config import GlobalConfig
from benchmark import Benchmark
import time
import requests
from pathlib import Path
import logging
from typing import Tuple
import uuid
from time import time
import multiprocessing
from time import sleep
from threading import Thread

USERNAMEPREFIX = f"user{str(uuid.uuid4())[:8]}"

from cloudstash_api_wrapper import (
    cloudstash_create_user,
    cloudstash_create_repository,
    cloudstash_upload_artifact,
    cloudstash_login_user,
)

# get config singleton
config = GlobalConfig.get()

# set random seed
random.seed(config.RANDOM_SEED)

class GetArtifactIdWorkerThread(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            benchmark, repo_id, a_name, artifact_ids = self.queue.get()
            try:
                GetArtifactId(benchmark, repo_id, a_name, artifact_ids)
            finally:
                self.queue.task_done()

class GetArtifactIdWorkerProcess(multiprocessing.Process):

    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue

    def run(self):
        threads = []
        for _ in range(multiprocessing.cpu_count() * 2): # Start threads inside process
            
            thread = GetArtifactIdWorkerThread(self.queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            thread.daemon = True
            thread.start()

            threads.append(thread)

        for t in threads:
            t.join()


class GetArtifactNamesWorkerThread(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            benchmark, repository_id, artifact_names_per_id = self.queue.get()
            try:
                GetArtifactNames(benchmark, repository_id, artifact_names_per_id)
            finally:
                self.queue.task_done()

class GetArtifactNamesWorkerProcess(multiprocessing.Process):

    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue

    def run(self):
        threads = []
        for _ in range(multiprocessing.cpu_count() * 2): # Start threads inside process
            
            thread = GetArtifactNamesWorkerThread(self.queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            thread.daemon = True
            thread.start()

            threads.append(thread)

        for t in threads:
            t.join()


class UploadWorkerThread(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            index_i, num_users, num_repos, benchmark, deploy_tokens, datas = self.queue.get()
            try:
                UploadSingleArtifact(index_i, num_users, num_repos, benchmark, deploy_tokens, datas)
            finally:
                self.queue.task_done()

class UploadWorkerProcess(multiprocessing.Process):

    def __init__(self, queue):
        multiprocessing.Process.__init__(self)
        self.queue = queue

    def run(self):
        threads = []
        for _ in range(multiprocessing.cpu_count() * 2): # Start threads inside process
            thread = UploadWorkerThread(self.queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            thread.daemon = True
            thread.start()

            threads.append(thread)

        for t in threads:
            t.join()



# Multithreaded payload function
def UploadSingleArtifact(
    index_i: int,
    num_users: int,
    num_repos: int,
    benchmark: Benchmark,
    deploy_tokens: list,
    datas: list
) -> str:

    if config.VERBOSE:
        logging.info("Processing %s: starting", index_i)

    artifact_size = random.randint(config.ARTIFACT_SIZE_LOWER, config.ARTIFACT_SIZE_UPPER)

    u_num = index_i % num_users
    username = f"{USERNAMEPREFIX}{u_num}"
    r_num = index_i % num_repos
    repository = f"repo{r_num}"
    organization = username

    stop = False
    num = index_i % num_users
    while not stop : # continue to all artifacts have been created. We need a certain state
        success, benchmark_obj = cloudstash_upload_artifact(
            benchmark,
            index_i,
            artifact_size,
            username,
            deploy_tokens[num],
            repository,
            organization
        )
        stop = success

        if success == True:
            # artifact_data = benchmark_obj["artifact_raw_data"]
            artifact_data = benchmark_obj["payload"]
            if config.VERBOSE:
                logging.info("Processing %s: finishing", index_i)
            datas.append(artifact_data)

def UploadArtifactsConcurrently(
    num_processes: int, 
    num_users: int, 
    deploy_tokens: list,
    num_repos: int,
    num_artifacts: int,
    benchmark: Benchmark
):
    # THREADSAFE COLLECTIONS
    generated_artifacts = []

    # CSV HEADERS START
    csv_header_ids = f"artifact_id\n"
    csv_artifact_ids = csv_header_ids

    csv_header_json = f"json\n"
    csv_artifact_json = csv_header_json

    csv_header_repo_ids = f"repo_id\n"
    csv_repo_ids = csv_header_repo_ids

    csv_header_ids = f"artifact_name,version,description,repositoryName,organization,provider,runtime,handler,applicationToken,file\n"
    csv_artifacts = csv_header_ids
    # CSV HEADERS END

    log(f"Creating {num_artifacts} artifacts split equally amongst {num_repos} repositories...")

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    
    ts = time()
    # Create a queue to communicate with the worker threads
    queue = multiprocessing.JoinableQueue()
    # Create worker threads
    for _ in range(num_processes):
        worker = UploadWorkerProcess(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    # Put the tasks into the queue as a tuple
    for i in range(0, num_artifacts):
        if config.REALLYVERBOSE:
            logging.info('Queueing {}'.format(i))
        queue.put((i, num_users, num_repos, benchmark, deploy_tokens, generated_artifacts))

    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    if config.VERBOSE:
        logging.info('Took %s', time() - ts)

    ####
    # Single threaded due to only single API call
    ####
    repo_ids = GetRepositorieIds(benchmark)

    ####
    # Multi threaded from here on
    ####

    #
    # Obtain Artifact Names
    #
    if config.VERBOSE:
        log(f"Listing artifacts to obtain artifact names")

    ts = time()
    # Create a queue to communicate with the worker threads
    queue = multiprocessing.JoinableQueue()
    # Create worker threads
    for _ in range(num_processes):
        worker = GetArtifactNamesWorkerProcess(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    
    artifact_names_per_id = data = {k: [] for k in repo_ids}
    # Put the tasks into the queue as a tuple
    for i in range(0, len(repo_ids)-1):
        if config.REALLYVERBOSE:
            logging.info('Queueing {}'.format(i))
        queue.put((benchmark, repo_ids[i], artifact_names_per_id))
    
    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    if config.VERBOSE:
        logging.info('Get Artifact Names Took %s', time() - ts)

    #
    # Get Ids for artifact names
    #

    if config.VERBOSE:
        log(f"Listing artifacts to obtain artifact ids")

    ts = time()
    # Create a queue to communicate with the worker threads
    queue = multiprocessing.JoinableQueue()
    # Create worker threads
    for _ in range(num_processes):
        worker = GetArtifactIdWorkerProcess(queue)
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    
    artifact_ids = []
    # Put the tasks into the queue as a tuple
    for repo_id in artifact_names_per_id:
        for a_name in artifact_names_per_id[repo_id]:
            if config.REALLYVERBOSE:
                logging.info('Queueing {}'.format(a_name))
            queue.put((benchmark, repo_id, a_name, artifact_ids))
    
    # Causes the main thread to wait for the queue to finish processing all the tasks
    queue.join()
    if config.VERBOSE:
        logging.info('Took %s', time() - ts)

    ####
    # Single threaded from here on. Optimize later maybe
    ####

    for id in repo_ids:
        csv_repo_ids = f"{csv_repo_ids}{id}\n"

    for id in artifact_ids:
        csv_artifact_ids = f"{csv_artifact_ids}{id}\n"

    for data in generated_artifacts:
        csv_artifact_json = f"{csv_artifact_json}{data}\n"

    for data in generated_artifacts:
        artifact_name = data["artifact_name"]
        version = data["version"]
        description = data["description"]
        repositoryName = data["repositoryName"]
        organization = data["organization"]
        provider = data["provider"]
        runtime = data["runtime"]
        handler = data["handler"]
        applicationToken = data["applicationToken"]
        file = data["file"]

        data_as_line = f"{artifact_name},{version},{description},{repositoryName},{organization},{provider},{runtime},{handler},{applicationToken},{file}"
        csv_artifacts = f"{csv_artifacts}{data_as_line}\n"

    return (csv_artifact_ids, csv_repo_ids, csv_artifacts, csv_artifact_json)

def GetArtifactId(benchmark: Benchmark, repository_id: int, artifact_name: str, artifact_ids: list):
    endpoint_url = f"{benchmark.gateway_url}/repository/{repository_id}/artifact/{artifact_name}"
    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
            endpoint_url,
            headers=headers,
        )
        if response.status_code == 200:
            json_obj = response.json()
            for obj in json_obj: # should only be 1. Ok to return
                artifact_ids.append(obj['artifactId'])
                return 
        else: 
            log(
                f"Failed to get artifact id for repo {repository_id} artifact {artifact_name}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            log(
                f"Status code {response.status_code} endpoint url {endpoint_url}",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

def GetArtifactNames(benchmark: Benchmark, repository_id: int, artifact_names: dict):
    a_name_list = artifact_names[repository_id]
    endpoint_url = f"{benchmark.gateway_url}/repository/{repository_id}"
    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
            endpoint_url, 
            headers=headers
        )

        if response.status_code == 200:
            json_objs = response.json()
            for obj in json_objs['artifacts']:
                a_name_list.append(f"{obj['group_name']}/{obj['artifact_name']}")
            return
        else:
            log(
                f"Repository creation failed for repository{repository_id}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True
            )
            time.sleep(config.RETRY_DELAY)

def GetRepositorieIds(benchmark: Benchmark):
    log(f"Listing repositores to obtain respository ids")
    endpoint_url = f"{benchmark.gateway_url}/publicrepository"
    ids = []

    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
            endpoint_url,
            headers=headers,
            params= {'repoType': 'Function'}
        )

        if response.status_code == 200:
            json_obj = response.json()
            for repo in json_obj['repositories']:
                org = repo['repoOrg']
                # if USERNAMEPREFIX in org:
                ids.append(repo['repoId'])
            return ids

        else:
            log(
                f"Failed to get ids for repositories, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            log(
                f"Status code {response.status_code} endpoint url {endpoint_url}",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

def CreateRepositories(num_repos: int, num_users: int, tokens: list, benchmark: Benchmark):
    header = "repo_id, user\n"
    csv = header
    log(f"Creating {num_repos} repositoires split amongst {num_users} users...")
    for i in range(0, num_repos):
        uname = f"{USERNAMEPREFIX}{i%num_users}"
        repo_name = f"repo{i}"
        for _ in range(0, config.RETRIES):
            repo_created = cloudstash_create_repository(
                    benchmark, 
                    tokens[i], 
                    repo_name
            )

            if repo_created:
                csv_line = f"{repo_name},{uname}\n"
                csv = f"{csv}{csv_line}"
                break
            else:
                log(
                    f"Repository creation failed for repository{i}, waiting {config.RETRY_DELAY}s before trying again.",
                    error=True,
                )
                time.sleep(config.RETRY_DELAY)

    return csv.strip() # remove last empty line

def CreateUsers(num: int, benchmark: Benchmark):
    session_tokens = []
    deploy_tokens = []
    header = "username, password, session_token, deploy_token\n"
    csv = f"{header}"

    log(f"Creating {num} users...")
    for i in range(0, num):
        uname = f"{USERNAMEPREFIX}{i}"
        pword = "pass"
        for _ in range(0, config.RETRIES):
            user_created, deploy_token = cloudstash_create_user(
                benchmark, 
                uname, 
                pword
            )
            deploy_tokens.append(deploy_token)

            # login user to get session token
            if user_created:
                logged_in, session_token = cloudstash_login_user(
                    benchmark, 
                    uname, 
                    pword
                )
                if logged_in:
                    session_tokens.append(session_token)
                    csv_line = f"{uname},{pword},{session_token},{deploy_token}\n"
                    csv = f"{csv}{csv_line}"
                    break
                else:
                    log(
                        f"User login failed  when logging in user {uname}, waiting {config.RETRY_DELAY}s before trying again.",
                        error=True,
                    )
                    time.sleep(config.RETRY_DELAY)
            else:
                log(
                    f"User creation failed  when creating user {uname}, waiting {config.RETRY_DELAY}s before trying again.",
                    error=True,
                )
                time.sleep(config.RETRY_DELAY)

    return (csv.strip(), session_tokens, deploy_tokens)

def WriteToFile(csv: str, filepath: str):
    f = open(filepath, "w") # Overwrite if exists
    f.write(csv)
    f.close()

def EnsurePathCreated(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def run_bootstrap(benchmark: Benchmark) -> Tuple[bool, dict]:

    # TODO: Write out some meta on precondition params?
    
    writeCSVToLog = False

    base_path = config.BENCHMARK_OUTPUT_PATH #"/home/alpine/artifacts/B2"
    EnsurePathCreated(base_path)

    num_users = 10
    num_repos = 10
    num_processes = multiprocessing.cpu_count()
    num_upload_threads = multiprocessing.cpu_count() * 2
    num_artifacts = benchmark.number_of_artefacts

    log(f"Running on CPU with {multiprocessing.cpu_count()} cores. Will run bootstrapper with {num_processes} processes which each will have {num_upload_threads} threads")
    sleep(5.0)

    user_filename = "created_users.csv"
    repo_filename = "created_repositories.csv"
    repoid_filename = "created_repository_ids.csv"
    artifact_ids_filename = "created_artifact_ids.csv"
    artifact_datas_filename = "created_artifact_datas.csv"

    (user_csv, session_tokens, deploy_tokens) = CreateUsers(num_users, benchmark)
    WriteToFile(user_csv, f"{base_path}/{user_filename}")
    if writeCSVToLog: log(user_csv)

    repo_csv = CreateRepositories(
        num_repos,
        num_users,
        session_tokens,
        benchmark
    )
    WriteToFile(repo_csv, f"{base_path}/{repo_filename}")
    if writeCSVToLog: log(repo_csv)

    # Replace Repository Names with Repository Ids

    # Apply preconditions (Multithreaded B1)
    (ids, repo_ids, datas, json_csv) = UploadArtifactsConcurrently(
        num_upload_threads, 
        num_users, 
        deploy_tokens,
        num_repos, 
        num_artifacts,
        benchmark
    )
    WriteToFile(repo_ids, 
        f"{base_path}/{repoid_filename}"
    )
    if writeCSVToLog: log(repo_ids)

    WriteToFile(ids, 
        f"{base_path}/{artifact_ids_filename}"
    )
    if writeCSVToLog: log(ids)

    WriteToFile(datas, 
        f"{base_path}/{artifact_datas_filename}"
    )
    if writeCSVToLog: 
        log(f"Datas Count: {datas.splitlines().__len__()-1}")
        # log(f"Example data: {datas.splitlines()[1]}")

    return(True, None)
