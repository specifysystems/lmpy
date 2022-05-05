# Occurrence Data Wranglers

The files in this module define tree data manipulations, and parameters for each, that can be configured 
for various purposes. 

* A configuration file is in JSON format, a list of one dictionary per desired wrangler.  
  * Each dictionary must contain "wrangler_type", with the name of the wrangler types (listed below).  
  * The dictionary will also contain all required parameters and any optional parameters.  

* Currently, wrangler names correspond to the wrangler class `name` attribute in this module's files.
* Each wrangler's parameters correspond to the constructor arguments for that wrangler. 

## Wrangler types 

### AcceptedNameTreeWrangler
* optional
  * **name_map** (dict): A map of original name to accepted name.
  * **name_resolver** (str or Method): If provided, use this method for getting new accepted names. 
    If set to 'gbif', use GBIF name resolution. 
  * **purge_failures** (bool): Should failures be purged from the tree.
  
### MatchMatrixTreeWrangler
* required
  *  **matrix** (Matrix): A matrix to get taxon names to match.
  *  **species_axis** (int): The matrix axis with taxon names.

### SubsetTreeWrangler
* required
  * **keep_taxa** (list of str): A list of taxon names to keep.

