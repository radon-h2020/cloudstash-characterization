#!/bin/bash

docker run --rm -it \
    -v /home/alpine/cloudstash-characterization/EC2/secrets/.aws:/home/alpine/.aws:ro \
    -v /home/alpine/cloudstash/serverless:/home/alpine/serverless \
    docker.pkg.github.com/radon-h2020/cloudstash-characterization/cloudstash-benchmarker:main \
    bash
