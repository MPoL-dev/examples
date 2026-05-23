# Download and extract datasets

# Installation and running

In this 'example,' one merely downloads and extracts the ALMA datasets to a common data format like `.npz` or `.asdf`. This step requires the `casatools` package, which frequently has restrictions on Python versions and installation environments.

To simplify this step for users of the tutorials, one can use our Docker container via 
```
./run.sh
```

Depending on the speed of your internet connection, it may take some time to download the several Gb measurement sets from the archive servers.

Upon successful completion, you should see the following items in your directory:

Alternatively, if one already has their own Python environment compatible casatools, one can install the [relevant packages](../casatools-env/requirements.txt) into that environment.