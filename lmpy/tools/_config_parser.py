"""Module containing a tool for parsing a configuration file for argparse."""
import json


# .....................................................................................
def _process_arguments(parser, config_arg=None):
    """Process arguments including filling in those provided by configuration file.

    Args:
        parser (argparse.ArgumentParser): An argparse.ArgumentParser with parameters.
        config_arg (str): If provided, try to read configuration file for additional
            arguments.

    Returns:
        argparse.Namespace: An augmented Namespace with any parameters specified in a
            configuration file.
    """
    args = parser.parse_args()

    if config_arg is not None and hasattr(args, config_arg):
        config_filename = getattr(args, config_arg)
        if config_filename is not None:
            with open(config_filename, mode='rt') as in_json:
                config = json.load(in_json)
                for k in config.keys():
                    tmp = getattr(args, k)
                    if tmp is None:
                        setattr(args, k, config[k])
                    elif isinstance(tmp, list):
                        tmp.extend(config[k])
                        setattr(args, k, tmp)
    return args
