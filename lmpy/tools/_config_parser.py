"""Module containing a tool for parsing a configuration file for argparse."""
import json
import sys


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
    # If positional arguments are not specified, we need to create dummy values so
    #     argparse doesn't fail.  To do that, we need to find where they should start
    #     and add dummy values there.  Determine where they start by finding the last
    #     specified optional parameter and stepping `nargs` steps specified by that
    #     optional parameter.

    # Create optional parameter dict
    #     Cannot just look for '-' because some positional arguments can be negative
    #     values.
    opt_param_nargs = {}
    for opt_param in parser._optionals._group_actions:
        opt_nargs = opt_param.nargs
        if opt_nargs is None or opt_nargs == '+':
            opt_nargs = 1
        elif opt_nargs == '*':
            opt_nargs = 0
        for o_str in opt_param.option_strings:
            opt_param_nargs[o_str] = opt_nargs

    # Find last optional parameter
    last_option_index = -1
    for arg_i in range(1, len(sys.argv)):
        # Split the argument on '=' and check if it is in known options
        if sys.argv[arg_i].split('=')[0] in opt_param_nargs.keys():
            last_option_index = arg_i

    # Find the start of the positional arguments
    if last_option_index < 0:
        # If no optional arguments, first positional starts at index 1
        pos_idx = 1
    else:
        # Check last optional parameter for =, positionals start after that
        if '=' in sys.argv[last_option_index]:
            pos_idx = last_option_index + 1
        # Otherwise, add nargs to get positionals start
        else:
            opt_nargs = opt_param_nargs[sys.argv[last_option_index]]
            pos_idx = last_option_index + opt_nargs + 1

    # Check if each positional argument is present
    for pos_arg in parser._positionals._group_actions:
        # Get nargs for this positional
        if pos_arg.nargs is None:
            pos_nargs = 1
        else:
            pos_nargs = pos_arg.nargs

        # Move pos_idx
        pos_idx += pos_nargs
        # Add dummy values if the target number of args is less than len(sys.argv)
        for _ in range(max(0, pos_idx - len(sys.argv))):
            # If choices, pick one
            if pos_arg.choices is not None:
                sys.argv.append(pos_arg.choices[0])
            else:
                # Add stringified integer, they can be cast to any primitive type
                sys.argv.append(str(1))

    args = parser.parse_args()

    if config_arg is not None and hasattr(args, config_arg):
        config_filename = getattr(args, config_arg)
        if config_filename is not None:
            with open(config_filename, mode='rt') as in_json:
                config = json.load(in_json)
                for k in config.keys():
                    # Always replace existing values
                    setattr(args, k, config[k])
    return args
