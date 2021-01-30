from argparse import ArgumentParser
from time import sleep
import config
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery

# Create the cli parser
cli_args_parser = ArgumentParser(
    description="Orchestrate deployment/removal of cloudstash instance and run sequential benchmark of function artefact uploads",
    epilog="By @zanderhavgaard & @ChristofferNissen for the Radon H2020 Project",
)

# define the cli arguments
cli_args_parser.add_argument(
    "number_of_artefacts",
    type=int,
    help="The number of artefacts to upload during the benchmark",
)
cli_args_parser.add_argument("--verbose", action="store_true", help="Enable more verbose messages")
cli_args_parser.add_argument("--debug", action="store_true", help="Enable debug prints")

# parse the cli arguments, and load them into python vars
cli_args = cli_args_parser.parse_args()
if cli_args.verbose:
    config.VERBOSE = True
number_of_artefacts = cli_args.number_of_artefacts

print("number_of_artefacts", number_of_artefacts)

res = shell("echo foo")
log(res.stdout)

# === TODO these should be read from cli
# how long to wait between operations, for everyting to be ready
delay = 60
# what stage to deploy
stage = "deploy-test-1"
# what artillery script to run on the deployed cloudstash
artillery_script = "create_users.yml"
gateway_url = "https://zn0reubddh.execute-api.eu-west-1.amazonaws.com/deploy-test-1"
# ===

# deploy cloudstash using serverless, get the api gateway url of the deployment
#  gateway_url, deployed = deploy_cloudstash(stage)

# make sure everything is ready before starting benchmark
#  log(f"Waiting {delay} seconds before starting benchmark")
#  sleep(delay)

# run benchmark
#  benchmark_run = run_artillery(artillery_script, gateway_url, True)
#  benchmark_run = run_artillery(artillery_script, gateway_url)

# TODO parse artillery output step

# remove the cloudstash deployment
#  removed = remove_deployment(stage)
