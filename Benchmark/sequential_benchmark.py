from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark

# get config singleton
config = GlobalConfig.get()


def run_sequential_benchmark(benchmark: Benchmark):
    artillery_script = ""

    ###
    # Deploy cloudstash
    ###

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    gateway_url, deployed = deploy_cloudstash(benchmark.stage)

    # make sure everything is ready before starting benchmark
    #  log(f"Waiting {delay} seconds before starting benchmark")
    #  sleep(delay)

    ###
    # Run the benchmark
    ###

    # run benchmark
    benchmark_run = run_artillery(artillery_script, gateway_url)

    # TODO parse artillery output step

    ###
    # Teardown cloudstash instance
    ###

    # remove the cloudstash deployment
    removed = remove_deployment(benchmark.stage)
