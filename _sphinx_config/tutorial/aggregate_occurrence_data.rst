===========================
Aggregating Occurrence Data
===========================

Introduction
============
Performing large-scale analyses often requires using data from multiple sources.
However, the data coming from multiple sources is often in different formats.  We
provide tools for aggregating these heterogeneous occurrence datasets so that they can
be used in combination for analysis.  We can use data wranglers to perform specific
data manipulations and / or filtering on data from each source before then converting
the data into a common format.

Data Formats
============
The two primary formats supported by lmpy are text-delimited data and Darwin Core
Archives.  It is possible to use other data formats if needed but we will focus on CSV
and Darwin Core Archive.
`Submit a Feature Request <https://github.com/specifysystems/lmpy/issues/new?assignees=&labels=&template=feature_request.md&title=>`_
if you need help with another format.  Data from `GBIF <https://www.gbif.org/>`_,
`iDigBio <https://www.idigbio.org/>`_, `ALA <https://www.ala.org.au/>`_ and others is
supported.

Wrangling Data For Aggregation
==============================
You will need to perform some manipulations on each dataset individually before they
can be aggregated together.  Do this by specifying a set of occurrence data wranglers
for each dataset.  A common use-case is to resolve the taxonomy of a dataset, perform
any provider-specific actions, like filtering points flagged by the provider as
invalid, and then convert the data into a common format.

Example wrangler configuration

  .. code-block:: json

    [
        {
            "wrangler_type": "AcceptedNameOccurrenceWrangler",
            "name_resolver": "gbif",
            "out_map_filename": "name_map.json",
        },
        {
            "wrangler_type": "CommonFormatWrangler",
            "attribute_map": {
                "taxonname": "species_name",
                "decimallongitude": "x",
                "decimallatitude": "y",
            }
        }
    ]


Example - Console Scripts
=========================
This example shows how data from three files, a GBIF DWCA file, an iDigBio DWCA file,
and an ALA CSV file, can be combined and split into one CSV file per species in the
data.  See `split_occurrence_data <../scripts/split_occurrence_data>`_ for usage
documentation.

GBIF DWCA File
--------------
The wrangling steps for GBIF data will be to resolve taxon names, filter records GBIF
has flagged as having spatial or taxonomic issues, add a field indicating that the
record comes from GBIF, and then convert to a common format.

  .. code-block:: json

    [
        {
            "wrangler_type": "AcceptedNameOccurrenceWrangler",
            "name_map": "species_name_map.json"
        },
        {
            "wrangler_type": "AttributeFilterWrangler",
            "attribute_name": "issue",
            "filter_func": {
                "for-each": {
                    "condition": "not-in",
                    "values": [
                        "TAXON_MATCH_FUZZY",
                        "TAXON_MATCH_HIGHERRANK",
                        "TAXON_MATCH_NONE"
                    ]
                }
            }
        },
        {
            "wrangler_type": "AttributeModifierWrangler",
            "attribute_name": "data_source",
            "attribute_func": {
                "constant": "gbif"
            }
        },
        {
            "wrangler_type": "CommonFormatWrangler",
            "attribute_map": {
                "species_name": "species_name",
                "x": "x",
                "y": "y",
                "data_source": "data_source"
            }
        }
    ]


iDigBio DWCA File
-----------------
The wrangling steps for iDigBio data will be to resolve taxon names, filter records
iDigBio has flagged as having spatial or taxonomic issues, add a field indicating that
the record comes from iDigBio, and then convert to a common format.


  .. code-block:: json

    [
        {
            "wrangler_type": "AcceptedNameOccurrenceWrangler",
            "name_map": "species_name_map.json"
        },
        {
            "wrangler_type": "AttributeFilterWrangler",
            "attribute_name": "flags",
            "filter_func": {
                "for-each": {
                    "condition": "not-in",
                    "values": [
                        "geopoint_datum_missing",
                        "geopoint_bounds",
                        "geopoint_datum_error",
                        "geopoint_similar_coord",
                        "rev_geocode_mismatch",
                        "rev_geocode_failure",
                        "geopoint_0_coord",
                        "taxon_match_failed",
                        "dwc_kingdom_suspect",
                        "dwc_taxonrank_invalid",
                        "dwc_taxonrank_removed"                    ]
                }
            }
        },
        {
            "wrangler_type": "AttributeModifierWrangler",
            "attribute_name": "data_source",
            "attribute_func": {
                "constant": "idigbio"
            }
        },
        {
            "wrangler_type": "CommonFormatWrangler",
            "attribute_map": {
                "species_name": "species_name",
                "x": "x",
                "y": "y",
                "data_source": "data_source"
            }
        }
    ]


ALA CSV file
------------
The wrangling steps for ALA data will be to resolve taxon names, add a field indicating
that the record comes from ALA, and then convert to a common format.

  .. code-block:: json

    [
        {
            "wrangler_type": "AcceptedNameOccurrenceWrangler",
            "name_map": "species_name_map.json"
        },
        {
            "wrangler_type": "AttributeModifierWrangler",
            "attribute_name": "data_source",
            "attribute_func": {
                "constant": "idigbio"
            }
        },
        {
            "wrangler_type": "CommonFormatWrangler",
            "attribute_map": {
                "species_name": "species_name",
                "x": "x",
                "y": "y",
                "data_source": "data_source"
            }
        }
    ]


Example - Console Script
------------------------
For this example, we will use the data and example data wranglers as inputs and we will
write the output datasets to the `./species_info/` directory and write out a species
list of the species seen while processing the data.

 .. code-block:: bash

  $ split_occurrence_data \
        --species_list_filename=./seen_species.txt \
        --dwca sample_data/gbif.zip gbif_wrangler_config.json \
        --dwca sample_data/idigbio.zip idigbio_wrangler_config.json \
        --csv sample_data/ala.csv ala_wrangler_config.json scientificName decimalLongitude decimalLatitude \
        ./species_info/


Example - Python
------------------------
For this example, we will use the data and example data wranglers as inputs and we will
write the output datasets to the `./species_info/` directory and write out a species
list of the species seen while processing the data.

 .. code-block:: python

  import os
  from lmpy.data_preparation.occurrence_splitter import (
      get_writer_key_from_fields_func,
      get_writer_filename_func,
      OccurrenceSplitter,
  )
  from lmpy.data_wrangling.factory import WranglerFactory
  from lmpy.point import PointCsvReader, PointDwcaReader

  sample_data_dir = './sample_data/'
  gbif_dwca_filename = os.path.join(sample_data_dir, 'occurrence/gbif.zip')
  idigbio_dwca_filename = os.path.join(sample_data_dir, 'occurrence/idigbio.zip')
  ala_csv_filename = os.path.join(sample_data_dir, 'occurrence/ala.csv')

  species_list_filename = './seen_species.txt'
  key_field = ['species_name']
  out_dir = './species_info/'
  # Wrangler configuration dictionaries
  gbif_wrangler_conf = [
      {
          "wrangler_type": "AcceptedNameOccurrenceWrangler",
          "name_resolver": "gbif",
          "out_map_filename": "name_map.json",
      },
      {
          "wrangler_type": "CommonFormatWrangler",
          "attribute_map": {
              "taxonname": "species_name",
              "decimallongitude": "x",
              "decimallatitude": "y",
          }
      }
  ]

  idigbio_wrangler_conf = [
      {
          "wrangler_type": "AcceptedNameOccurrenceWrangler",
          "name_map": "species_name_map.json"
      },
      {
          "wrangler_type": "AttributeFilterWrangler",
          "attribute_name": "flags",
          "filter_func": {
              "for-each": {
                  "not-in": [
                      "geopoint_datum_missing",
                      "geopoint_bounds",
                      "geopoint_datum_error",
                      "geopoint_similar_coord",
                      "rev_geocode_mismatch",
                      "rev_geocode_failure",
                      "geopoint_0_coord",
                      "taxon_match_failed",
                      "dwc_kingdom_suspect",
                      "dwc_taxonrank_invalid",
                      "dwc_taxonrank_removed"                    ]
              }
          }
      },
      {
          "wrangler_type": "AttributeModifierWrangler",
          "attribute_name": "data_source",
          "attribute_func": {
              "constant": "idigbio"
          }
      },
      {
          "wrangler_type": "CommonFormatWrangler",
          "attribute_map": {
              "species_name": "species_name",
              "x": "x",
              "y": "y",
              "data_source": "data_source"
          }
      }
  ]

  ala_wrangler_conf = [
      {
          "wrangler_type": "AcceptedNameOccurrenceWrangler",
          "name_map": "species_name_map.json"
      },
      {
          "wrangler_type": "AttributeModifierWrangler",
          "attribute_name": "data_source",
          "attribute_func": {
              "constant": "idigbio"
          }
      },
      {
          "wrangler_type": "CommonFormatWrangler",
          "attribute_map": {
              "species_name": "species_name",
              "x": "x",
              "y": "y",
              "data_source": "data_source"
          }
      }
  ]

  # Establish functions for getting writer key and filename
  writer_key_func = get_writer_key_from_fields_func(*tuple(key_field))
  writer_filename_func = get_writer_filename_func(out_dir)

  factory = WranglerFactory()
  readers_and_wranglers = [
      (PointDwcaReader(gbif_dwca_filename), factory.get_wranglers(gbif_wrangler_conf)),
      (
          PointDwcaReader(idigbio_dwca_filename),
          factory.get_wranglers(idigbio_wrangler_conf)
      ),
      (
          PointCsvReader(
              ala_csv_filename,
              'scientificName',
              'decimalLongitude',
              'decimalLatitude'
          ),
          factory.get_wranglers(ala_wrangler_conf))
  ]
  write_fields = ['species_name', 'x', 'y', 'data_source']

  # Initialize processor
  with OccurrenceSplitter(
      writer_key_func,
      writer_filename_func,
      write_fields=write_fields,
  ) as occurrence_processor:
      for reader, wranglers in readers_and_wranglers:
          occurrence_processor.process_reader(reader, wranglers)
      occurrence_processor.write_species_list(species_list_filename)
