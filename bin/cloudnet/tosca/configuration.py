######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import logging
import logging.config
import os

import yaml
from cloudnet.tosca.utils import merge_dict

LOGGER = logging.getLogger(__name__)

CONFIGURATION_FILE = "tosca2cloudnet.yaml"


def load(config_file=CONFIGURATION_FILE):
    configuration = DEFAULT_CONFIGURATION

    if os.path.exists(config_file):
        # Load the configuration file if it exists.
        with open(config_file, "r") as stream:
            content = yaml.load(stream, Loader=yaml.FullLoader)
            configuration = merge_dict(DEFAULT_CONFIGURATION, content)

    # Configure logging.
    logging.config.dictConfig(configuration["logging"])

    # Log the configuration file loading.
    if configuration != DEFAULT_CONFIGURATION:
        LOGGER.info(config_file + " loaded.")

    # Return the configuration.
    return Configuration(configuration)


class Configuration(object):
    """
    This is a class for managing configuration.
    """

    def __init__(self, configuration):
        self.configuration = configuration

    def get(self, *path):
        result = self.configuration
        for p in path:
            result = result[p]
        return result


#
# Default configuration
#
DEFAULT_CONFIGURATION = {
    "logging": {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            __name__: {
                "level": "INFO",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}
