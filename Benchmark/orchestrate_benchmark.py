import sys
from argparse import ArgumentParser
from time import sleep
from uuid import uuid4
from utils import shell, log
from config import GlobalConfig
from benchmark import Benchmark
from sequential_benchmark import run_sequential_benchmark
from load_test import run_load_test

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
    log("Verbose outputs enabled.")
if cli_args.debug:
    config.DEBUG = True
    log("Debug outputs enabled.")

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

if benchmark_to_run == "sequential_upload":
    run_sequential_benchmark(benchmark)
elif benchmark_to_run == "load_test":
    run_load_test(benchmark)
else:
    print("You must pass one of 'sequential_upload' or 'load_test' as the benchmark argument.")
    sys.exit(1)
