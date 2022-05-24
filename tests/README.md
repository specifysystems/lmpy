# Tests

All tests may be run at the top directory level with

```commandline
pytest tests/ -v --cov lmpy --cov-report term-missing
```

## Github hook

Github action PyTest with Conda configured with .github/workflows/pyconda-test.yml

## Handy tools

Functions in the tests/data_simulator.py module allow simple on-the-fly data
construction for a variety of testing applications.

## Some of our test fixtures

### generate_temp_filename

The `generate_temp_filename` test fixture provides functionality for generating
temporary filenames that can be used in testing and then will be automatically
deleted once the test completes.

### script_runner

The `script_runner` test fixture is used to call a script from the command line using
`subprocess.run`.  This fixture takes the name of a console script as well as the
module path for that script and runs the appropriate call at runtime.  Setting the
environment variable, `SCRIPT_FAIL_IF_MISSING=1` will cause the fixture to fail if the
specified console script does not exist.
