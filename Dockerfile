FROM alpine:3

ENV npm_config_loglevel=silent
ENV PATH=$PATH:/home/alpine/serverless/node_modules/.bin

COPY cloudstash_package.json /tmp/package.json

RUN \
    apk add --no-cache bash aws-cli nodejs npm python3 py3-pip && \
    addgroup -S alpine -g 1000 && \
    adduser -S alpine -G alpine -u 1000 && \
    cd /tmp && \
    npm install --log-level=error \
    && mv /tmp/node_modules /home/alpine/node_modules && \
    chown -R 1000:1000 /home/alpine

USER alpine

COPY . /home/alpine/cloudstash-characterization

WORKDIR /home/alpine/cloudstash-characterization

CMD ["bash"]
