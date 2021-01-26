FROM alpine:3

RUN \
    apk add --no-cache bash nodejs npm python3 py3-pip && \
    npm install -g serverless serverless-python-requirements && \
    addgroup -S alpine && adduser -S alpine -G alpine

USER alpine

COPY . /home/alpine/cloudstash-characterization

WORKDIR /home/alpine/cloudstash-characterization

CMD ["bash"]
