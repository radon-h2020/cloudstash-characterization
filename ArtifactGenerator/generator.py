import os
import time
import sys
import uuid
from random import seed, randint
from zipfile import ZipFile

seed(time.time())


def create_payload(size: int = 4096, filename: str = "payload.txt") -> None:
    payload = ""
    for i in range(size):
        payload = payload + f"{randint(0, 9)}"

    with open(filename, "w") as pf:
        pf.write(payload)

    print("Payload size on disc: ", os.stat(filename).st_size)
    print("Payload size as object in Python3 (with 49 bytes overhead, unicode string) ", sys.getsizeof(payload))


def create_cloudstash_config_file(cloudstash_org: str, cloudstash_repo: str, filename: str = "config.ini") -> None:
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


def create_zip_archive(filename: str = "artifact.zip", files_to_be_zipped: list[str] = []) -> None:
    with ZipFile(filename, "w") as zf:
        for _file in files_to_be_zipped:
            zf.write(_file)
            os.remove(_file)
    print(f"Zip size: {os.stat(filename).st_size}")


# run as script from cli
if __name__ == "__main__":
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