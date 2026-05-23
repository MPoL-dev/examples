# Docker image with casatools

This folder contains the instructions and Dockerfile for how to build a Docker container that will run `casatools`, necessary for the `00-download-and-extract-datasets` example. In the normal course of events, this container is built automatically as part of the GitHub Actions workflow, and you can download it from the GitHub Container Registry following the instructions in the [00 example](../00-download-and-extract-datasets/README.md).

The following instructions are aimed at developers of the examples. It is assumed that you have already installed a [Docker environment](https://www.docker.com/), e.g., such as Docker Desktop.

Building the container locally, from within this directory, and tag as `casatools-env`
```
docker build --platform linux/amd64 -t casatools-env .
```
Note that the `--platform linux/amd64` is necessary to accommodate the modular casa packages, which to my understanding are not built for Apple Silicon architecture.

Run the container and enter a bash shell
```
docker run --rm -it --platform linux/amd64 casatools-env
```