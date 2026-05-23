#!/usr/bin/env bash

# note: it is not required to run this script to build the container,
# it should already be built by GitHub workflows and available via the
# GitHub Container Registry
# However, if you want to build the container locally, then use this
docker build --platform linux/amd64 -t casatools-env .