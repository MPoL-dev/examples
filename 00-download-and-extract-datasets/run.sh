#!/usr/bin/env bash

docker run --rm --platform linux/amd64 \
  -v "$(pwd)":/workspace \
  casatools-env \
  snakemake -c1 all