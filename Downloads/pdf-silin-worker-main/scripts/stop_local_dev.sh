#!/bin/sh
(
    cd docker-compose && \
    cd local && \
    docker compose -f local_dev.yml stop
)