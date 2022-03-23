FROM conda/miniconda3:latest as lmpy

LABEL maintainer="Specify Systems <github.com/specifysystems>"
LABEL description="A Docker image lmpy tools"

# RUN apt-get update && apt-get install -y .....

RUN conda update -n base -c conda-forge conda && \
    conda install -y -c conda-forge gdal libspatialindex rtree

# RUN conda update -n base -c conda-forge conda && \
#     conda env create -f environment.yml
# SHELL ["conda", "run", "-n", "lmpy", "/bin/bash", "-c"]

# Copy in our library and install
WORKDIR /lmpy
COPY . .
RUN pip install .
