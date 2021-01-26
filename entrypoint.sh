#!/bin/bash

# TODO change to run on orchestration server

docker run --rm -it \
    -v /home/zander/eficode/radon/cloudstash-characterization/EC2/secrets/.aws:/home/alpine/.aws \
    -v /home/zander/eficode/radon/cloudstash/serverless:/home/alpine/serverless \
    -v /home/zander/eficode/radon/cloudstash-characterization:/home/alpine/cloudstash-characterization \
    cctest:latest \
    bash
