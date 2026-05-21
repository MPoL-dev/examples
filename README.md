# MPoL Examples

This repository hosts self-contained examples demonstrating [MPoL](https://mpol-dev.github.io/MPoL/) functionality. More info on each example can be found in the README.md within each example folder. This repository is *not* continuously integrated with the rest of the codebase because the computational demands are too significant. If you do encounter an error, please log it as a [GitHub issue](https://github.com/MPoL-dev/examples/issues).

# Installing and running the examples 

These examples strive to use real, or approximately real, data to demonstrate MPoL functionality. Unfortunately, using real ALMA data means that we must contend with the fact that the Python `casatools` package frequently lags supported [SPEC 0](https://scientific-python.org/specs/spec-0000/) Python versions. This creates a situation where one needs both a deprecated Python version old enough to run `casatools` and a current Python version new enough to support modern development.

## The initial 00 example
We've isolated the `casatools` dependency to the initial dataset download and extraction in the `00-download-and-extract-datasets` example. In that folder, you will need to install `casatools` into an older Python version that still supports it (e.g., 3.10). ([More Info](./00-download-and-extract-datasets/README.md))

## All other examples
Once you have completed the 00 example and extracted the ALMA datasets to either `.npz` or `.asdf` formats, you can then copy these data products into the `01-...` or `02-...` example folders that require them. In those later example folders, it is assumed that you have activated a (virtual) python environment to which you've [successfully installed the MPoL package](https://mpol-dev.github.io/MPoL/installation.html), and that your version of python is at least the minimum current version supported by MPoL.

Each folder will have a `requirements.txt` file that lists the additional python packages necessary for the analysis specific to the example in that folder. You can install them with
```
pip install -r requirements.txt
```

`Snakefile` is a snakemake file setting up the workflow. Within each example directory, you can run 

```
$ snakemake -c 1 all
```
and you should see all scripts execute in order.

# List of Examples
* [00 - **Setup**: Download and Extract Datasets](00-download-and-extract-datasets/README.md) | Download a few calibrated ALMA measurement sets and use `casatools` and `visread` to extract the visibilities to a common format like `.npz` or `.asdf`.
* [01 - **Intro**: Setup Mock Image and Baselines](01-generate-mock-baselines/README.md) | Generate a mock sky image $I_\nu(l,m)$ and interferometer baselines $(u,v)$ (but not the visibilities). These products are used as input for the other examples.
* [02 - **Intro**: Stochastic Gradient Descent](02-sgd/README.md) | A complete end-to-end example using MPoL to image mock data.
* [03 - **Advanced**: Visibility Inference with Pyro](03-AS209-pyro-inference/README.md) | Use MPoL with Pyro to sample parametric visibility plane models.
* [04 - **Advanced**: IM Lup protoplanetary disk](04-IMLup-multi-EB) | Use MPoL to image the ALMA DSHARP observations of the IM Lup protoplanetary disk, taking into account alignment and weight-scaling adjustments for a multi-execution block dataset.