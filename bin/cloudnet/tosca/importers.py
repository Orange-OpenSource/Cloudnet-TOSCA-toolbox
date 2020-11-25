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

import requests # for HTTP GET requests.
import yaml # for parsing YAML.
import zipfile # for reading ZIP files.

import cloudnet.tosca.configuration as configuration
configuration.DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

class ToscaServiceTemplate(object):
    '''
        Represents a TOSCA service template.
    '''

    def __init__(self, filename, yaml_content, importer):
        '''
            Constructor.
        '''
        self.filename = filename
        self.yaml_content = yaml_content
        self.importer = importer

    def __repr__(self):
        '''
            Textual representation.
        '''
        return '<ToscaServiceTemplate filename=' + self.filename + ' importer=' + repr(self.importer) + '>'

    def get_filename(self):
        return self.filename

    def get_fullname(self):
        return self.importer.get_fullname() + self.filename

    def get_yaml(self):
        return self.yaml_content

    def imports(self, path):
        '''
            Imports a TOSCA service template from the importer of this template.
        '''
        return self.importer.imports(path)

class Importer(object):
    '''
        Abstract base class for importers of TOSCA service templates.
    '''

    # Root importer used to load HTTP and aliased templates.
    root_importer = None

    def __init__(self, base_path, alias={}):
        '''
            Constructor.
        '''
        self.base_path = base_path
        self.alias = alias
        # Init the cache of already loaded TOSCA service templates.
        self.already_loaded_tosca_service_templates = {}
        # Init the cache of children importers.
        self.children_importers = {}
        # Store the first created imported as the root importer.
        if Importer.root_importer == None:
            Importer.root_importer = self
        LOGGER.debug(str(self) + ' created')

    def __repr__(self):
        '''
            Textual representation.
        '''
        return '<' + type(self).__name__ + ' base_path=' + self.base_path + '>'

    def get_fullname(self):
        return self.base_path

    def imports(self, path):
        '''
            Imports a TOSCA service template.
        '''

        LOGGER.debug('Imports ' + path + ' from ' + str(self))

        # Try to resolve aliased files.
        filepath = Importer.root_importer.alias.get(path)
        if filepath:
            return Importer.root_importer.imports(filepath)

        # Cut the path into its base path and file name.
        index = path.rfind('/')
        base_path = path[:index+1]
        filename = path[index+1:]

        # if not / in path then use the current importer.
        if base_path == '':
            importer = self
        # if path is an url then reuse or create an URL importer.
        elif base_path.startswith('file:'):
            base_path = base_path[len('file:'):]
            importer = Importer.root_importer.children_importers.get(base_path)
            if importer == None:
                importer = FilesystemImporter(base_path)
                Importer.root_importer.children_importers[base_path] = importer
        elif base_path.startswith('http:') or base_path.startswith('https:'):
            importer = Importer.root_importer.children_importers.get(base_path)
            if importer == None:
                importer = UrlImporter(base_path)
                Importer.root_importer.children_importers[base_path] = importer
        # else reuse or create an importer of the same type of the current importer.
        else:
            importer = self.children_importers.get(base_path)
            if importer == None:
                importer = self.new_importer(base_path)
                self.children_importers[base_path] = importer

        # Is this tosca service template already loaded?
        tosca_service_template = importer.already_loaded_tosca_service_templates.get(filename)
        if tosca_service_template:
            return tosca_service_template # then return it.

        # Load the YAML content.
        LOGGER.debug('Loads ' + importer.base_path + filename + ' from ' + str(importer))
        try:
            yaml_content = importer.load_yaml(importer.base_path + filename)
        except FileNotFoundError:
            raise FileNotFoundError('No such file: ' +  filename)

        # Create the TOSCA service template.
        tosca_service_template = ToscaServiceTemplate(filename, yaml_content, importer)

        # Store the loaded tosca service template.
        importer.already_loaded_tosca_service_templates[filename] = tosca_service_template

        # Return the TOSCA service template.
        return tosca_service_template

    def new_importer(self, path):
        '''
            Creates a new importer.
        '''
        pass

    def load_yaml(self, filename):
        '''
            Loads a YAML file.
        '''
        pass

class FilesystemImporter(Importer):
    '''
        Importer of TOSCA service templates as files.
    '''

    def new_importer(self, path):
        '''
            Creates a new importer.
        '''
        return FilesystemImporter(self.base_path + path, self.alias)

    def load_yaml(self, filename):
        '''
            Loads a YAML file.
        '''
        template = ""
        with open(filename, 'r') as stream:
            try:
                template = yaml.load(stream, Loader=yaml.SafeLoader)
            except yaml.YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    raise ValueError("Yaml error line %s column %s" % (mark.line+1, mark.column+1))

        return template

class UrlImporter(Importer):
    '''
        Importer of TOSCA service templates as HTTP resources.
    '''

    def new_importer(self, path):
        '''
            Creates a new importer.
        '''
        return UrlImporter(self.base_path + path, self.alias)

    def load_yaml(self, filename):
        '''
            Loads a YAML file.
        '''
        response = requests.get(filename)
        if response.status_code == 404:
            raise FileNotFoundError(filename)
        return yaml.load(response.text, Loader=yaml.FullLoader)

class ArchiveImporter(Importer):
    '''
        Importer of TOSCA service templates as archive resources.
    '''

    def __init__(self, zipFile, base_path='', alias={}):
        '''
            Constructor.
        '''
        if type(zipFile) == zipfile.ZipFile:
            self.zipfile = zipFile
        else:
            self.zipfile = zipfile.ZipFile(zipFile, 'r')
        Importer.__init__(self, base_path, alias)

    def __repr__(self):
        '''
            Textual representation.
        '''
        return '<ArchiveImporter zipfile=' + repr(self.zipfile) + ' base_path=' + self.base_path + '>'

    def get_fullname(self):
        return self.zipfile.filename + ':' + self.base_path

    def new_importer(self, path):
        '''
            Creates a new importer.
        '''
        return ArchiveImporter(self.zipfile, self.base_path + path, self.alias)

    def load_yaml(self, filename):
        '''
            Loads a YAML file.
        '''
        try:
            with self.zipfile.open(filename) as stream:
                return yaml.load(stream, Loader=yaml.FullLoader)
        except KeyError:
            raise FileNotFoundError(filename)

def imports(tosca_service_template_path, alias={}):
    # Inits the root loader of TOSCA service templates.
    importer = FilesystemImporter('', alias)

    if not (tosca_service_template_path.endswith('.csar') or tosca_service_template_path.endswith('.zip')):
        return importer.imports(tosca_service_template_path)
    else:
        importer = ArchiveImporter(tosca_service_template_path, '', alias)
        tosca_meta = importer.imports('TOSCA-Metadata/TOSCA.meta').get_yaml()
        if type(tosca_meta) != dict:
            raise ValueError('Invalid TOSCA-Metadata/TOSCA.meta file')
        entry_definitions = tosca_meta.get('Entry-Definitions')
        if entry_definitions == None:
            raise ValueError('No entry-definitions in TOSCA-Metadata/TOSCA.meta')
        return importer.imports(entry_definitions)
