"""Test script to process an iDigBio DWCA into something we can parse."""
import argparse
import io
import zipfile

import defusedxml.ElementTree as ET

from lmpy.point import PointDwcaReader


# DWCA Tag Constants
CORE_TAG = '{http://rs.tdwg.org/dwc/text/}core'
FIELD_TAG = '{http://rs.tdwg.org/dwc/text/}field'
FILES_TAG = '{http://rs.tdwg.org/dwc/text/}files'
ID_TAG = '{http://rs.tdwg.org/dwc/text/}id'
LOCATION_TAG = '{http://rs.tdwg.org/dwc/text/}location'
EXTENSION_TAG = '{http://rs.tdwg.org/dwc/text/}extension'

ROW_TYPE_ATT = 'rowType'
OCCURRENCE_ROW_TYPE = 'http://rs.tdwg.org/dwc/terms/Occurrence'

TERM_TYPE_ATT = 'term'
DELIMITED_TERMS = [
    'http://portal.idigbio.org/terms/flags',
    'http://portal.idigbio.org/terms/recordIds',
]
DELIMITED_BY_ATT = 'delimitedBy'


# .....................................................................................
def process_meta_xml(meta_xml_contents):
    """Process the contents of the meta.xml file.

    Args:
        meta_xml_contents (str): String containing XML metadata information for a DWCA.

    Returns:
        str: The processed metadata XML as a string.
    """
    meta_xml_root = ET.fromstring(meta_xml_contents)
    core_element = meta_xml_root.find(CORE_TAG)

    # If core element is missing (iDigBio) look in extensions
    if core_element is None:
        for extension_el in meta_xml_root.findall(EXTENSION_TAG):
            if (
                core_element is None
                and extension_el.attrib[ROW_TYPE_ATT] == OCCURRENCE_ROW_TYPE
            ):
                core_element = extension_el
                extension_el.tag = CORE_TAG

    # Add attribute for delimited fields
    for field_element in core_element.findall(FIELD_TAG):
        if field_element.attrib[TERM_TYPE_ATT] in DELIMITED_TERMS:
            field_element.attrib[DELIMITED_BY_ATT] = ';'

    return ET.tostring(meta_xml_root)


# .....................................................................................
def process_idb_dwca(in_zipfile, out_zipfile):
    """Process an idigbio zipfile.

    Args:
        in_zipfile (str): File path to an input DWCA zip file.
        out_zipfile (str): File path to write the output DWCA zip file.
    """
    # Open zip files
    dwca_in = zipfile.ZipFile(in_zipfile, mode='r')
    dwca_out = zipfile.ZipFile(out_zipfile, mode='w')

    # Read and prcoess meta.xml
    meta_xml_contents = io.TextIOWrapper(dwca_in.open('meta.xml')).read()
    new_meta_xml_contents = process_meta_xml(meta_xml_contents)
    dwca_out.writestr('meta.xml', new_meta_xml_contents)

    # Read meta.xml
    #   Correct element tag
    #   Add delimiter to fields?

    # Open occurrence.csv
    in_occ = io.TextIOWrapper(dwca_in.open('occurrence.csv'))

    i = 0
    trip_quote = '"' + '""'  # So python doesn't interpret as block comment
    quad_quote = '""' + '""'
    trip_quote_replace = '"' + "'"
    with open('temp_occ.csv', mode='wt') as temp_occ:
        for line in in_occ:
            i += 1
            # Remove double-double-quotes
            mod_line = (
                line.replace(quad_quote, '""')
                .replace(trip_quote, trip_quote_replace)
                .replace('""', "'")
            )

            quote_chunks = mod_line.split('"')
            write_line = ''

            inside = False

            for chunk in quote_chunks:
                if chunk.startswith('[') and chunk.endswith(']'):
                    write_line += (
                        chunk[1:-1].replace(',', ';').replace("'", '').replace(' ', '')
                    )
                elif chunk.startswith('{') and chunk.endswith('}'):  # JSON
                    write_line += '"' + chunk + '"'
                else:
                    # Quoted section
                    if inside:
                        write_line += '"' + chunk + '"'
                    else:
                        write_line += chunk
                inside = not inside

            # Process lists
            # while mod_line.find('"[') >= 0:
            #    pre_idx = mod_line.find('"[')
            #    post_idx = mod_line[pre_idx:].find(']"') + pre_idx

            #    pre_chunk = mod_line[:pre_idx]
            #    list_chunk = mod_line[pre_idx+2:post_idx].replace(',', ';')
            #        .replace("'", '').replace(' ', '')
            #    post_chunk = mod_line[post_idx+2:]

            #    mod_line = pre_chunk + list_chunk + post_chunk

            #    #mod_line = parts_0[0] + parts_1[0].replace(',', ';')
            #        .replace("'", '').replace(' ', '') + ']"'.join(parts_1[1:])

            # Process json sections (geopoints)

            if not write_line.endswith('\n'):
                write_line += '\n'
            temp_occ.write(write_line)

    dwca_out.write('temp_occ.csv', 'occurrence.csv')

    in_occ.close()

    # Close zip files
    dwca_in.close()
    dwca_out.close()


# .....................................................................................
def test_dwca(dwca_filename):
    """Test that a DWCA file can be processed.

    Args:
        dwca_filename (str): The file path of a DarwinCore Archive to test.

    Raises:
        ValueError: Raised if points returned is None.
    """
    with PointDwcaReader(
        dwca_filename, geopoint_term='geoPoint', x_term='lon', y_term='lat'
    ) as reader:
        for points in reader:
            if points is None:
                raise ValueError('Points is None')


# .....................................................................................
def main():
    """Main method for script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dwca', type=str, help='Input DWCA zip file.')
    parser.add_argument('out_dwca', type=str, help='Output processed DWCA zip file.')
    args = parser.parse_args()
    process_idb_dwca(args.in_dwca, args.out_dwca)
    test_dwca(args.out_dwca)


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    main()
