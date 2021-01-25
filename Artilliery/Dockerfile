FROM node:8

ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

USER node
RUN npm i -g artillery

COPY users.csv .
COPY *.yml ./

ENTRYPOINT [ "artillery" ]
CMD [ "run", "script.yml" ]