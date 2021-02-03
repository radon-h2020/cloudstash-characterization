#!/bin/bash

docker run --rm -it \
    -v /home/ubuntu/.aws:/home/alpine/.aws:ro \
    -v /home/ubuntu/cloudstash/serverless:/home/alpine/serverless \
    docker.pkg.github.com/radon-h2020/cloudstash-characterization/cloudstash-benchmarker:main \
    bash
