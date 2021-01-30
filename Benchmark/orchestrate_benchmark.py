from argparse import ArgumentParser
from time import sleep
from uuid import uuid4
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark

# get config singleton
config = GlobalConfig.get()

###
# cli arg parse boilerplate
###

# Create the cli parser
cli_args_parser = ArgumentParser(
    description="Orchestrate deployment, running, logging and teardown of cloudstash benchmarks",
    epilog="By @zanderhavgaard & @ChristofferNissen for the Radon H2020 Project",
)

# define the cli arguments
cli_args_parser.add_argument(
    "benchmark",
    type=str,
    help="Which benchmark to run, should be one of: 'sequential_upload', 'load_test'",
)
cli_args_parser.add_argument(
    "number_of_artefacts",
    type=int,
    help="The number of artefacts to upload during the benchmark",
)
cli_args_parser.add_argument("--verbose", action="store_true", help="Enable more verbose messages")
cli_args_parser.add_argument("--debug", action="store_true", help="Enable debug prints")

# parse the cli arguments
cli_args = cli_args_parser.parse_args()

# update config defaults
if cli_args.verbose:
    config.VERBOSE = True
if cli_args.debug:
    config.DEBUG = True

# load cli args into variables
number_of_artefacts = cli_args.number_of_artefacts
benchmark_to_run = cli_args.benchmark

###
# Setup benchmark metadata
###

# set the deployed stage to be a random uuid of 8 chars
stage = str(uuid4())[:8]

# create the benchmark object
benchmark = Benchmark(benchmark=benchmark_to_run, stage=stage, number_of_artefacts=number_of_artefacts)

###
# Run benchmark
###

if benchmark_to_run is "sequential_upload":
    print('foo')
elif benchmark_to_run is "load_test":
    print('bar')
else:


# === TODO these should be read from cli
# what stage to deploy
#  stage = "deploy-test-1"
# what artillery script to run on the deployed cloudstash
#  artillery_script = "create_users.yml"
#  gateway_url = "https://zn0reubddh.execute-api.eu-west-1.amazonaws.com/deploy-test-1"
# ===

###
# Deploy cloudstash
###

# deploy cloudstash using serverless, get the api gateway url of the deployment
#  gateway_url, deployed = deploy_cloudstash(stage)

# make sure everything is ready before starting benchmark
#  log(f"Waiting {delay} seconds before starting benchmark")
#  sleep(delay)

###
# Run the benchmark
###

# run benchmark
#  benchmark_run = run_artillery(artillery_script, gateway_url, True)
#  benchmark_run = run_artillery(artillery_script, gateway_url)

# TODO parse artillery output step

###
# Teardown cloudstash instance
###

# remove the cloudstash deployment
#  removed = remove_deployment(stage)
