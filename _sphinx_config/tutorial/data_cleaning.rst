=============
Data Cleaning
=============

Cleaning Occurrences
====================

Introduction
------------
One of the first steps in creating
:term:`species distribution models<Species Distribution Model>`, let alone
multi-species analyses, is acquiring and preparing specimen occurrence records.  There
are multiple method for acquiring these raw specimen records such as aggregator
downloads or API calls but once you have the raw data, you need to assemble your entire
dataset, which involves converting records to a common format, grouping, and cleaning.
The lmpy library provides tools for performing these aggregation and cleaning steps to
greatly simplify the process for the user.

Occurrence Data Wrangler Configuration
--------------------------------------
You can either use the Data
`Wrangler Factory <../autoapi/lmpy/data_wrangling/factory/index.html#lmpy.data_wrangling.factory.WranglerFactory>`_
or instantiate occurrence data wrangler classes directly.  We will use the factory for
this example with the configuration below.

  .. code-block:: json

    [
        # Decimal precision
        dict(
            wrangler_type='DecimalPrecisionFilter',
            decimal_places=4
        ),
        # Bounding box
        dict(
            wrangler_type='BoundingBoxFilter',
            min_x=0.0,
            min_y=-90.0,
            max_x=180.0,
            max_y=0.0
        ),
        # Unique localities
        dict(wrangler_type='UniqueLocalitiesFilter')
    ]

Example - Console Script
------------------------
For this example, we will use the raw occurrence data found in the sample data
directory in lmpy at `occurrence/Crocodylus porosus.csv` and the example wrangler
configuration should be written to `./occurrence_wrangler_config.json`.  The cleaned
data will be written to `./clean_data.csv`.

 .. code-block:: bash

    $ wrangle_occurrences "./lmpy/sample_data/occurrence/Crocodylus porosus.csv" \
        ./clean_data.csv \
        ./occurrence_wrangler_config.json


Example - Python
------------------------
For this example, we will use the raw occurrence data found in the sample data
directory in lmpy at `occurrence/Crocodylus porosus.csv` and the example wrangler
configuration.  The cleaned data will be written to `./clean_data.csv`.

 .. code-block:: python

    from lmpy.data_wrangling.factory import WranglerFactory
    from lmpy.point import PointCsvReader, PointCsvWriter

    raw_occurrences_filename = './lmpy/sample_data/occurrence/Crocodylus porosus.csv'
    clean_occurrences_filename = './clean_data.csv'

    wrangler_config = [
        # Decimal precision
        dict(
            wrangler_type='DecimalPrecisionFilter',
            decimal_places=4
        ),
        # Bounding box
        dict(
            wrangler_type='BoundingBoxFilter',
            min_x=0.0,
            min_y=-90.0,
            max_x=180.0,
            max_y=0.0
        ),
        # Unique localities
        dict(wrangler_type='UniqueLocalitiesFilter')
    ]

    factory = WranglerFactory()
    wranglers = factory.get_wranglers(wrangler_config)
    with PointCsvReader(
        raw_occurrences_filename,
        'species_name',
        'x',
        'y'
    ) as reader:
        with PointCsvWriter(
            clean_occurrences_filename, ['species_name', 'x', 'y']
        ) as writer:
            for points in reader:
                for wrangler in wranglers:
                    points = wrangler.wrangle_points(points)
                if len(points) > 0:
                    writer.write_points(points)
