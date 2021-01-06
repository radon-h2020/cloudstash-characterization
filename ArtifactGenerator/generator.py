import os
import time
import sys
import uuid
from random import seed, randint
from zipfile import ZipFile

seed(time.time())
payload_file = "payload.txt"
config_file = "config.ini"
cloudstash_org = "benchmark"
cloudstash_repo = "benchmark-artifacts"
zip_file = "artifact.zip"
artifact_size = 4096


def create_payload(size: int = 4096, filename: str = "payload.txt", zip: bool = True) -> None:

    if zip:
        print(f"Desired size: {size}, Zipping {zip}")
        size = size - 120
    else:
        print(f"Desired size: {size}, Zipping {zip}")

    payload = ""
    for i in range(size):
        payload = payload + f"{randint(0, 9)}"

    with open(filename, "w") as pf:
        pf.write(payload)

    print("Payload size:")
    print("On disc: ", os.stat(filename).st_size)
    print("As object in Python3 (with 49 bytes overhead, unicode string) ", sys.getsizeof(payload))


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


create_payload(size=artifact_size, filename=payload_file)
create_cloudstash_config_file(cloudstash_org=cloudstash_org, cloudstash_repo=cloudstash_repo, filename=config_file)

#  if zip:
#  zipName = "sample.zip"
#  print("Zip size:")
#  zipObj = ZipFile(zipName, "w")
#  zipObj.write(payload_file)
#  zipObj.close()
#  os.remove(payload_file)
#  print(os.stat(zipName).st_size)
