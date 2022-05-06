# lmpy.data_wrangling

Submodules under this module define data manipulation that can be configured for
various tools.  Data wrangling requires a configuration file, in JSON format, with a
list of one dictionary per desired wrangle.

* Each dictionary must contain "wrangler_type", with the name of the wrangler types.
* The dictionary will also contain all required parameters and any optional parameters.
