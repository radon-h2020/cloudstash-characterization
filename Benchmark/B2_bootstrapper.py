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

def CreateArtifacts(threads: int, num_users: int, deploy_tokens: list,
        num_repos: int, num_artifacts: int, benchmark: Benchmark):

    csv_header = f"id"

    # Apply preconditions (Multithreaded B1)
    # start 10 threads, 1 thread uploads to one repo
        # if too slow, up to 10 threads per repo
        # file names are predicable
    # Test with 10, 100, 1000
    # Benchmark with 1000, 10000, 100.000

    log(f"Creating {num_artifacts} artifacts split equally amongst {num_repos}...")

    for i in range(0, num_artifacts):

        artifact_size = random.randint(
            config.ARTIFACT_SIZE_LOWER, config.ARTIFACT_SIZE_UPPER)

        username = f"user{i%num_users}"
        repository = f"repo{i%num_repos}"
        organization = username

        success, benchmark_data = cloudstash_upload_artifact(
            benchmark,
            i,
            artifact_size,
            username,
            deploy_tokens[i%num_users],
            repository,
            organization
        )

    # Obtain ids for uploaded artifacts by query
        # Use list repo => list artifacts => list versions to get artifact_id
        
        # curl https://cloudstash.io/publicrepository\?repoType\=Function | jq
        # curl https://cloudstash.io/repository/48ce911ec127539ad841688ed5a34f | jq
        # curl https://cloudstash.io/repository/48ce911ec127539ad841688ed5a34f/artifact/aws\.python3\.8/snyk\_test | jq
    repo_ids = GetRepositorieIds(benchmark)
    artifact_names = dict
    artifact_ids = []

    for id in repo_ids:
        artifact_names[id](GetArtifactNames(benchmark, id))

    for (repo_id, a_name) in artifact_names:
        artifact_ids.append(GetArtifactId(benchmark, repo_id, a_name))

    # write artifacts to csv file

def GetArtifactId(benchmark: Benchmark, repository_id: int, artifact_name: str):
    log(f"Listing artifacts to obtain artifact ids")
    # extract artifact name from JSON
    endpoint_url = f"{benchmark.gateway_url}repository/{repository_id}/artifact/{artifact_name}"
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
    response = requests.get(
                    endpoint_url,
                    headers=headers,
                )
    json_objs = response.json()
    # extract artifact name from JSON
    for obj in json_objs:
        names.append(obj['artifact_name'])

    return names

def GetRepositorieIds(benchmark: Benchmark):
    ids = []
    log(f"Listing repositores to obtain respository ids")
    endpoint_url = f"{benchmark.gateway_url}/publicrepository\?repoType\=Function"
    headers = {"content-type": "application/json"}
    response = requests.get(
                    endpoint_url,
                    headers=headers,
                )
    json_obj = response.json()

    # parse JSON
    for repo in json_obj:
        ids.append(repo['repoId'])

    return ids

def CreateRepositories(num_repos: int, num_users: int, tokens: list, benchmark: Benchmark):
    header = "repository\n"
    csv = f"{header}"
    log(f"Creating {num_repos} repositoires...")
    for i in range(0, num_repos):
        uname = f"user{i}"
        pword = "pass"
        for _ in range(0, config.RETRIES):
            repo_created = cloudstash_create_repository(
                    benchmark, tokens[i], f"repository{i}")

            if repo_created:
                    break
            else:
                log(
                    f"Repository creation failed for repository{i}, waiting {config.RETRY_DELAY}s before trying again.",
                    error=True,
                )
                time.sleep(config.RETRY_DELAY)

        csv_line = f"{uname},{pword}\n"
        csv = f"{csv}{csv_line}"
    
    return csv

def CreateUsers(num: int, benchmark: Benchmark):
    session_tokens = []
    deploy_tokens = []
    header = "username, password\n"
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
                session_tokens.append(session_token)
                csv_line = f"{uname},{pword},{session_token},{logged_in}\n"
                csv = f"{csv}{csv_line}"

                if logged_in:
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

    return (csv, session_tokens, deploy_tokens)

def WriteToFile(csv: str, filepath: str):
    f = open(filepath, "x") # Create. Fail if exists
    f.write(csv)
    f.close()

def EnsurePathCreated(path: str):
    from pathlib import Path
    Path("/my/directory").mkdir(parents=True, exist_ok=True)

def run_benchmark(benchmark: Benchmark) -> Tuple[bool, dict]:

    # TODO: Write out some meta on benchmark params?

    results = [] # list to hold benchmark results
    base_path = "/home/alpine/artifacts/B2"
    EnsurePathCreated(base_path)

    num_users = 10
    num_repos = 10
    num_artifacts = 100
    num_upload_threads = 10

    user_filename = "created_users.csv"
    repo_filename = "created_repositories.csv"
    artifact_ids_filename = "created_artifacts.csv"

    # Create 10 users
        # output created users to csv
    (user_csv, session_tokens, deploy_tokens) = CreateUsers(10, benchmark)
    WriteToFile(user_csv, f"{base_path}/{user_filename}")

    # Create 10 repositories
    WriteToFile(CreateRepositories(num_repos, num_users, session_tokens, benchmark), f"{base_path}/{repo_filename}")

    # Apply preconditions (Multithreaded B1)
        # start 10 threads, 1 thread uploads to one repo
            # if too slow, up to 10 threads per repo
            # file names are predicable
        # Test with 10, 100, 1000
        # Benchmark with 1000, 10000, 100.000

    # Obtain ids for uploaded artifacts by query
        # Use list repo => list artifacts => list versions to get artifact_id
        
        # curl https://cloudstash.io/publicrepository\?repoType\=Function | jq
        # curl https://cloudstash.io/repository/48ce911ec127539ad841688ed5a34f | jq
        # curl https://cloudstash.io/repository/48ce911ec127539ad841688ed5a34f/artifact/aws\.python3\.8/snyk\_test | jq
    WriteToFile(CreateArtifacts
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
