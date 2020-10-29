"""Module containing wrangler factory tools."""
import requests
import urllib

from lmpy import Point
from lmpy.data_wrangling.occurrence.filters import (
    get_attribute_filter, get_bounding_box_filter,
    get_decimal_precision_filter, get_disjoint_geometries_filter,
    get_intersect_geometries_filter, get_minimum_points_filter,
    get_spatial_index_filter, get_unique_localities_filter)
from lmpy.data_wrangling.occurrence.modifiers import (
    get_accepted_name_modifier, get_attribute_modifier,
    get_common_format_modifier, get_coordinate_converter_modifier)
from lmpy.spatial import SpatialIndex


# .............................................................................
class WRANGLER_TYPES:
    # Filters
    ATTRIBUTE_FILTER = 'attribute_filter'
    BBOX_FILTER = 'bbox_filter'
    DECIMAL_PRECISION_FILTER = 'decimal_precision_filter'
    MINIMUM_POINTS_FILTER = 'minimum_points_filter'
    SPATIAL_INDEX_FILTER = 'spatial_index_filter'
    UNIQUE_LOCALITIES_FILTER = 'unique_localities_filter'
    # Modifiers
    ACCEPTED_NAME_MODIFIER = 'accepted_name_modifier'
    ATTRIBUTE_MAP_MODIFIER = 'attribute_map_modifier'


# .............................................................................
def wrangler_factory(wrangler_config):
    """Get an occurrence data wrangler from the wrangler configuration.

    Args:
        wrangler_config (dict): A dictionary of wrangler configuration
            parameters.

    Return:
        An occurrence data wrangler.
    """
    wrangler_type = wrangler_config['wrangler_type'].lower()
    if wrangler_type == WRANGLER_TYPES.ATTRIBUTE_FILTER:
        att_name = wrangler_config['attribute_name']
        list_delimiter = wrangler_config['field_delimiter']
        bad_values = wrangler_config['condition']['all']['not_in']

        # Not in list
        def all_not_in(value):  # pragma: no cover
            field_values = value.split(list_delimiter)
            return all(
                [val.strip(']').strip('[').strip(
                    '"') not in bad_values for val in field_values])

        return get_attribute_filter(att_name, all_not_in)
    if wrangler_type == WRANGLER_TYPES.DECIMAL_PRECISION_FILTER:
        return get_decimal_precision_filter(
            int(wrangler_config['decimal_precision']))
    if wrangler_type == WRANGLER_TYPES.UNIQUE_LOCALITIES_FILTER:
        return get_unique_localities_filter()
    if wrangler_type == WRANGLER_TYPES.BBOX_FILTER:
        min_x = float(wrangler_config['min_x'])
        min_y = float(wrangler_config['min_y'])
        max_x = float(wrangler_config['max_x'])
        max_y = float(wrangler_config['max_y'])
        return get_bounding_box_filter(min_x, min_y, max_x, max_y)
    if wrangler_type == WRANGLER_TYPES.MINIMUM_POINTS_FILTER:
        return get_minimum_points_filter(
            int(wrangler_config['minimum_points']))
    if wrangler_type == WRANGLER_TYPES.SPATIAL_INDEX_FILTER:
        spatial_index = SpatialIndex(wrangler_config['index_file'])

        def check_hit_func(hit, check_vals):  # pragma: no cover
            for check_key, check_val in check_vals:
                if check_key in hit:
                    if hit[check_key] == check_val:
                        return True
            return False

        def get_valid_intersections_func(species_name):  # pragma: no cover
            ret_vals = []
            if species_name in wrangler_config['species']:
                for level, value in wrangler_config['species'][species_name]:
                    level_key = 'Level_{}_cod'.format(level)
                    if int(level) < 4:
                        level_key = level_key.upper()
                    ret_vals.append((level_key, value))
            return ret_vals

        return get_spatial_index_filter(
            spatial_index, get_valid_intersections_func, check_hit_func)
    if wrangler_type == WRANGLER_TYPES.ATTRIBUTE_MAP_MODIFIER:
        mapping = wrangler_config['attribute_mapping']
        return get_common_format_modifier(mapping)
    if wrangler_type == WRANGLER_TYPES.ACCEPTED_NAME_MODIFIER:
        return get_accepted_name_modifier(wrangler_config['filename'])
