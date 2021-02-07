import random
from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from artillery_report_parser import parse_artillery_output
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

def CreateRepositories(num: int, benchmark: Benchmark):
    header = "repository\n"
    csv = f"{header}"
    log(f"Creating {num} repositoires...")
    for i in range(0, num):
        uname = f"user{i}"
        pword = "pass"
        cloudstash_create_user(
            benchmark,
            uname, 
            pword
        )
        csv_line = f"{uname},{pword}\n"
        csv = f"{csv}{csv_line}"
    
    return csv

def CreateUsers(num: int, benchmark: Benchmark):
    header = "username, password\n"
    csv = f"{header}"
    log(f"Creating {num} users...")
    for i in range(0, num):
        uname = f"user{i}"
        pword = "pass"
        for _ in range(0, config.RETRIES):

            cloudstash_create_user(
                benchmark,
                uname, 
                pword
            )
            
            user_created, deploy_token = cloudstash_create_user(
                benchmark, 
                uname, 
                pword)

            # login user to get session token
            if user_created:
                logged_in, session_token = cloudstash_login_user(
                benchmark, 
                uname, 
                pword)
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
    return csv

def WriteToFile(csv: str, filepath: str):
    f = open(filepath, "x") # Create. Fail if exists
    f.write(csv)
    f.close()

def EnsurePathCreated(path: str):
    from pathlib import Path
    Path("/my/directory").mkdir(parents=True, exist_ok=True)

def run_benchmark(benchmark: Benchmark) -> (bool, dict):

    # Write out some meta on benchmark params?


    # list to hold benchmark results
    # results = []
    base_path = "/home/alpine/artifacts/B2" # TODO: Ensure created
    EnsurePathCreated(base_path)

    user_filename = "created_users.csv"
    repo_filename = "created_repositories.csv"
    artifact_ids_filename = "created_artifacts.csv"

    # Create 10 users
        # output created users to csv
    WriteToFile(CreateUsers(10), f"{base_path}/{user_filename}")

    # Create 10 repositories
    WriteToFile(CreateRepositories(10), f"{base_path}/{repo_filename}")

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

