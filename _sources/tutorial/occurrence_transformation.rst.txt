Delimited to Points
===================

Converting delimited data (tab, comma, or other) to points can be done using
`convert_delimited_to_point <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_transformation.convert_delimited_to_point>`_
You can use column indices or getter methods like 'itemgetter' to get values.

    >>> csv_filename = 'points.csv'
    >>> species_column = 0
    >>> x_column = 1
    >>> y_column = 2
    >>> points = convert_delimited_to_point(csv_filename, species_column, itemgetter(x_column), y_column)

----

JSON to Points
==============

Point data can be extracted from JSON data as well by using dictionary keys or
getter functions.  Combined with an optional iterator function, even
complicated JSON data structures can be processed to extract occurrence point
information.

See: `convert_json_to_point <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_transformation.convert_delimited_to_point>`_

    >>> from operation import itemgetter
    >>> point_data = {
        'title': 'My points',
        'date': 'May 13, 2020',
        'data': [
            {'species': 'Test species', 'x': -30, 'y': 20},
            {'species': 'Test species', 'x': -40, 'y': 21},
            {'species': 'Test species', 'x': -32, 'y': 22},
            {'species': 'Test species', 'x': -28, 'y': 19},
        ]
        }
    >>> points = convert_json_to_point(point_data, itemgetter('species'), itemgetter('x'), itemgetter('y'), point_iterator=itemgetter('data'))

----

Convert Coordinate Systems
==========================
The 'get_coordinate_converter' function returns a function that will convert
the X and Y coordinates of points provided to it from the original coordinate
system to the specified target coordinate system.

See: `get_coordinate_converter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_transformation.get_coordinate_converter>`_.

    >>> points = [
    ...           Point('Test species', -30, 20),
    ...           Point('Test species', -33, 22),
    ...           Point('Test species', -28, 18)]
    >>> converter = get_coordinate_converter(4326, 2815)
    >>> new_points = [converter(pt) for pt in points]
