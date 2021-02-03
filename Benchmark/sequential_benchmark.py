import sys

sys.path.append("../ArtifactGenerator")  # noqa
import time
import json
import shutil
import errno
import base64
import os
from time import sleep
from artillery_report_parser import parse_artillery_output
from benchmark import Benchmark
from artifact_generator import generate_artifact
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from cloudstash_api_wrapper import (
    cloudstash_create_user,
    cloudstash_create_repository,
    cloudstash_upload_artifact,
    cloudstash_login_user,
)

# get config singleton
config = GlobalConfig.get()


def run_sequential_benchmark(benchmark: Benchmark):

    ###
    # Deploy cloudstash
    ###

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    #  gateway_url, deployed = deploy_cloudstash(benchmark.stage)
    # set gateway_url in benchmark object
    #  benchmark.gateway_url = gateway_url

    benchmark.gateway_url = "https://gnr7g9tfj2.execute-api.eu-west-1.amazonaws.com/b018670f"

    # make sure everything is ready before starting benchmark
    #  log(f"Waiting {config.ORCHESTRATION_DELAY} seconds before starting benchmark")
    #  sleep(config.ORCHESTRATION_DELAY)

    ###
    # Run the benchmark
    ###

    # run benchmark
    benchmark_sucess, report_file = run_benchmark(benchmark)

    # save when the experiment finished running
    #  benchmark.log_experiment_stop_time()

    ###
    # Parse artillery output
    ###
    #  parsed = parse_artillery_output(report_file)

    ###
    # Teardown cloudstash instance
    ###

    # remove the cloudstash deployment
    #  removed = remove_deployment(benchmark.stage)


def run_benchmark(benchmark: Benchmark) -> (bool, str):
    #  username = "user1"
    #  password = "password1"
    import uuid

    username = str(uuid.uuid4())[:8]
    password = "password1"
    repository = f"{username}-benchmark-1"
    organization = username

    # Create one user
    user_created, deploy_token = cloudstash_create_user(benchmark, username, password)

    # login user to get session token
    logged_in, session_token = cloudstash_login_user(benchmark, username, password)

    # Create one respository
    repo_created = cloudstash_create_repository(benchmark, session_token, repository)

    # flush prints
    sys.stdout.flush()

    if user_created and repo_created:
        # Execute the sequential load test
        # for the number of artifacts specified in benchmark:
        for i in range(0, benchmark.number_of_artefacts):
            log(f"Processing request {i}")
            success = cloudstash_upload_artifact(benchmark, i, deploy_token, repository, organization)

            # flush prints
            sys.stdout.flush()

        # TODO
        report_filename = ""
        return True, report_filename
