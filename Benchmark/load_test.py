from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from artillery_report_parser import parse_artillery_output

# get config singleton
config = GlobalConfig.get()


def run_load_test(benchmark: Benchmark):
    artillery_script = ""

    ###
    # Deploy cloudstash
    ###

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    gateway_url, deployed = deploy_cloudstash(benchmark.stage)

    # make sure everything is ready before starting benchmark
    #  log(f"Waiting {config.ORCHESTRATION_DELAY} seconds before starting benchmark")
    #  sleep(config.ORCHESTRATION_DELAY)

    ###
    # Run the benchmark
    ###

    # run benchmark
    benchmark_run, report_file = run_artillery(artillery_script, gateway_url)

    # save when the experiment finished running
    benchmark.log_experiment_stop_time()

    ###
    # Parse artillery output
    ###
    parsed = parse_artillery_output(report_file)

    ###
    # Teardown cloudstash instance
    ###

    # remove the cloudstash deployment
    removed = remove_deployment(benchmark.stage)
