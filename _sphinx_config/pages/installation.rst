============
Installation
============

`lmpy` can be installed via multiple methods.  Before installation, your environment
must have prerequisite libraries installed.

The required libraries are:
 - gdal
 - libspatialindex

If you install the libraries with `apt` or from source, you can install lmpy via pip.
Alternatively, you can install all of the prerequisites using `conda`.

-----------------------------
Apt Requirements Installation
-----------------------------

.. code-block:: bash

  python -m pip install --upgrade pip
  pip install numpy
  add-apt-repository --yes ppa:ubuntugis/ppa
  apt-get --quiet update
  apt-get install --yes libgdal-dev gdal-bin libspatialindex-dev
  pip install GDAL==`gdal-config --version`
  pip install -r requirements.txt

-------------------------------
Conda Requirements Installation
-------------------------------

.. code-block:: bash

  conda update -n base -c conda-forge conda
  conda env create -f environment.yml
  conda activate lmpy

=================
lmpy Installation
=================

After installing the prerequisites are installed, you can install lmpy using pip.

--------------
Install latest
--------------

.. code-block:: bash

  git clone https://github.com/specifysystems/lmpy.git
  pip install lmpy/

----------------------
Install latest release
----------------------

.. code-block:: bash

  pip install specify-lmpy

====================================================
Alternative: Install and run with a Docker Container
====================================================

You can avoid installing locally and just run `lmpy` using a Docker container.  We distribute containers through DockerHub as well as the GitHub Container Registry.

------------------
Get from DockerHub
------------------

.. code-block:: bash

  docker pull specifyconsortium/specify-lmpy:latest

Then you can run the container interactively and call tools with bash

.. code-block:: bash

  docker run -it specifyconsortium/specify-lmpy:latest bash

----------------------------------
Get from GitHub Container Registry
----------------------------------

.. code-block:: bash

  docker pull ghcr.io/specifysystems/lmpy:latest

Then you can run the container interactively and call tools with bash

.. code-block:: bash

  docker run -it specifysystems/lmpy:latest bash
