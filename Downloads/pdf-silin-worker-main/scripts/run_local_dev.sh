#!/bin/sh
(
    cd docker-compose && \
    cd local && \
    docker compose -f local_dev.yml up --build -d && \
    docker compose -f local_dev.yml logs -f
)