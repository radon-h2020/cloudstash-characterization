import random
from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from artillery_report_parser import parse_artillery_output
import time
import requests
from pathlib import Path
import logging
import threading
import time
from typing import Tuple

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
    deploy_tokens: list
) -> str:

    logging.info("Thread %s: starting", index_i)

    artifact_size = random.randint(config.ARTIFACT_SIZE_LOWER, config.ARTIFACT_SIZE_UPPER)

    u_num = index_i % num_users
    username = f"user{u_num}"
    r_num = index_i % num_repos
    repository = f"repo{r_num}"
    organization = username

    stop = False
    num = index_i % num_users
    while stop == False: # continue to all artifacts have been created. We need a certain state
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
            artifact_data = benchmark_obj["artifact_raw_data"]
            logging.info("Thread %s: finishing", index_i)
            return artifact_data

def UploadArtifactsConcurrently(
    num_threads: int, 
    num_users: int, 
    deploy_tokens: list,
    num_repos: int,
    num_artifacts: int,
    benchmark: Benchmark
):
    generated_artifacts = []
    csv_header_ids = f"artifact_id\n"
    csv_ids = csv_header_ids
    csv_header_ids = f"artifact_data\n"
    csv_artifacts = csv_header_ids
    log(f"Creating {num_artifacts} artifacts split equally amongst {num_repos}...")

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    for i in range(0, num_artifacts):
        logging.info("Main    : before creating thread")
        t = threading.Thread(target=UploadSingleArtifact, 
            args=(i, num_users, num_repos, benchmark, deploy_tokens))
        logging.info("Main    : before running thread")
        t.start()
        threads.append(t)

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        artifact_raw_data = t.join()
        generated_artifacts.append(artifact_raw_data)

    logging.info("Main    : all artifacts uploaded")

    repo_ids = GetRepositorieIds(benchmark)
    artifact_names = dict()
    artifact_ids = []

    for id in repo_ids:
        artifact_names[id] = GetArtifactNames(benchmark, id)
        for (repo_id, a_name) in artifact_names:
            artifact_ids.append(GetArtifactId(benchmark, repo_id, a_name))

    for id in artifact_ids:
        csv_ids = f"{csv_ids}{id},\n"

    for data in generated_artifacts:
        csv_artifacts = f"{csv_artifacts}{data},\n"

    return (csv_ids, csv_artifacts)

def GetArtifactId(benchmark: Benchmark, repository_id: int, artifact_name: str):
    log(f"Listing artifacts to obtain artifact ids")
    endpoint_url = f"{benchmark.gateway_url}/repository/{repository_id}/artifact/{artifact_name}"
    headers = {"content-type": "application/json"}
    response = requests.get(
                    endpoint_url,
                    headers=headers,
                )
    json_obj = response.json()
    for obj in json_obj['artifacts']:
        return obj['artifactId']

def GetArtifactNames(benchmark: Benchmark, repository_id: int):
    log(f"Listing artifacts to obtain artifact names")
    names = []
    endpoint_url = f"{benchmark.gateway_url}/publicrepository\?repoType\=Function"
    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
                        endpoint_url,
                        headers=headers,
                    )
        if response.status_code == 200:
            json_objs = response.json()
            for obj in json_objs:
                names.append(obj['artifact_name'])
        else:
            log(
                f"Repository creation failed for repository{repository_id}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True
            )
            time.sleep(config.RETRY_DELAY)

    return names.strip() # remove last empty line

def GetRepositorieIds(benchmark: Benchmark):
    ids = []
    log(f"Listing repositores to obtain respository ids")
    endpoint_url = f"{benchmark.gateway_url}/publicrepository\?repoType\=Function"
    headers = {"content-type": "application/json"}
    for _ in range(0, config.RETRIES):
        response = requests.get(
                        endpoint_url,
                        headers=headers,
                    )
        if response.status_code == 200:
            json_obj = response.json()
            for repo in json_obj:
                ids.append(repo['repoId'])
        else:
            log(
                f"Failed to get ids for repositories, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

    return ids

def CreateRepositories(num_repos: int, num_users: int, tokens: list, benchmark: Benchmark):
    header = "repo_id, user\n"
    csv = header
    log(f"Creating {num_repos} repositoires split amongst {num_users} users...")
    for i in range(0, num_repos):
        uname = f"user{i%num_users}"
        repo_name = f"repository{i}"
        for _ in range(0, config.RETRIES):
            repo_created = cloudstash_create_repository(
                    benchmark, tokens[i], repo_name)

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
        uname = f"user{i}"
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

    # Apply preconditions (Multithreaded B1)
    (ids, datas) = UploadArtifactsConcurrently(
        num_upload_threads, 
        num_users, 
        deploy_tokens,
        num_repos, 
        num_artifacts,
        benchmark
    )

    WriteToFile(ids, 
        f"{base_path}/{artifact_ids_filename}"
    )
    if writeCSVToLog: log(ids)

    WriteToFile(datas, 
        f"{base_path}/{artifact_datas_filename}"
    )
    if writeCSVToLog: log(datas)

    return(True, None)
