import requests
import base64
import time
from configparser import Error as configparser_error, NoOptionError, ConfigParser
from benchmark import Benchmark
from artifact_generator import generate_artifact
from utils import shell, log
from config import GlobalConfig
from os import path
from zipfile import ZipFile 
import io

# get config singleton
config = GlobalConfig.get()

def read_config(config_file_bytes: bytes):
    try:
        # original
        # config = ConfigParser()
        # config.read(config_file)
        
        config = ConfigParser()
        config.read_string(config_file_bytes.decode("utf-8"))
        return config
    except configparser_error as e:
        log("Error reading artifact config file.", error=True)
        raise e


def cloudstash_create_user(benchmark: Benchmark, username: str, password: str) -> (bool, str):
    log(f"Creating user {username} to obtain deploy token...")

    payload = {
        "username": username,
        "password": password,
    }
    endpoint_url = f"{benchmark.gateway_url}/signup"
    headers = {"content-type": "application/json"}

    for _ in range(0, config.RETRIES):
        response = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
        )
        if response.status_code == 200:
            break
        else:
            log(
                f"Received {response.status_code} status code when creating user {username}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

    log(f"Create user request HTTP status code: {response.status_code}")
    message_str_split = response.json()["message"].split(" ")  # extract from response
    deploy_token = message_str_split[
        len(message_str_split) - 1
    ]  # take out last word of return message, should be token
    log(f"Obtained deploy token {deploy_token}")

    if deploy_token is not None and type(deploy_token) is str and deploy_token != "error":
        return (True, deploy_token)
    else:
        log("Something went wrong trying to create cloudstash user", error=True)
        return (False, None)


def cloudstash_login_user(benchmark: Benchmark, username: str, password: str) -> (bool, str):
    log(f"Logging in user {username} to obtain session token.")
    endpoint_url = f"{benchmark.gateway_url}/login"
    payload = {
        "username": username,
        "password": password,
    }

    for _ in range(0, config.RETRIES):
        response = requests.post(
            endpoint_url,
            json=payload,
        )
        if response.status_code == 200:
            break
        else:
            log(
                f"Received {response.status_code} status code when logging in user {username}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

    log(f"User {username} login request HTTP status code {response.status_code}")

    # parse the session token from response headers
    session_token = response.headers["Set-Cookie"].split(";")[0].split("=")[1]
    log(f"Acquired session token {session_token}")

    if response.status_code == 200:
        return (True, session_token)
    else:
        return (False, None)


def cloudstash_create_repository(benchmark: Benchmark, session_token: str, repository_name: str) -> bool:
    log(f"Creating repository for user account...")
    repo_type = "Function"

    payload = {
        "repository": repository_name,
        "repositoryType": repo_type,
        "repositoryAvailability": "public",
    }
    endpoint_url = f"{benchmark.gateway_url}/repository"
    headers = {"content-type": "application/json"}
    cookies = {"authtoken": session_token}

    for _ in range(0, config.RETRIES):
        response = requests.post(
            endpoint_url,
            json=payload,
            headers=headers,
            cookies=cookies,
        )
        if response.status_code == 200:
            break
        else:
            log(
                f"Received {response.status_code} status code when creating repository {repository_name}, waiting {config.RETRY_DELAY}s before trying again.",
                error=True,
            )
            time.sleep(config.RETRY_DELAY)

        log(f"Create repository request HTTP status code {response.status_code}")

    return True


def cloudstash_upload_artifact(
    benchmark: Benchmark,
    artifact_num: int,
    artifact_size: int,
    username: str,
    deploy_token: str,
    repository: str,
    org: str
) -> True:

    artifact_zip_file = f"{artifact_num}_artifact.zip"
    artifact_filename = f"{config.ARTIFACT_STORE_PATH}/{artifact_zip_file}"

    # if artifact has already been created, existing artifact will be used
    # retry up to 5 times to generate artifact
    for _ in range(0, 5):
        artifact_created = path.exists(artifact_filename)
        if not artifact_created:
            artifact_created = generate_artifact(
                artifact_size=artifact_size,
                artifact_name=artifact_filename,
                cloudstash_repo=repository,
                cloudstash_org=org,
            )
        else:
            break

    if artifact_created:
        # upload artifact to cloudstash

        config_as_bytes = None
        with ZipFile(artifact_filename) as zip:
            with zip.open('config.ini') as configfile:
                config_as_bytes = configfile.read()

        artifact_config = read_config(config_as_bytes)
        payload = {}
        try:
            payload["artifact_name"] = artifact_config.get("FUNCTION", "name")
            payload["version"] = artifact_config.get("FUNCTION", "version")
            payload["description"] = artifact_config.get("FUNCTION", "description")
            payload["repositoryName"] = artifact_config.get("REPOSITORY", "repository") #repository 
            payload["organization"] = artifact_config.get("REPOSITORY", "org")
            payload["provider"] = artifact_config.get("RUNTIME", "provider")
            payload["runtime"] = artifact_config.get("RUNTIME", "runtime")
            payload["handler"] = artifact_config.get("RUNTIME", "handler")
            payload["applicationToken"] = deploy_token

            # TODO what is going on here ??? Taken from Functionhub-Cli
            with open(artifact_filename, "rb") as binfile:
                file_content = binfile.read()
                encoded = base64.b64encode(file_content)
            payload["file"] = encoded.decode()
            
            if config.VERBOSE:
                log(f"upload function {payload['artifact_name']} to repository {payload['repositoryName']}")

            headers = {"content-type": "application/json", "Authorization": deploy_token}
            endpoint_url = f"{benchmark.gateway_url}/artifact"
            response = None
            start_time = time.time()

            try:
                response = requests.post(
                    endpoint_url,
                    json=payload,
                    headers=headers,
                )
            except Exception as err:
                log(f"Encountered an error uploading artifact {artifact_num}, the error was: {err}", error=True)

            end_time = time.time()
            total_time = end_time - start_time

            if response is not None:
                if config.VERBOSE:
                    log(f"Upload Artifact HTTP status code: {response.status_code}")

                # dict containing data for the upload
                benchmark_data = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "total_time": total_time,
                    "status_code": response.status_code,
                    "artifact_num": artifact_num,
                    "artifact_name": artifact_zip_file,
                    "artifact_size": artifact_size,
                    "repository": repository,
                    "user": username,
                    "artifact_raw_data": payload["file"],
                    "payload": payload
                }

                if response.status_code == 200:
                    return (True, benchmark_data)
                else:
                    return (False, benchmark_data)
            else:
                log("Something went wrong uploading artifact {artifact_num}, continueing ...", error=True)
                return (False, None)

        except (KeyError, NoOptionError, requests.exceptions.RequestException) as err:
            log(f"Encountered an error trying to upload artifact #{artifact_num} error:{err}", error=True)
            return False

    else:
        return False

