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
    get_attribute_modifier, get_common_format_modifier,
    get_coordinate_converter_modifier)
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
        def all_not_in(value):
            field_values = value.split(list_delimiter)
            return all([val.strip(']').strip('[').strip('"') not in bad_values for val in field_values])
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
        return get_bbox_filter(min_x, min_y, max_x, max_y)
    if wrangler_type == WRANGLER_TYPES.MINIMUM_POINTS_FILTER:
        return get_minimum_points_filter(
            int(wrangler_config['minimum_points']))
    if wrangler_type == WRANGLER_TYPES.SPATIAL_INDEX_FILTER:
        spatial_index = SpatialIndex(wrangler_config['index_file'])
        def check_hit_func(hit, check_vals):
           for check_key, check_val in check_vals:
               if check_key in hit:
                  if hit[check_key] == check_val:
                      return True
           return False
        def get_valid_intersections_func(species_name):
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
        return get_accepted_name_wrangler(wrangler_config['filename'])

# TODO: Move this
# .............................................................................
def get_accepted_name_wrangler(accepted_taxa_filename):
    """Get a data wrangler for populating accepted taxon name for points."""
    accepted_map = {}
    with open(accepted_taxa_filename, 'r') as in_file:
        _ = next(in_file)
        for line in in_file:
            parts = line.split(',')
            accepted_map[parts[0]] = parts[1]

    # .......................
    def accepted_taxon_wrangler(points):
        return_points = []
        if isinstance(points, Point):
            points = [points]
        for point in points:
            check_sp = point.species_name
            # Check if we don't have an entry for this name
            if check_sp not in accepted_map.keys():
                # We don't have it, go get it!
                # new_name = get_gbif_accepted_name(check_sp)
                # print('New name: {}'.format(new_name))
                # We don't have it, it doesn't exist
                new_name = ''
                accepted_map[check_sp] = new_name
                # print('{},{},,'.format(check_sp, new_name))
            accepted_taxon_name = accepted_map[check_sp]
            if accepted_taxon_name is None or len(accepted_taxon_name) < 2:
                # print('No accepted name for {}'.format(check_sp))
                pass
            else:
                point.species_name = accepted_taxon_name
                return_points.append(point)
        return return_points
    return accepted_taxon_wrangler

# .............................................................................
def get_gbif_accepted_name(name_str):
    """Get the accepted name for a name string.

    Note:
        If there is an HTTP error, I want it to fail out
    """
    other_filters = {'name': name_str.strip()}
    url = 'http://api.gbif.org/v1/species/match?{}'.format(
        urllib.parse.urlencode(other_filters))
    response = requests.get(url).json()
    try:
        if response['status'].lower() in ('accepted', 'synonym') and \
                'speciesKey' in response.keys():
            return response['canonicalName']
    except KeyError:
        pass
    return ''


