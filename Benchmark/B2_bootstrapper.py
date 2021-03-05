import random
from utils import log
from config import GlobalConfig
from benchmark import Benchmark
import time
import requests
from pathlib import Path
import logging
import threading
import time
from typing import Tuple
import uuid

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

# Multithreaded payload function
def UploadSingleArtifact(
    index_i: int,
    num_users: int,
    num_repos: int,
    benchmark: Benchmark,
    deploy_tokens: list,
    datas: list
) -> str:

    logging.info("Thread %s: starting", index_i)

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
            logging.info("Thread %s: finishing", index_i)

            # import base64

            # Standard Base64 Encoding
            # encodedBytes = base64.b64encode(artifact_data.encode("utf-8"))
            # encodedStr = str(encodedBytes, "utf-8")
            datas.append(artifact_data)

def UploadArtifactsConcurrently(
    num_threads: int, 
    num_users: int, 
    deploy_tokens: list,
    num_repos: int,
    num_artifacts: int,
    benchmark: Benchmark
):
    # THREAD COLLECTIONS
    threads = []
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

    log(f"Creating {num_artifacts} artifacts split equally amongst {num_repos}...")

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    
    for i in range(0, num_artifacts):
        logging.info("Main    : before creating thread")
        t = threading.Thread(target=UploadSingleArtifact, 
            args=(i, num_users, num_repos, benchmark, deploy_tokens, generated_artifacts))
        logging.info("Main    : before running thread")
        t.start()
        threads.append(t)

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()
        # generated_artifacts.append(artifact_raw_data)

    logging.info("Main    : all artifacts uploaded")

    ####
    # Single threaded from here on. Optimize later maybe
    ####

    repo_ids = GetRepositorieIds(benchmark)
    artifact_ids = []

    for id in repo_ids:
        a_names = GetArtifactNames(benchmark, id)
        for a_name in a_names:
            artifact_ids.append(GetArtifactId(benchmark, id, a_name))

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

def GetArtifactId(benchmark: Benchmark, repository_id: int, artifact_name: str):
    log(f"Listing artifacts to obtain artifact ids")
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
                return obj['artifactId']
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


def GetArtifactNames(benchmark: Benchmark, repository_id: int):
    log(f"Listing artifacts to obtain artifact names")
    names = []
    endpoint_url = f"{benchmark.gateway_url}/repository/{repository_id}" #\?repoType\=Function"
    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
            endpoint_url, 
            headers=headers
        )

        if response.status_code == 200:
            json_objs = response.json()
            for obj in json_objs['artifacts']:
                names.append(f"{obj['group_name']}/{obj['artifact_name']}")
            return names

        else:
            log(
                f"Repository creation failed for repository{repository_id}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True
            )
            time.sleep(config.RETRY_DELAY)

def GetRepositorieIds(benchmark: Benchmark):
    ids = []
    log(f"Listing repositores to obtain respository ids")
    endpoint_url = f"{benchmark.gateway_url}/publicrepository"
    # \?repoType\=Function

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
    
    writeCSVToLog = True

    base_path = config.BENCHMARK_OUTPUT_PATH #"/home/alpine/artifacts/B2"
    EnsurePathCreated(base_path)

    num_users = 10
    num_repos = 10
    num_upload_threads = 10
    num_artifacts = benchmark.number_of_artefacts

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
