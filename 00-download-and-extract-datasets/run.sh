#!/usr/bin/env bash

docker run --rm --platform linux/amd64 \
  -v "$(pwd)":/workspace \
  ghcr.io/mpol-dev/examples:sha-2cb1a15 \
  snakemake -c1 all