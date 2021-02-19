import time
from utils import shell, log
from config import GlobalConfig
from typing import Tuple

# get config singleton
config = GlobalConfig.get()


def run_artillery(script_file: str, gateway_url: str, print_output_to_stdout: bool = False) -> Tuple[bool, dict]:
    log(f"Running Artillery with script {script_file}")

    # output report timestamp
    timestamp = time.strftime("%Y-%d_%m-%H_%M_%S", time.localtime())
    output_file = f"{config.BENCHMARK_OUTPUT_PATH}/{timestamp}-report.json"
    log(f"Outputting report to {output_file}")

    # set environment variables for the artillery process
    env = {"gateway_url": gateway_url}
    # create artillery command to be run
    artillery_cmd = f"""{config.ARTILLERY_BIN_PATH} run --output {output_file} {script_file}"""

    # run artillery command
    res = shell(artillery_cmd, context=config.ARTILLERY_CODE_PATH, env=env)

    # print the output of the artillery command to stdout?
    if print_output_to_stdout:
        log(f"Artillery run stdout: {res.stdout}")

    if res.returncode == 0:
        log(f"Successfully finished running artillery script {script_file}")
        return (True, output_file)
    else:
        log(
            f"There was an error running artillery script {script_file}, returncode was {res.returncode}",
            error=True,
        )
        log(f"(artillery stdout) {res.stdout}", error=True)
        return (False, None)


# TEST
#  gateway_url = "https://ryjtk5xgpg.execute-api.eu-west-1.amazonaws.com/deploy-test-1"
#  script_file = "create_users.yml"
#  run_artillery(script_file, gateway_url)
