import sys

sys.path.append("../ArtifactGenerator")  # noqa
import csv
import uuid
import time
import json
import shutil
import errno
import base64
import os
import random
from typing import Tuple
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

# set random seed
random.seed(config.RANDOM_SEED)


def run_sequential_benchmark(benchmark: Benchmark):
    ###
    # Deploy cloudstash
    ###
    log("----- Create Infrastructure")

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    gateway_url, deployed = deploy_cloudstash(benchmark.stage)
    # set gateway_url in benchmark object
    benchmark.gateway_url = gateway_url

    # make sure everything is ready before starting benchmark
    log(f"Waiting {config.ORCHESTRATION_DELAY} seconds before starting benchmark")
    sleep(config.ORCHESTRATION_DELAY)

    ###
    # Run the benchmark
    ###
    log("----- Run Benchmark")

    # run benchmark
    if deployed:
        benchmark_ran, benchmark_data = run_benchmark(benchmark)

        #  save when the experiment finished running
        benchmark.log_experiment_stop_time()

    ###
    # Parse benchmark output
    ###
    log("----- Parse Benchmark results")

    if benchmark_ran:
        benchmark_output_file = f"{config.BENCHMARK_OUTPUT_PATH}/{benchmark.stage}-{benchmark.benchmark}-{benchmark.number_of_artefacts}.csv"
        wrote_file = write_benchmark_results_csv_file(
            benchmark, benchmark_output_file, benchmark_data)

    ###
    # Teardown cloudstash instance
    ###
    log("----- Remove Benchmark Infrastructure")

    # remove the cloudstash deployment
    removed = remove_deployment(benchmark.stage)

    ###
    # End Benchmark orchestration
    ###
    log("-----")
    log(f"Benchmark orchestration finished.")
    log(f"Benchmark running time: {benchmark.running_time}")


def write_benchmark_results_csv_file(bencmark: Benchmark, results_filename: str, results: list) -> bool:
    log(f"Writing benchmark data to file: {results_filename}")
    benchmark_data_fieldnames = [
        "start_time",
        "end_time",
        "total_time",
        "status_code",
        "artifact_num",
        "artifact_name",
        "artifact_size",
        "repository",
        "user",
    ]
    with open(results_filename, "w") as csvfile:
        csvfile_writer = csv.DictWriter(
            csvfile, fieldnames=benchmark_data_fieldnames)
        csvfile_writer.writeheader()
        for result in results:
            csvfile_writer.writerow(result)
        log("Done writing benchmark data.")
        return True
    return False


def run_benchmark(benchmark: Benchmark) -> Tuple[bool, dict]:
    # list to hold benchmark results
    results = []

    username = str(uuid.uuid4())[:8]
    password = "password"
    repository = f"{username}-benchmark-1"
    organization = username

    # Create one user
    user_created, deploy_token = cloudstash_create_user(
        benchmark, username, password)

    # login user to get session token
    if user_created:
        logged_in, session_token = cloudstash_login_user(
            benchmark, username, password)

        # Create one respository
        if logged_in:
            repo_created = cloudstash_create_repository(
                benchmark, session_token, repository)

            if user_created and repo_created:
                # Execute the sequential load test
                # for the number of artifacts specified in benchmark:
                for i in range(0, benchmark.number_of_artefacts):
                    if config.VERBOSE:
                        log(f"Processing request #{i} ...")
                    # do some incremental logging
                    if i % 100 == 0:
                        log(f"Processing request #{i} ...")

                    artifact_size = random.randint(
                        config.ARTIFACT_SIZE_LOWER, config.ARTIFACT_SIZE_UPPER)

                    # make sure that we do not add the same benchmark_data multiple times
                    benchmark_data = None

                    # benchmark uploading an artifact
                    success, benchmark_data = cloudstash_upload_artifact(
                        benchmark, i, artifact_size, username, deploy_token, repository, organization
                    )

                    # save data from upload attempt
                    if benchmark_data is not None:
                        results.append(benchmark_data)

        return (True, results)
    else:
        return (False, None)
