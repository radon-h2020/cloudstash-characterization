import random
from time import sleep
from utils import shell, log
from deploy_remove_cloudstash import deploy_cloudstash, remove_deployment
from run_artillery import run_artillery
from config import GlobalConfig
from benchmark import Benchmark
from artillery_report_parser import parse_artillery_output
from B2_bootstrapper import run_bootstrap, WriteToFile

# get config singleton
config = GlobalConfig.get()

# set random seed
random.seed(config.RANDOM_SEED)


def run_load_test(benchmark: Benchmark):
    ###
    # Deploy cloudstash
    ###

    shouldDeploy = True

    log("----- Create Infrastructure")

    # deploy cloudstash using serverless, get the api gateway url of the deployment
    
    if shouldDeploy:
        gateway_url, deployed = deploy_cloudstash(benchmark.stage)
        # set gateway_url in benchmark object
        benchmark.gateway_url = gateway_url
    else: 
        benchmark.gateway_url = "https://tav1nup498.execute-api.eu-west-1.amazonaws.com/0ab0856d"
        deployed = True


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
        # filename for benchmark results .csv
        benchmark_output_file = f"{config.BENCHMARK_OUTPUT_PATH}/{benchmark.stage}-{benchmark.benchmark}-{benchmark.number_of_artefacts}.csv"
        # function to write benchmark results .csv
        wrote_file = write_benchmark_results_csv_file(benchmark, benchmark_output_file, benchmark_data)

    ###
    # Teardown cloudstash instance
    ###
    log("----- Remove Benchmark Infrastructure")

    if shouldDeploy:
        # remove the cloudstash deployment
        removed = remove_deployment(benchmark.stage)

    ###
    # End Benchmark orchestration
    ###
    log("-----")
    log(f"Benchmark orchestration finished.")
    log(f"Benchmark running time: {benchmark.running_time}")


def write_benchmark_results_csv_file(bencmark: Benchmark, results_filename: str, results: list) -> bool:
    WriteToFile(results, results_filename)
    pass


def run_benchmark(benchmark: Benchmark) -> (bool, dict):
    
    benchmark_status, benchmark_data = run_bootstrap(benchmark)

    # def run_artillery(script_file: str, gateway_url: str, print_output_to_stdout: bool = False) -> Tuple[bool, dict]:
    run_artillery("Benchmark/load_test.yml", benchmark.gateway_url, True)

    # TODO: Change to artillery output rather than bootstrapping
    
    return(benchmark_status, benchmark_data)

