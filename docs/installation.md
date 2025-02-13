# Installation

## Setting up a user environment

As a `pysimdeum` user, it is easiest to install using `pip` as it is available on `PyPI`:

--8<-- "README.md:docs-install-PyPI"

Alternatively, you can install `pysimdeum`  from its repository:

--8<-- "README.md:docs-install-repo"


## Setting up a developer environment

The install instructions are slightly different to create a development environment compared to a user environment:

1. Install mamba with the [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) executable for your operating system.
1. Open the command line (or the "miniforge prompt" in Windows).
1. Create a Python environment: `mamba create -n pysimdeum python=3.11 pip -c conda-forge`
1. Activate the pysimdeum environment: `mamba activate pysimdeum`
1. Install dependencies: `pip install -r requirements.txt .`

--8<-- "README.md:docs-install-dev"