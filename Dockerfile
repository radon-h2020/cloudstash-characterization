FROM alpine:3

# do not print warnings when installing node packages
ENV npm_config_loglevel=silent
# Preemptively append cloudstash specific node_modules to PATH
# The cloudstash serverless code will be bindmounted in on the orchestration server
ENV PATH=$PATH:/home/alpine/serverless/node_modules/.bin

# where to put global packages
ENV NPM_CONFIG_PREFIX=/home/alpine/.npm-global
ENV PATH=$PATH:$NPM_CONFIG_PREFIX/bin

COPY cloudstash_package.json /tmp/package.json
COPY . /home/alpine/cloudstash-characterization

RUN \
    # install python, pip, nodejs, npm, bash and aws-cli
    apk add --no-cache bash aws-cli nodejs npm python3 py3-pip && \
    # install artillery npm packages globally
    npm install -g artillery serverless serverless-artillery && \
    # create direcotry to store generated artifacts and reports
    mkdir -p /home/alpine/artifacts && \
    mkdir -p /home/alpine/output && \
    # add a non-root user and group, with specific group and user id 1000:1000
    addgroup -S alpine -g 1000 && \
    adduser -S alpine -G alpine -u 1000 && \
    # cache node_modules for the cloudstash project, to allow to deploy using serverless
    cd /tmp && \
    npm install --log-level=error && \
    mv /tmp/node_modules /home/alpine/node_modules && \
    # make sure that alpine user owns everything in /home/alpine
    chown -R 1000:1000 /home/alpine

USER alpine

WORKDIR /home/alpine/cloudstash-characterization/Benchmark

ENTRYPOINT ["python3", "-u", "orchestrate_benchmark.py"]
CMD ["--help"]
