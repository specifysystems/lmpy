"""Module containing wrangler factory tools."""
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
    """Constants class for occurrence data wrangler types."""
    # Filters
    ATTRIBUTE_FILTER = 'attribute_filter'
    BBOX_FILTER = 'bbox_filter'
    DECIMAL_PRECISION_FILTER = 'decimal_precision_filter'
    DISJOINT_GEOMETRIES_FILTER = 'disjoint_geometries_filter'
    INTERSECT_GEOMETRIES_FILTER = 'intersect_geometries_filter'
    MINIMUM_POINTS_FILTER = 'minimum_points_filter'
    SPATIAL_INDEX_FILTER = 'spatial_index_filter'
    UNIQUE_LOCALITIES_FILTER = 'unique_localities_filter'
    # Modifiers
    ACCEPTED_NAME_MODIFIER = 'accepted_name_modifier'
    ATTRIBUTE_MODIFIER = 'attribute_modifier'
    ATTRIBUTE_MAP_MODIFIER = 'attribute_map_modifier'
    CORDINATE_CONVERTER_MODIFIER = 'coordinate_converter_modifier'


# .............................................................................
def wrangler_factory(wrangler_config):
    """Get an occurrence data wrangler from the wrangler configuration.

    Args:
        wrangler_config (dict): A dictionary of wrangler configuration parameters.

    Returns:
        Method: An occurrence data wrangler.
    """
    wrangler_type = wrangler_config['wrangler_type'].lower()
    occurrence_wrangler = None
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

        occurrence_wrangler = get_attribute_filter(att_name, all_not_in)
    elif wrangler_type == WRANGLER_TYPES.DECIMAL_PRECISION_FILTER:
        occurrence_wrangler = get_decimal_precision_filter(
            int(wrangler_config['decimal_precision']))
    elif wrangler_type == WRANGLER_TYPES.DISJOINT_GEOMETRIES_FILTER:
        # Get geometries (wkts)
        wkts = wrangler_config['geometry_wkts']
        occurrence_wrangler = get_disjoint_geometries_filter(wkts)
    elif wrangler_type == WRANGLER_TYPES.INTERSECT_GEOMETRIES_FILTER:
        wkts = wrangler_config['geometry_wkts']
        occurrence_wrangler = get_intersect_geometries_filter(wkts)
    elif wrangler_type == WRANGLER_TYPES.UNIQUE_LOCALITIES_FILTER:
        occurrence_wrangler = get_unique_localities_filter()
    elif wrangler_type == WRANGLER_TYPES.BBOX_FILTER:
        min_x = float(wrangler_config['min_x'])
        min_y = float(wrangler_config['min_y'])
        max_x = float(wrangler_config['max_x'])
        max_y = float(wrangler_config['max_y'])
        occurrence_wrangler = get_bounding_box_filter(
            min_x, min_y, max_x, max_y)
    elif wrangler_type == WRANGLER_TYPES.MINIMUM_POINTS_FILTER:
        occurrence_wrangler = get_minimum_points_filter(
            int(wrangler_config['minimum_points']))
    elif wrangler_type == WRANGLER_TYPES.SPATIAL_INDEX_FILTER:
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

        occurrence_wrangler = get_spatial_index_filter(
            spatial_index, get_valid_intersections_func, check_hit_func)
    elif wrangler_type == WRANGLER_TYPES.ATTRIBUTE_MODIFIER:
        att_name = wrangler_config['attribute_name']
        map_dict = wrangler_config['map_values']

        def replace_func(in_value):  # pragma: no cover
            if in_value in map_dict:
                return map_dict[in_value]
            return None

        occurrence_wrangler = get_attribute_modifier(att_name, replace_func)
    elif wrangler_type == WRANGLER_TYPES.ATTRIBUTE_MAP_MODIFIER:
        mapping = wrangler_config['attribute_mapping']
        occurrence_wrangler = get_common_format_modifier(mapping)
    elif wrangler_type == WRANGLER_TYPES.ACCEPTED_NAME_MODIFIER:
        occurrence_wrangler = get_accepted_name_modifier(
            wrangler_config['filename'])
    elif wrangler_type == WRANGLER_TYPES.CORDINATE_CONVERTER_MODIFIER:
        in_epsg = wrangler_config['in_epsg']
        out_epsg = wrangler_config['out_epsg']
        occurrence_wrangler = get_coordinate_converter_modifier(
            in_epsg, out_epsg)
    return occurrence_wrangler
