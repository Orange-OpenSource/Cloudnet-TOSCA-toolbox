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

import logging  # for logging purposes.
import os
from sys import stderr

import cloudnet.tosca.configuration as configuration
from cloudnet.tosca.diagnostics import diagnostic
from cloudnet.tosca.importers import ArchiveImporter
from cloudnet.tosca.utils import normalize_name

configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "WARNING",
}

LOGGER = logging.getLogger(__name__)

# For colored printing.
CEND = "\33[0m"
CRED = "\33[31m"
CYELLOW = "\33[33m"


class Processor(object):
    """
    Abstract base class for processors.
    """

    def __init__(
        self,
        tosca_service_template=None,
        configuration=None,
        type_system=None,
        processor=None,
    ):
        if processor is not None:
            self.tosca_service_template = processor.tosca_service_template
            self.configuration = processor.configuration
            self.type_system = processor.type_system
        else:
            self.tosca_service_template = tosca_service_template
            self.configuration = configuration
            self.type_system = type_system
        self.nb_errors = 0
        self.nb_warnings = 0
        self.logger = logging.getLogger(self.__class__.__module__)

    def get_mapping(self, key, mappings):
        previous = None
        while True:
            result = previous
            previous = mappings.get(key)
            if previous is None:
                break
            else:
                key = previous
                if isinstance(key, list):
                    result = []
                    for value in key:
                        mapping = self.get_mapping(value, mappings)
                        if mapping is not None:
                            result.append(mapping)
                        else:
                            result.append(value)
                    break
        return result

    def get_tosca_definitions_version(self):
        return self.tosca_service_template.get_yaml().get("tosca_definitions_version")

    def is_tosca_definitions_version_file(self):
        tosca_definitions_version = self.get_tosca_definitions_version()
        if tosca_definitions_version:
            path = self.tosca_service_template.get_fullname()
            result = path.endswith(
                "/profiles/" + tosca_definitions_version + "/types.yaml"
            ) or path.endswith(tosca_definitions_version + ".yaml")
            return result
        return False

    def get_import_full_filepath(self, import_yaml):
        import cloudnet.tosca.syntax as syntax

        import_file = syntax.get_import_file(import_yaml)
        import_repository = syntax.get_import_repository(import_yaml)
        result = import_file
        if import_repository is not None:
            repository = syntax.get_repositories(
                self.tosca_service_template.get_yaml()
            ).get(import_repository)
            if repository is None:
                self.error(
                    ":imports["
                    + str(index)
                    + "]:repository: "
                    + import_repository
                    + " undefined",
                    import_repository,
                )
            else:
                repository_url = syntax.get_repository_url(repository)
                if repository_url is None:
                    self.error(":repositories:" + import_repository + ":url undefined", repository)
                else:
                    result = repository_url + "/" + import_file
        return result

    def error(self, message, value=None):
        print(
            CRED,
            "[ERROR] ",
            self.tosca_service_template.get_fullname(),
            ":",
            message,
            "!",
            CEND,
            sep="",
            file=stderr,
        )
        self.diagnostic('error', message, value=value)
        self.nb_errors += 1

    def warning(self, message, value=None):
        print(
            CYELLOW,
            "[Warning] ",
            self.tosca_service_template.get_fullname(),
            ":",
            message,
            "!",
            CEND,
            sep="",
            file=stderr,
        )
        self.diagnostic('warning', message, value=value)
        self.nb_warnings += 1

    def info(self, message, value=None):
        if self.logger.isEnabledFor(logging.INFO):
            print(
                "[Info] ",
                self.tosca_service_template.get_fullname(),
                ": ",
                message,
                sep="",
                file=stderr,
            )
        self.diagnostic('info', message, value=value)

    def diagnostic(self, gravity, message, value=None):
        diagnostic(
            gravity=gravity,
            file=self.tosca_service_template.get_fullname(), 
            message=message, cls=self.__class__.__name__,
            value=value
            )

    def process(self):
        pass


class Checker(Processor):
    """
    Abstract base class for checkers.
    """

    def check(self):
        return True


class Generator(Processor):
    """
    Abstract base class for generators.
    """

    def __init__(
        self,
        tosca_service_template=None,
        configuration=None,
        type_system=None,
        generator=None,
    ):
        Processor.__init__(
            self, tosca_service_template, configuration, type_system, generator
        )
        if generator is not None:
            self.file = generator.file
        else:
            self.file = None

    def generator_configuration_id(self):
        raise Error("generator_configuration_id must be overloaded!")

    TARGET_DIRECTORY = "target-directory"

    def create_target_directory(self):
        target_directory = self.configuration.get(
            self.generator_configuration_id(), Generator.TARGET_DIRECTORY
        )
        # Get the importer of the template.
        importer = self.tosca_service_template.importer
        if isinstance(importer, ArchiveImporter):
            # If the importer is type of ArchiveImporter then
            # add the basename of the zip file to the target directory.
            target_directory = (
                target_directory + "/" + os.path.basename(importer.zipfile.filename)
            )
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
            self.logger.info(target_directory + "/ created.")
        return target_directory

    def compute_filename(self, tosca_service_template, normalize=True):
        # Compute the file path.
        template_yaml = tosca_service_template.get_yaml()
        metadata = template_yaml.get("metadata")
        if metadata is None:
            metadata = template_yaml
        template_name = metadata.get("template_name")
        if template_name is not None:
            filename = template_name
            template_version = metadata.get("template_version")
            if template_version is not None:
                filename = filename + "-" + str(template_version)
        else:
            tmp = tosca_service_template.get_filename()
            filename = tmp[: tmp.rfind(".")]
        if normalize:
            filename = normalize_name(filename)
        return filename

    def open_file(self, extension, normalize=False):
        # Create the target directory if not already exists.
        target_directory = self.create_target_directory()
        # Compute the file path.
        # TODO: call sefl.compute_filename()
        template_yaml = self.tosca_service_template.get_yaml()
        metadata = template_yaml.get("metadata")
        if metadata is None:
            metadata = template_yaml
        template_name = metadata.get("template_name")
        if template_name is not None:
            filename = template_name
            template_version = metadata.get("template_version")
            if template_version is not None:
                filename = filename + "-" + str(template_version)
            if normalize:
                filename = normalize_name(filename)
            if extension is not None:
                filename = filename + ".ext"
        else:
            filename = self.tosca_service_template.get_filename()
        if extension is not None:
            filename = filename[: filename.rfind(".")]
            if normalize:
                filename = normalize_name(filename)
            filepath = target_directory + "/" + filename + extension
        else:
            filepath = target_directory + "/" + filename
        # Open the file.
        self.file = open(filepath, "w")
        self.logger.info(filepath + " opened.")

    def generate(self, *args, sep=" "):
        print(*args, sep=sep, file=self.file)

    def close_file(self):
        self.file.close()
