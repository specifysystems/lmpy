"""Module containing common functions for occurrence data wranglers."""
from lmpy import Point


# .............................................................................
def make_list(points):
    """Make sure that 'points' is a list.

    Args:
        points (list or Point): A point or list of points.

    Returns:
        list of Point: A list of Point objects.
    """
    if isinstance(points, Point):
        return [points]
    return points


# .............................................................................
def get_occurrence_filter(pass_condition_func):
    """Function to get a filter from a pass condition function.

    Args:
        pass_condition_func (Method): A function for determining if a Point should be
            filtered.

    Returns:
        Method: A function to filter a list of points.
    """
    # .......................
    def occurrence_filter(points):
        return list(filter(pass_condition_func, points))
    return occurrence_filter


# .............................................................................
def get_occurrence_map(map_func):
    """Function to get a mapper to apply a function to all points.

    Args:
        map_func (Method): A function to apply to all points.

    Returns:
        Method: A function to map the provied function to all points.
    """
    # .......................
    def occurrence_mapper(points):
        return list(map(map_func, make_list(points)))

    return occurrence_mapper
