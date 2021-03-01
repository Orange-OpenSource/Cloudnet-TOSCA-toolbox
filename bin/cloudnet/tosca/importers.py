######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-21 Orange
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
import requests  # for HTTP GET requests.
import yaml  # for parsing YAML.
import zipfile  # for reading ZIP files.

import cloudnet.tosca.configuration as configuration
import requests  # for HTTP GET requests.

configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}

# init logger
LOGGER = logging.getLogger(__name__)


class ToscaServiceTemplate(object):
    """
    Represents a TOSCA service template.
    """

    def __init__(self, filename, yaml_content, importer):
        """
        Constructor.
        """
        self.filename = filename
        self.yaml_content = yaml_content
        self.importer = importer
        LOGGER.debug("%r created" % self)

    def __repr__(self):
        """
        Textual representation.
        """
        return "<ToscaServiceTemplate filename=%s importer=%r>" % (
            self.filename,
            self.importer,
        )

    def get_filename(self):
        return self.filename

    def get_fullname(self):
        return self.importer.get_fullname() + self.filename

    def get_yaml(self):
        return self.yaml_content

    def imports(self, path):
        """
        Imports a TOSCA service template from the importer of this template.
        """
        return self.importer.imports(path)


class Importer(object):
    """
    Abstract base class for importers of TOSCA service templates.
    """

    # Root importer used to load HTTP and aliased templates.
    root_importer = None

    def __init__(self, base_path, alias={}):
        """
        Constructor.
        """
        self.base_path = base_path
        self.alias = alias
        # Init the cache of already loaded TOSCA service templates.
        self.already_loaded_tosca_service_templates = {}
        # Init the cache of children importers.
        self.children_importers = {}
        # Store the first created imported as the root importer.
        if Importer.root_importer is None:
            Importer.root_importer = self
        LOGGER.debug("%r created" % self)

    def __repr__(self):
        """
        Textual representation.
        """
        return "<%s base_path=%s>" % (type(self).__name__, self.base_path)

    def get_fullname(self):
        return self.base_path

    def imports(self, path):
        """
        Imports a TOSCA service template.
        """
        LOGGER.debug("import %s from %r" % (path, self))

        # Try to resolve aliased files.
        filepath = Importer.root_importer.alias.get(path)
        if filepath != None:
            return Importer.root_importer.imports(filepath)

        # Cut the path into its base path and file name.
        index = path.rfind("/")
        base_path = path[: index + 1]
        filename = path[index + 1 :]

        # if not / in path then use the current importer.
        if base_path == "":
            importer = self
        # if path is an url then reuse or create an URL importer.
        elif base_path.startswith("file:"):
            base_path = base_path[len("file:") :]
            importer = Importer.root_importer.children_importers.get(base_path)
            if importer is None:
                importer = FilesystemImporter(base_path)
                Importer.root_importer.children_importers[base_path] = importer
        elif base_path.startswith("http:") or base_path.startswith("https:"):
            importer = Importer.root_importer.children_importers.get(base_path)
            if importer is None:
                importer = UrlImporter(base_path)
                Importer.root_importer.children_importers[base_path] = importer
        # else reuse or create an importer of the same type of the current importer.
        else:
            importer = self.children_importers.get(base_path)
            if importer is None:
                importer = self.new_importer(base_path)
                self.children_importers[base_path] = importer

        # Is this tosca service template already loaded?
        tosca_service_template = importer.already_loaded_tosca_service_templates.get(
            filename
        )
        if tosca_service_template is not None:
            return tosca_service_template  # then return it.

        # Load the YAML content.
        LOGGER.debug(
            "load_yaml %s%s from %r" % (importer.base_path, filename, importer)
        )
        try:
            yaml_content = importer.load_yaml(importer.base_path + filename)
        except FileNotFoundError:
            raise FileNotFoundError("No such file: " + filename)
        except yaml.YAMLError as exc:
            problem = exc.problem
            if problem.startswith("found unexpected end of stream"):
                problem = "missed quote at the end of the string"
            elif problem.startswith("expected <block end>, but found"):
                problem = "incorrect indentation"
            elif problem == "mapping values are not allowed here":
                problem = "incorrect indentation or string must be quoted"
            if exc.context is None:
                raise ValueError(
                    "%s at line %s column %s"
                    % (problem, exc.problem_mark.line + 1, exc.problem_mark.column + 1)
                )
            else:
                raise ValueError(
                    "%s at line %s column %s %s at line %s column %s"
                    % (
                        problem,
                        exc.problem_mark.line + 1,
                        exc.problem_mark.column + 1,
                        exc.context,
                        exc.context_mark.line + 1,
                        exc.context_mark.column + 1,
                    )
                )

        # Create the TOSCA service template.
        tosca_service_template = ToscaServiceTemplate(filename, yaml_content, importer)

        # Store the loaded tosca service template.
        importer.already_loaded_tosca_service_templates[
            filename
        ] = tosca_service_template

        # Return the TOSCA service template.
        return tosca_service_template

    def new_importer(self, path):
        """
        Creates a new importer.
        """
        raise NotImplementedError()

    def load_yaml(self, filename):
        """
        Loads a YAML file.
        """
        raise NotImplementedError()


class FilesystemImporter(Importer):
    """
    Importer of TOSCA service templates as files.
    """

    def new_importer(self, path):
        """
        Creates a new importer.
        """
        return FilesystemImporter(self.base_path + path, self.alias)

    def load_yaml(self, filename):
        """
        Loads a YAML file.
        """
        with open(filename, "r") as stream:
            return yaml.safe_load(stream)


class UrlImporter(Importer):
    """
    Importer of TOSCA service templates as HTTP resources.
    """

    def new_importer(self, path):
        """
        Creates a new importer.
        """
        return UrlImporter(self.base_path + path, self.alias)

    def load_yaml(self, filename):
        """
        Loads a YAML file.
        """
        try:
            response = requests.get(filename)
        except requests.exceptions.ConnectionError:
            raise FileNotFoundError(filename)
        if response.status_code == 404:
            raise FileNotFoundError(filename)
        return yaml.safe_load(response.text)


class ArchiveImporter(Importer):
    """
    Importer of TOSCA service templates as archive resources.
    """

    def __init__(self, zipFile, base_path="", alias={}):
        """
        Constructor.
        """
        if isinstance(zipFile, zipfile.ZipFile):
            self.zipfile = zipFile
        else:
            self.zipfile = zipfile.ZipFile(zipFile, "r")
        Importer.__init__(self, base_path, alias)

    def __repr__(self):
        """
        Textual representation.
        """
        return "<ArchiveImporter zipfile=%r base_path=%s>" % (
            self.zipfile,
            self.base_path,
        )

    def get_fullname(self):
        return self.zipfile.filename + ":" + self.base_path

    def new_importer(self, path):
        """
        Creates a new importer.
        """
        return ArchiveImporter(self.zipfile, self.base_path + path, self.alias)

    def load_yaml(self, filename):
        """
        Loads a YAML file.
        """
        try:
            with self.zipfile.open(filename) as stream:
                return yaml.safe_load(stream)
        except KeyError:
            raise FileNotFoundError(filename)


def imports(tosca_service_template_path, alias={}):
    # Inits the root loader of TOSCA service templates.
    importer = FilesystemImporter("", alias)

    if not (
        tosca_service_template_path.endswith(".csar")
        or tosca_service_template_path.endswith(".zip")
    ):
        return importer.imports(tosca_service_template_path)
    else:
        importer = ArchiveImporter(tosca_service_template_path, "", alias)
        tosca_meta = importer.imports("TOSCA-Metadata/TOSCA.meta").get_yaml()
        if not isinstance(tosca_meta, dict):
            raise ValueError("Invalid TOSCA-Metadata/TOSCA.meta file")
        entry_definitions = tosca_meta.get("Entry-Definitions")
        if entry_definitions is None:
            raise ValueError("No entry-definitions in TOSCA-Metadata/TOSCA.meta")
        return importer.imports(entry_definitions)
