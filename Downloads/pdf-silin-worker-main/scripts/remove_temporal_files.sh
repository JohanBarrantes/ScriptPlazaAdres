#!/bin/sh
(
    cd converter/templates/download_files && \
    yes | sudo rm -r temporal
)