=============
Data Cleaning
=============

Introduction
============
One of the first steps in creating species distribution models, let alone multi-species
analyses, is acquiring and preparing specimen occurrence records.  There are multiple
method for acquiring these raw specimen records such as aggregator downloads or API
calls but once you have the raw data, you need to assemble your entire dataset, which
involves converting records to a common format, grouping, and cleaning.  The lmpy
library provides tools for performing these aggregation and cleaning steps to greatly
simplify the process for the user.


Reading a CSV File
==================
Read a CSV file that has fields "decimalLongitude" and "decimalLatitude" for x and y
and "speciesName" for the species binomial.

See: `PointCsvReader <../autoapi/lmpy/point/index.html#lmpy.point.PointCsvReader>`_

    >>> reader = PointCsvReader(csv_filename, 'speciesName', 'decimalLongitude', 'decimalLatitude')


Reading a Darwin Core Archive File
==================================
Read a Darwin Core Archive file.  The file is assumed to be valid and metadata will
be pulled from the 'meta.xml' file contained within the zip file.

See: `PointDwcaReader <../autoapi/lmpy/point/index.html#lmpy.point.PointDwcaReader>`_

    >>> reader = PointDwcaReader(dwca_filename)


Filtering Records
=================

Built-in Filters
----------------
Filter a list of Point objects so that those with less than four (4) decimal places
of precision are removed.

    >>> points = [Point('Species A', 10.3, 23.1),
    ...    Point('Species B', 11.34123, 12.2314),
    ...    Point('Species C', 13.23131, 18.3123)]
    >>> precision_filter = get_decimal_precision_filter(4)
    >>> flt_points = precision_filter(points)
    >>> print(flt_points)
    [Point('Species B', 11.34123, 12.2314), Point('Species C', 13.23131, 18.3123)]


Custom Filters
--------------
Filter a list of points so that those without a species epithet are removed.

    >>> def genus_filter_func(point):
    ...     return len(point.split(' ')) > 1
    >>> genus_filter = get_occurrence_filter(genus_filter_func)
    >>> points = [Point('Species A', 1, 2),
    ...     Point('Genus', 3, 4), Point('Genus', 9, 3), Point('Species B', 2, 1)]
    >>> flt_points = genus_filter(points)
    >>> print(flt_points)
    [Point('Species A', 1, 2), Point('Species B', 2, 1)]


Modifying Records
=================

Built-in Modifiers
------------------
Use the accepted name modifier with a file, ACCEPTED_TAXA_FILENAME, containing accepted
name mappings.

    >>> accepted_name_modifier = get_accepted_name_modifier(ACCEPTED_TAXA_FILENAME)
    >>> points = [Point('Accepted species', 1, 2),
    ...     Point('Synonym species', 5, 3), Point('Another synonym', 4, 4)]
    >>> mod_points = accepted_name_modifier(points)
    >>> print(mod_points)
    [Point('Accepted species', 1, 2), Point('Accepted species', 5, 3),
    Point('Accepted species', 4, 4)]


Putting It All Together
=======================

Aggregate and Clean Multiple Data Files
---------------------------------------
For this example, we will process occurrence data from three sources, a Darwin Core
Archive, a JSON file, and a CSV file.  The Darwin Core Archive file is at
DWCA_FILENAME, the JSON data is at JSON_FILENAME and the records are under the 'items'
key with 'scientificName' as the species key and 'lon' and 'lat' as the x and y keys
under the 'geopoint' key.  For the CSV file, CSV_FILENAME, the fields are 'taxonName',
'decimalLongitude', and 'decimalLatitude' for the species, x, and y fields
respectively.

First, define a modifier function that will ensure points from each source are in the
same format and only include species name, x, and y.  We can do this by only keeping
the attributes 'species_name', 'x', and 'y'.  We will also send the points through an
accepted name modifier, with a mapping file at ACCEPTED_NAMES_FILENAME, to ensure that
the species name for each point is an accepted name.  We will define a chained modifier
function that we will utilize to apply both the accepted name modifier and the common
format modifier.  It is defined in the 'get_chained_modifier' function.

    >>> accepted_name_modifier = get_accepted_name_modifier(ACCEPTED_NAMES_FILENAME)
    >>> def common_format_modifier(points):
    ...     return [Point(pt.species_name, pt.x, pt.y) for pt in points]
    >>> def get_chained_modifier(*modifiers):
    ...     def chained_modifier(points):
    ...         for modifier in list(modifiers):
    ...             points = modifier(points)
    ...         return points
    ...     return chained_modifier
    >>> chained_modifier = get_chained_modifier(
    ...     accepted_name_modifier,
    ...     common_format_modifier
    ... )
    >>> all_points = []
    >>> # Process the Darwin Core Archive
    >>> with PointDwcaReader(DWCA_FILENAME) as dwca_reader:
    ...     for points in dwca_reader:
    ...         all_points.extend(chained_modifier(points))
    >>> # Process the JSON file
    >>> with open(JSON_FILENAME) as in_file:
    ...     json_point_data = json.load(in_file)
    >>> raw_json_points = []
    >>> for item in json_point_data['items']:
    ...     raw_json_points.append(
    ...         Point(
    ...             item['scientificName'],
    ...             item['geopoint']['lon'],
    ...             item['geopoint']['lat']
    ...         )
    ...     )
    >>> # For consistency, common format json points
    >>> all_points.extend(chained_modifier(raw_json_points))
    >>> # Process the CSV file
    >>> with PointCsvReader(
    ...     CSV_FILENAME,
    ...     'taxonName',
    ...     'decimalLongitude',
    ...     'decimalLatitude'
    ... ) as csv_reader:
    ...     for points in csv_reader:
    ...         all_points.extend(chained_modifier(points))

In this example, we assume that there are a reasonable number of points that can be
sorted at once.  For large datasets, it may be necessary to split the data first
before attempting to sort.  We will sort the points and write to a temporary file
because, when we read them from it, each group will contain all of the points for a
single species.

    >>> # Sort points and write to a temporary file
    >>> temp_filename = tempfile.NamedTemporaryFile(suffix='.csv', delete=True).name
    >>> with PointCsvWriter(temp_filename, 'species_name', 'x', 'y') as csv_writer:
    ...     for points in sorted(all_points):
    ...         csv_writer.write_points(points)

Now we have an aggregated CSV file containing all of the specimen records from each of
the three sources that is grouped and sorted by species name.  Next, we will filter
the specimen records so that we only keep those with at least four decimal places of
precision, only unique localities, and only keep species with at least 12 points.
Write the cleaned data points to OUTPUT_POINTS_FILENAME.

    >>> # Set up filters (except for duplicate localities)
    >>> chain_filters = [
    ...     get_decimal_precision_filter(4),
    ...     get_minimum_points_filter(12),
    ... ]
    >>> with PointCsvWriter(
    ...     OUTPUT_POINTS_FILENAME,
    ...     ['species_name, 'x', 'y']
    ... ) as csv_writer:
    ...     with PointCsvReader(temp_filename, 'species_name', 'x', 'y') as csv_reader:
    ...         for points in csv_reader:
    ...             dup_filter = get_unique_localities_filter()
    ...             points = dup_filter(points)
    ...             for flt in chain_filters:
    ...                 if points:  # Stop trying to filter if there are no points
    ...                     points = flt(points)
    ...             dup_filter = None  # Reset to preserve memory
    ...             if points:  # If any points remain, write them
    ...                 csv_writer.write_points(points)

That's it!  We have processed data from three sources, ensured that all records
have an accepted taxon name, filtered out records that have low coordinate decimal
precision, identified taxa with a minimum number of unique localities, to be able to use all of the resulting
data for computing species distribution models.
