# Packaging

* The lmpy library is intended to be installed via pip.
* Build the package using setuptools and the setup.cfg and setup.py files.

## Local edit/develop

* Install dependencies in a virtual environment using python-virtualenv

```commandline
  sudo apt-get install python3-venv
  python3 -m venv venv
  . venv/bin/activate
  pip3 install -r requirements.txt
  pip3 install -r requirements-docs.txt
  pip3 install -r requirements-test.txt
```

## Docker instances

* Build docker instance and run scripts. Run command from the top level directory.
  The `-t` option assigns a name (dlmpy in this case) for later reference.  The final '.'
  parameter indicates that the Dockerfile is in the current directory.

```commandline
docker build -t dlmpy .
```

### Fixme

* these commands create data in container as root, and output data is owned by root.
* explore creating a user in the container, need to sync with the user running the
  container

### Run in container interactive shell

* Run an interactive shell and set up a volume to share from system to container.
  The `-v` option specifies a volume.  The directory before the colon (`"$(pwd)"/data`)
  system indicates a path (`data` directory below the current directory) to map to the
  `/docker_data` directory in the container.  The `-it` option indicates an interactive
  `bash` terminal in the `dlmpy` container.

```commandline
docker run -v "$(pwd)"/host_data:/container_data -it dlmpy bash
```

* All scripts are listed in setup.cfg console_scripts section.  Go to the module listed
  for the script to find expected parameters.

* Start a script.  As a temporary hack, first set PROJ_LIB environment variable.

```commandline
export PROJ_LIB=/usr/local/share/proj
build_grid /docker_data/twenty_grid.shp -20 -20 20 20 1 4326
```

* Test the output in the docker container

```commandline
ogrinfo -al /container_data/test_grid.shp
```

* Exit the container and test the output in the host system directory.

```commandline
ogrinfo -al ./host_data/test_grid.shp
```

### Run in one-shot container, run and exit

* Run with docker run

```commandline
docker run -v "$(pwd)"/host_data:/container_data \
           -e PROJ_LIB=/usr/local/share/proj \
           dlmpy \
           build_grid /container_data/again_grid.shp -20 -20 20 20 1 4326
```

* Test output in local directory

```commandline
ogrinfo -al ./host_data/again_grid.shp
```

## Project tools

### Pre-commit hooks

* Defined in .pre-commit-config.yaml and some supporting files in .github/linters

### Github tools

* Github actions defined in .github/workflows directory
  * .github/workflows/pytest-conda.yml contains setup, test, bragging

* additional pre-commit configuration in .github/linters

### Documentation

* Use sphinx and readthedocs to generate HTML pages from documentation
* with configuration files .readthedocs.yaml and _sphinx_config/conf.py

### Tests

* Run tests at command line

```commandline
pytest --cov
```
