# casatools-env/Dockerfile
# need to force the platform here so that casatools is available for the right
# architecture. Doesn't work with Apple Silicon.
FROM --platform=linux/amd64 ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install core system dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip-whl \
    gfortran \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN python3.12 -m venv /opt/casa_venv

# Add the virtual environment binaries to the container path
# This automatically "activates" the venv
ENV PATH="/opt/casa_venv/bin:$PATH"

# Upgrade pip inside the virtual environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install requirements
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# create casa data directory
# https://casadocs.readthedocs.io/en/stable/notebooks/external-data.html
RUN mkdir -p /root/.casa/data

COPY casasiteconfig.py /workspace/casasiteconfig.py
ENV CASASITECONFIG="/workspace/casasiteconfig.py"

# Trigger the initial measures data download inside the container build, 
# so that this isn't redone each time the user runs the container
# https://casadocs.readthedocs.io/en/stable/api/casaconfig.html#casasiteconfig-py
RUN python3 -c "from casaconfig import pull_data; pull_data('/root/.casa/data')"