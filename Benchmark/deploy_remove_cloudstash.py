#!/bin/python

import os
import sys
import re
import time
from utils import shell, log
from config import GlobalConfig

# get the config singleton
config = GlobalConfig.get()


def deploy_cloudstash(stage: str) -> (str, bool):
    if not os.path.isdir(f"{config.CLOUDSTASH_CODE_PATH}/node_modules"):
        log("Moving node_modules directory to /home/alpine/serverless")
        mv_cmd = f"mv /home/alpine/node_modules {config.CLOUDSTASH_CODE_PATH}/"
        mv_cmd_res = shell(mv_cmd)
        if mv_cmd_res.returncode != 0:
            log(mv_cmd_res.stdout, error=True)
            log("There was an error moving the node_modules to the serverless directory, exitting ...", error=True)
            sys.exit(1)
    else:
        log("Found existing node_modules.")

    log(f"Deploying Cloudstash to stage {stage}")
    cmd = f"serverless deploy --stage {stage}"
    res = shell(cmd, context=config.CLOUDSTASH_CODE_PATH)
    returncode = res.returncode

    while returncode != 0 and config.RETRIES > 0:
        log(
            f"Deploying cloudstash to stage {stage} had returncode {returncode}, will retry deploying {config.RETRIES} more times.",
            error=True,
        )
        log(f"(serverless deploy stdout) {res.stdout}", error=True)
        log(f"Wating {config.RETRY_DELAY} seconds before next attempt.")
        time.sleep(config.RETRY_DELAY)
        config.RETRIES -= 1
        # retry shell command
        res = shell(cmd, context=config.CLOUDSTASH_CODE_PATH)
        returncode = res.returncode

    if returncode != 0 and config.RETRIES == 0:
        log("Error deploying cloudstash, max number of retries reached, exitting ...", error=True)
        sys.exit(1)

    # if successfully deployed, return no error message, and True
    log(f"Successfully deployed cloudstash to stage {stage}")
    if config.VERBOSE:
        log(f"(serverless deploy stdout) {res.stdout}")
    gateway_url = find_apigateway_url(res.stdout)
    if gateway_url is None:
        log("No API Gateway could be found.", error=True)
        return (None, False)
    log(f"Found API Gateway {gateway_url}")
    return (gateway_url, True)


def remove_deployment(stage: str) -> bool:
    log(f"Removing Cloudstash with stage {stage}")

    log("Removing artifact bucket and deleting all artifacts ...")
    delete_s3_bucket_cmd = f"aws s3 rb s3://artifacts-{stage} --force"
    s3_del_res = shell(delete_s3_bucket_cmd, context=config.CLOUDSTASH_CODE_PATH)
    if config.VERBOSE:
        log(f"(aws s3 rb stdout) {s3_del_res.stdout}")
    s3_del_rc = s3_del_res.returncode
    if s3_del_rc != 0:
        log("Error deleteing artifacts s3 bucket", error=True)
        log(f"(aws s3 rb stdout) {s3_del_res.stdout}")

    if s3_del_rc == 0:

        log("Removing cloudstash resources using serverless remove ...")
        cmd = f"serverless remove --stage {stage}"
        res = shell(cmd, context=config.CLOUDSTASH_CODE_PATH)
        returncode = res.returncode

        while returncode != 0 and config.RETRIES > 0:
            log(
                f"Removing cloudstash with stage {stage} had returncode {returncode}, will retry removing {config.RETRIES} more times.",
                error=True,
            )
            log(f"(serverless remove stdout) {res.stdout}", error=True)
            log(f"Wating {config.RETRY_DELAY} seconds before next attempt.")
            time.sleep(config.RETRY_DELAY)
            config.RETRIES -= 1
            # retry remove
            res = shell(cmd, context=config.CLOUDSTASH_CODE_PATH)
            returncode = res.returncode

        if returncode != 0 and config.RETRIES == 0:
            log("Error removing cloudstash, max number of retries reached, exitting ...", error=True)
            sys.exit(1)

        # if successfully deployed, return no error message, and True
        log(f"Successfully removed cloudstash with stage {stage}")
        if config.VERBOSE:
            log(f"(serverless remove stdout) {res.stdout}")

        return True
    else:
        return False


def find_apigateway_url(log_output: str) -> str:
    # regex to match urls that look like 'ttps://89p9orlkfl.execute-api.eu-west-1.amazonaws.com/foo/'
    regex = r"https:\/\/[\D\d]{10}\.execute\-api\..*\.amazonaws\.com\/[a-zA-Z0-9\-]+\/"
    matcher = re.compile(regex)
    search = matcher.search(log_output)
    if search is not None:
        match = search.group()
        # strip last / from string
        match = match[:-1]
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
