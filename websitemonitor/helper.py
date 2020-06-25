"""Helper tools"""

import argparse
import configparser
import logging

def parse_cmd_line_args(argv):
    """Parse command line arguments

    Args:
        argv (list): List of arguments given on the command line

    Returns:
        The returned object will have the following members:

        args.kakfa-config-file   string
        args.config-file         string
        args.verbose             boolean

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--kafka-config-file",
                        action="store",
                        dest="kafka_config_file",
                        required=True)
    parser.add_argument("--config-file",
                        action="store",
                        dest="config_file",
                        required=True)
    parser.add_argument("--verbose",
                        action="store_true",
                        required=False)

    args = parser.parse_args(argv)

    return args

def config(filename, section="DEFAULT"):
    """Parses a configuration file

    Args:
        filename (str): Location of the config file to parse
        section (str): Section to parse within this config file (defaults to DEFAULT)

    Returns:
        A configparser.ConfigParser() object for the section given

    """

    parser = configparser.ConfigParser()

    # explicitly open in order to catch a missing file
    with open(filename) as file_handle:
        parser.read_file(file_handle)

    return parser[section]

def setup_logging(name, verbose):
    """Configures basic logging behaviour

    Args:
        name (str): The log prefix to use
        verbose (bool): If logging.DEBUG should be set

    Returns:
        A loggging.Logger object
    """

    logging.basicConfig()
    logger = logging.getLogger(name)

    if verbose:
        logger.setLevel(logging.DEBUG)

    return logger
