# MPoL Examples

This repository hosts self-contained examples demonstrating [MPoL](https://mpol-dev.github.io/MPoL/) functionality. More info on each example can be found in the README.md within each example folder.

This repository is *not* continuously integrated with the rest of the codebase, because the computational demands are too significant. If you do encounter an error, please log it as a [GitHub issue](https://github.com/MPoL-dev/examples/issues).

# Installing and Running the Examples

Each example assumes you have activated a (virtual) python environment to which you've [successfully installed the MPoL package](https://mpol-dev.github.io/MPoL/installation.html), and that your version of python is at least the minimum current version supported by MPoL.

To run an example, `cd` into that subfolder.

The `requirements.txt` file lists the additional python packages necessary for the analysis specific to the example in that folder. You can install them with
```
pip install -r requirements.txt
```

`Snakefile` is a snakemake file setting up the workflow. Within each example directory, you can run 

```
$ snakemake -c 1 all
```
and you should see all scripts execute in order.


# Table of Contents
* [01 - **Intro**: Setup Mock Image and Baselines](01-generate-mock-baselines/README.md) | Generate a mock sky image $I_\nu(l,m)$ and interferometer baselines $(u,v)$ (but not visibilities $\mathcal{V}(u,v)$). These products are used as input for the other examples.
* [02 - **Intro**: Stochastic Gradient Descent](02-sgd/README.md) | A complete end-to-end example using MPoL to image mock data.
* [03 - **Advanced**: Visibility Inference with Pyro](03-AS209-pyro-inference/README.md) | Use MPoL with Pyro to sample parametric visibility plane models.
* [04 - **Advanced**: IM Lup protoplanetary disk](04-IMLup-multi-EB) | Use MPoL to image the ALMA DSHARP observations of the IM Lup protoplanetary disk, taking into account alignment and weight-scaling adjustments for a multi-execution block dataset.

