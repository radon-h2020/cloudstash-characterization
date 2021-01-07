FROM node:lts


RUN \
    apt-get update && \
    apt-get install -y python3 python3-dev python3-pip && \
    apt-get clean

COPY . /home/node

WORKDIR /home/node

USER node
