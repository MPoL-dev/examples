# Bayesian Inference Example

This tutorial walks through how one can use MPoL with the probabilistic programming language Pyro to do Bayesian inference with visibility datasets. We show how to use Stochastic Variational Inference (SVI), but Hamiltonian Monte Carlo samplers are also possible.

# Installation and requirements

## Data
Before starting, you should have already run the scripts in the `00` folder to download and extract the AS209 visibilities. Then, you will need to copy the `TODO_DATA.npz` file into this directory in a new `data` folder. For example, from within this 02 folder, run

**TODO**
```shell
$ mkdir data
$ cp ../01-generate-mock-baselines/data/mock_data.npz data/
```

## Required Packages
You can install necessary Python packages into your environment by
```shell
$ pip install -r requirements.txt
```

and then you can run the code by

```shell 
snakemake -c1 all
```

# Description of contents


The "source" of the tutorial is the `pyro.md` file, and the output `.ipynb` file is generated via 

```
jupytext --to ipynb --execute pyro.md
```

However, if you're just following along, you can view the `pyro.ipynb` file directly, since it contains the figure outputs.