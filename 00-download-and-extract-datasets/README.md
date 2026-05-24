# Download and extract datasets

In this 'pre-example,' one downloads and extracts the ALMA datasets to a common data format like `.npz` or `.asdf`. This step requires the `casatools` package, which frequently has restrictions on Python versions and installation environments.

To simplify this step for users of the tutorials, we built a Docker container with the software preinstalled. From within this folder, in your terminal, execute the `run.sh` bash script
```
./run.sh
```

This script will
1) download the Docker image
2) execute a series of commands via Snakemake, listed in the `snakefile`
   1) download the several Gb measurement sets from the archive servers (using `wget`)
   2) untar and extract them to a `data` folder
   3) run Python `casatools` to extract the visibilites to a `.npz` format. 

Upon successful completion, you should see a `data` subdirectory with a `IM_Lup_baselines_and_weights.npz` file.

Alternatively, if you already have your own Python environment compatible with casatools, you can install the [relevant packages](../casatools-env/requirements.txt) into that environment and then launch `snakemake -c1 all` directly.