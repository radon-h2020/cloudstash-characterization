import time
from utils import shell, log
from config import GlobalConfig
from typing import Tuple

# get config singleton
config = GlobalConfig.get()


def run_artillery(script_file: str, gateway_url: str, print_output_to_stdout: bool = False, use_serverless_artillery: bool = False) -> Tuple[bool, dict]:
    log(f"Running Artillery with script {script_file}")

    # output report timestamp
    timestamp = time.strftime("%Y-%d_%m-%H_%M_%S", time.localtime())
    output_file = f"{config.BENCHMARK_OUTPUT_PATH}/{timestamp}-report.json"
    log(f"Outputting report to {output_file}")

    # set environment variables for the artillery process
    res = None
    env = {
        "gateway_url": gateway_url, 
        "ramp_up_duration": "120",
        "ramp_up_arrivalrate ": "10",
        "ramp_up_to": "50",
        "load_duration": "600",
        "arrivalRate": "30"
    }

    # create artillery command to be run
    if use_serverless_artillery:
        artillery_cmd = f"""{config.SERVERLESS_ARTILLERY_BIN_PATH} deploy --stage CCSTUDY"""
        res = shell(artillery_cmd, context=config.ARTILLERY_CODE_PATH, env=env)
        if res.returncode == 0:
            artillery_cmd = f"""{config.SERVERLESS_ARTILLERY_BIN_PATH} invoke --path {script_file} --stage CCSTUDY --jsonOnly"""
            invoke_res = shell(artillery_cmd, context=config.ARTILLERY_CODE_PATH, env=env)
            if invoke_res.returncode == 0:
                artillery_cmd = f"""{config.SERVERLESS_ARTILLERY_BIN_PATH} remove --stage CCSTUDY"""
                res = shell(artillery_cmd, context=config.ARTILLERY_CODE_PATH, env=env)

    else:
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
