#!/bin/python

import re
import time
from config import VERBOSE
from utils import shell, log
from config import CLOUDSTASH_CODE_PATH


def deploy_cloudstash(stage: str) -> (str, bool):
    retries = 10
    retry_delay = 60

    import os

    if not os.path.isdir(f"{CLOUDSTASH_CODE_PATH}/node_modules"):
        log("Moving node_modules directory to /home/alpine/serverless")
        #  mv_cmd = f"[ ! -d {CLOUDSTASH_CODE_PATH}/node_modules ] && mv /home/alpine/node_modules {CLOUDSTASH_CODE_PATH}"
        mv_cmd = f"mv /home/alpine/node_modules {CLOUDSTASH_CODE_PATH}/"
        mv_cmd_res = shell(mv_cmd)
        if mv_cmd_res.returncode != 0:
            log(mv_cmd_res.stdout, error=True)
            log("There was an error moving the node_modules to the serverless directory, exitting ...", error=True)
            exit(1)
    else:
        log("Found existing node_modules.")

    log(f"Deploying Cloudstash to stage {stage}")
    cmd = f"serverless deploy --stage {stage}"
    res = shell(cmd, context=CLOUDSTASH_CODE_PATH)
    returncode = res.returncode

    while returncode != 0 and retries > 0:
        log(
            f"Deploying cloudstash to stage {stage} had returncode {returncode}, will retry deploying {retries} more times.",
            error=True,
        )
        log(f"(serverless deploy stdout) {res.stdout}", error=True)
        log(f"Wating {retry_delay} seconds before next attempt.")
        time.sleep(retry_delay)
        retries -= 1
        # retry shell command
        res = shell(cmd, context=CLOUDSTASH_CODE_PATH)
        returncode = res.returncode

    if returncode != 0 and retries == 0:
        log("Error deploying cloudstash, max number of retries reached, exitting ...", error=True)
        exit(1)

    # if successfully deployed, return no error message, and True
    log(f"Successfully deployed cloudstash to stage {stage}")
    if VERBOSE:
        log(f"(serverless deploy stdout) {res.stdout}")
    gateway_url = find_apigateway_url(res.stdout)
    if gateway_url is None:
        log("No API Gateway could be found.", error=True)
        return (None, False)
    log(f"Found API Gateway {gateway_url}")
    return (gateway_url, True)


def remove_deployment(stage: str) -> bool:
    retries = 10
    retry_delay = 60
    log(f"Removing Cloudstash with stage {stage}")
    cmd = f"serverless remove --stage {stage}"
    res = shell(cmd, context=CLOUDSTASH_CODE_PATH)
    returncode = res.returncode

    while returncode != 0 and retries > 0:
        log(
            f"Removing cloudstash with stage {stage} had returncode {returncode}, will retry removing {retries} more times.",
            error=True,
        )
        log(f"(serverless remove stdout) {res.stdout}", error=True)
        log(f"Wating {retry_delay} seconds before next attempt.")
        time.sleep(retry_delay)
        retries -= 1
        # retry remove
        res = shell(cmd, context=CLOUDSTASH_CODE_PATH)
        returncode = res.returncode

    if returncode != 0 and retries == 0:
        log("Error removing cloudstash, max number of retries reached, exitting ...", error=True)
        exit(1)

    # if successfully deployed, return no error message, and True
    log(f"Successfully removed cloudstash with stage {stage}")
    if VERBOSE:
        log(f"(serverless remove stdout) {res.stdout}")

    return True


def find_apigateway_url(log_output: str) -> str:
    # regex to match urls that look like 'ttps://89p9orlkfl.execute-api.eu-west-1.amazonaws.com/foo/'
    regex = "https:\/\/[\D\d]{10}\.execute\-api\..*\.amazonaws\.com\/[a-zA-Z0-9\-]+\/"
    matcher = re.compile(regex)
    search = matcher.search(log_output)
    if search is not None:
        match = search.group()
        return match
    else:
        return None


# TEST
#  stage = "deploy-test-1"
#  gateway_url, deployed = deploy_cloudstash(stage)
#  time.sleep(10)
#  print()
#  print()
#  print("deployed", deployed)
#  print("gateway_url", gateway_url)
#  print()
#  print()
#  removed = remove_deployment(stage)
#  print()
#  print()
#  print("removed", removed)
#  print()
#  print()
