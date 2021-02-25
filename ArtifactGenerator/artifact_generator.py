import os
import time
import sys
import uuid
from random import seed, randint
from zipfile import ZipFile
from pathlib import Path

seed(time.time())

VERBOSE = False


def create_payload(size: int = 4096, filename: str = "payload.txt") -> None:
    # if payload file already exists, then delete it
    if os.path.isfile(filename):
        os.remove(filename)

    payload = ""
    for _ in range(size):
        payload = payload + f"{randint(0, 9)}"

    with open(filename, "w") as pf:
        pf.write(payload)

    if VERBOSE:
        print("Payload size on disc: ", os.stat(filename).st_size)
        print("Payload size as object in Python3 (with 49 bytes overhead, unicode string) ", sys.getsizeof(payload))


def create_cloudstash_config_file(cloudstash_org: str, cloudstash_repo: str, filename: str = "config.ini") -> None:
    # if config file already exists, then delete it
    if os.path.isfile(filename):
        os.remove(filename)

    artifact_name = uuid.uuid4()
    artifact_version = uuid.uuid4()
    config_text = f"""
[REPOSITORY]
org = {cloudstash_org}
repository = {cloudstash_repo}

[FUNCTION]
name = {artifact_name}
version = {artifact_version}
description = Randomly generated artifact containing binary nonsense.

[RUNTIME]
provider = aws
runtime = python3.8
handler = handler"""
    with open(filename, "w") as cf:
        cf.write(config_text)


def create_zip_archive(filename: str = "artifact.zip", files_to_be_zipped: list = []) -> None:
    # if zipfile file already exists, then delete it
    if os.path.isfile(filename):
        os.remove(filename)

    with ZipFile(filename, "w") as zf:
        for _file in files_to_be_zipped:
            if "payload" in _file:
                zf.write(_file, "payload.txt")
            if "config" in _file:
                zf.write(_file, "config.ini")
            if not "config.ini" in _file:
                os.remove(_file)
    if VERBOSE:
        print(f"Zip size: {os.stat(filename).st_size}")


def generate_artifact(
    artifact_size: int,
    artifact_name: str,
    cloudstash_repo: str,
    cloudstash_org: str,
) -> bool:
    try:
        TEMPFOLDERPREFIX = f"TMP{str(uuid.uuid4())[:8]}"
        Path(TEMPFOLDERPREFIX).mkdir(parents=True, exist_ok=True)
        payload_file = f"{TEMPFOLDERPREFIX}/payload.txt"
        config_file = f"{TEMPFOLDERPREFIX}/config.ini"

        # create binary nonsense file to simulate function code
        create_payload(size=artifact_size, filename=payload_file)
        # create a cloudstash config file
        create_cloudstash_config_file(
            cloudstash_org=cloudstash_org, cloudstash_repo=cloudstash_repo, filename=config_file
        )

        files_to_be_zipped = [payload_file, config_file]
        create_zip_archive(filename=artifact_name, files_to_be_zipped=files_to_be_zipped)
        
        os.remove(config_file)
        os.rmdir(TEMPFOLDERPREFIX) # Clean up tmp folder
        return True

    except Exception as err:
        print(f"Encountered an error creating artifact {artifact_name}, the error was: {err}")
        return False


# run as script from cli
if __name__ == "__main__":
    VERBOSE = True
    payload_file = "payload.txt"
    config_file = "config.ini"
    artifact_size = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
    zip_file = sys.argv[2] if len(sys.argv) > 2 else "artifact.zip"
    cloudstash_org = sys.argv[3] if len(sys.argv) > 3 else "benchmark"
    cloudstash_repo = sys.argv[4] if len(sys.argv) > 4 else "benchmark-artifacts"
    if len(sys.argv) > 5:
        zip_files = True if sys.argv[5] in ["true", "True"] else False
    else:
        zip_files = True

    if zip_files:
        print(f"Desired size: {artifact_size}, Zipping {zip_files}")
        artifact_size = artifact_size - 120
    else:
        print(f"Desired artifact_size: {artifact_size}, Zipping {zip_files}")

    # create binary nonsense file to simulate function code
    create_payload(size=artifact_size, filename=payload_file)
    # create a cloudstash config file
    create_cloudstash_config_file(cloudstash_org=cloudstash_org, cloudstash_repo=cloudstash_repo, filename=config_file)
    # create zip file to be uploaded to cloudstash
    if zip_files:
        files_to_be_zipped = [payload_file, config_file]
        create_zip_archive(filename=zip_file, files_to_be_zipped=files_to_be_zipped)
