import random
from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from artillery_report_parser import parse_artillery_output
import time
from typing import Tuple
import requests
from pathlib import Path
import logging
import threading
import time

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


def UploadSingleArtifact(i: int, num_users: int, num_repos: int, benchmark: Benchmark, deploy_tokens: list):
    logging.info("Thread %s: starting", i)
    
    artifact_size = random.randint(
            config.ARTIFACT_SIZE_LOWER, config.ARTIFACT_SIZE_UPPER)

    u_num = i % num_users
    username = f"user{u_num}"
    r_num = i % num_repos
    repository = f"{r_num}"
    organization = username

    stop = False
    num = i % num_users
    while stop == False: # continue to all artifacts have been created. We need a certain state
        success, _ = cloudstash_upload_artifact(
            benchmark,
            i,
            artifact_size,
            username,
            deploy_tokens[num],
            repository,
            organization
        )
        stop = success

    logging.info("Thread %s: finishing", i)

def UploadArtifactsConcurrently(threads: int, num_users: int, deploy_tokens: list,
        num_repos: int, num_artifacts: int, benchmark: Benchmark):

    csv_header = f"id\n"
    csv = csv_header
    log(f"Creating {num_artifacts} artifacts split equally amongst {num_repos}...")

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    for i in range(0, num_artifacts):
        logging.info("Main    : before creating thread")
        x = threading.Thread(target=UploadSingleArtifact, 
            args=(i,num_users, num_repos, benchmark, deploy_tokens))
        logging.info("Main    : before running thread")
        x.start()
        threads.append(x)

    logging.info("Main    : wait for the thread to finish")
    for t in threads:
        t.join()

    logging.info("Main    : all artifacts uploaded")

    repo_ids = GetRepositorieIds(benchmark)
    artifact_names = dict
    artifact_ids = []

    for id in repo_ids:
        artifact_names[id](GetArtifactNames(benchmark, id))
        for (repo_id, a_name) in artifact_names:
            artifact_ids.append(GetArtifactId(benchmark, repo_id, a_name))

    for id in artifact_ids:
        csv = f"{csv}{id}\n"

    return csv

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
    names = []
    log(f"Listing artifacts to obtain artifact names")
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
                f"Repository creation failed for repository{i}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
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
    header = "repository, user\n"
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
    f = open(filepath, "x") # Create. Fail if exists
    f.write(csv)
    f.close()

def EnsurePathCreated(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def run_benchmark(benchmark: Benchmark) -> Tuple[bool, dict]:

    # TODO: Write out some meta on precondition params?

    base_path = config.BENCHMARK_OUTPUT_PATH #"/home/alpine/artifacts/B2"
    EnsurePathCreated(base_path)

    num_users = 10
    num_repos = 10
    num_artifacts = 100
    num_upload_threads = 10

    user_filename = "created_users.csv"
    repo_filename = "created_repositories.csv"
    artifact_ids_filename = "created_artifacts.csv"

    (user_csv, session_tokens, deploy_tokens) = CreateUsers(num_users, benchmark)
    WriteToFile(user_csv, f"{base_path}/{user_filename}")

    WriteToFile(CreateRepositories
        (
            num_repos,
            num_users,
            session_tokens,
            benchmark
            ), 
        f"{base_path}/{repo_filename}"
    )

    # Apply preconditions (Multithreaded B1)
    WriteToFile(UploadArtifactsConcurrently
        (
            num_upload_threads, 
            num_users, 
            deploy_tokens,
            num_repos, 
            num_artifacts
        ), 
        f"{base_path}/{artifact_ids_filename}"
    )

    return(True, [])
