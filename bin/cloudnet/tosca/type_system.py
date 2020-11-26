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

import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.processors import Checker, CRED, CEND
from cloudnet.tosca.utils import merge_dict, normalize_dict
from copy import deepcopy

import os
profiles_directory = 'file:' + os.path.dirname(__file__) + '/profiles'

import cloudnet.tosca.configuration as configuration

TYPE_SYSTEM = 'TypeSystem'
TOSCA_NORMATIVE_TYPES = 'tosca_normative_types'
DEFAULT_TOSCA_NORMATIVE_TYPES = 'default_tosca_normative_types'
SHORT_NAMES = 'short_names'
configuration.DEFAULT_CONFIGURATION[TYPE_SYSTEM] = {
    TOSCA_NORMATIVE_TYPES: {
        'tosca_simple_yaml_1_0': profiles_directory + '/tosca_simple_yaml_1_0/types.yaml',
        'tosca_simple_yaml_1_1': profiles_directory + '/tosca_simple_yaml_1_1/types.yaml',
        'tosca_simple_yaml_1_2': profiles_directory + '/tosca_simple_yaml_1_2/types.yaml',
        'tosca_simple_yaml_1_3': profiles_directory + '/tosca_simple_yaml_1_3/types.yaml'
    },
    DEFAULT_TOSCA_NORMATIVE_TYPES: 'tosca_simple_yaml_1_2',
    SHORT_NAMES: { # TODO: separate short names for TOSCA 1.0, TOSCA 1.1, TOSCA 1.2 and TOSCA 1.3
        'AttachesTo': 'tosca.relationships.AttachesTo',
        'BlockStorage': 'tosca.nodes.BlockStorage', # TODO warning not same in 1.0 and 1.2 Storage. removed
        'ObjectStorage': 'tosca.nodes.ObjectStorage',
        'Compute': 'tosca.nodes.Compute',
        'ConnectsTo': 'tosca.relationships.ConnectsTo',
        'Database': 'tosca.nodes.Database',
        'DBMS': 'tosca.nodes.DBMS',
        'Deployment.Image.VM': 'tosca.artifacts.Deployment.Image.VM',
        'LoadBalancer': 'tosca.nodes.LoadBalancer',
        'HostedOn': 'tosca.relationships.HostedOn',
        'Node': 'tosca.capabilities.Node',
        'PortDef': 'tosca.datatypes.network.PortDef',
        'PortInfo': 'tosca.datatypes.network.PortInfo',
        'PortSpec': 'tosca.datatypes.network.PortSpec',
        'SoftwareComponent': 'tosca.nodes.SoftwareComponent',
        'Root': 'tosca.nodes.Root',
        'WebApplication': 'tosca.nodes.WebApplication',
        'WebServer': 'tosca.nodes.WebServer',
        'tosca:Compute': 'tosca.nodes.Compute',
        'tosca:WebApplication': 'tosca.nodes.WebApplication',
        # TODO: must be completed with all short names
        'tosca.nodes.ObjectStorage': 'tosca.nodes.Storage.ObjectStorage',  # TODO remove later
        'tosca.nodes.BlockStorage': 'tosca.nodes.Storage.BlockStorage',  # TODO remove later
    },
}

configuration.DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

class TypeSystem(object):
    '''
        TOSCA Type System.
    '''

    def __init__(self, configuration):
        self.types = {}
        self.merged_types = {}
        self.artifact_types_by_file_ext = {}
        self.short_names = configuration.get(TYPE_SYSTEM, SHORT_NAMES)

    def is_yaml_type(self, type_name):
        return type_name in [ 'string', 'integer', 'float', 'boolean', 'timestamp', 'null', 'version' ]

    def get_type_uri(self, short_type_name):
        result = short_type_name
        if self.types.get(short_type_name) == None:
            type_name = self.short_names.get(short_type_name)
            if type_name != None:
                result = self.get_type_uri(type_name)
        return result

    def get_type(self, type_name):
        result = self.types.get(type_name)
        if result == None:
            type_name = self.short_names.get(type_name)
            if type_name != None:
                result = self.get_type(type_name)
        return result

    def is_derived_from(self, type_name, derived_from_type_name):
        if type_name == None:
            return False
        if type_name == derived_from_type_name:
            return True
        type_type = self.get_type(type_name)
        if type_type == None:
            return False
        return self.is_derived_from(type_type.get(syntax.DERIVED_FROM), derived_from_type_name)

    def merge_type(self, type_name):
        if type_name == None:
            raise ValueError('type_name == None')
        # Search the result in the cache.
        result = self.merged_types.get(type_name)
        if result != None:
            return result

        result = self.get_type(type_name)
        if result == None:
            LOGGER.error(CRED + type_name + ' unknown!' + CEND)
            return dict()

        requirements = result.get(syntax.REQUIREMENTS)
        if requirements:
            result[syntax.REQUIREMENTS] = normalize_dict(requirements)

        derived_from = result.get(syntax.DERIVED_FROM)
        if derived_from == None:
            result = deepcopy(result)
            requirements = result.get(syntax.REQUIREMENTS)
            if requirements:
                result[syntax.REQUIREMENTS] = normalize_dict(requirements)
        else:
            if not self.is_yaml_type(derived_from):
                tmp = self.merge_type(derived_from)
                result = merge_dict(tmp, result)

        # Store the result in the cache.
        self.merged_types[type_name] = result

        return result

    def merge_node_type(self, node_type_name):
        result = self.merge_type(node_type_name)
        result = deepcopy(result)
        interfaces = result.get(syntax.INTERFACES)
        if interfaces:
            for (interface_name, interface_yaml) in interfaces.items():
                interface_type = self.get_type(syntax.get_type(interface_yaml))
                if interface_type:
                    interfaces[interface_name] = merge_dict(interface_type, interfaces[interface_name])
        for (capability_name, capability_yaml) in syntax.get_capabilities(result).items():
            if type(capability_yaml) == dict:
                value = capability_yaml.get('value') # TODO: rename 'value' to '_old_value_'
                if value != None:
                    capability_yaml[syntax.TYPE] = value
        return result

    def get_artifact_type_by_file_ext(self, file_ext):
        return self.artifact_types_by_file_ext.get(file_ext)


class TypeChecker(Checker):
    '''
        TOSCA type system checker
    '''
    def check(self):

        self.info('TOSCA type checking')

        # Load the used TOSCA normative types according to tosca_definitions_version.
        if not self.is_tosca_definitions_version_file():
            tosca_normative_types_map = self.configuration.get(TYPE_SYSTEM, TOSCA_NORMATIVE_TYPES)
            tosca_normative_types = self.get_mapping(self.get_tosca_definitions_version(), tosca_normative_types_map)
            if tosca_normative_types == None:
                default_tosca_normative_types = self.configuration.get(TYPE_SYSTEM, DEFAULT_TOSCA_NORMATIVE_TYPES)
                if default_tosca_normative_types != None:
                    self.warning(' '+ default_tosca_normative_types + ' normative types loaded')
                    tosca_normative_types = self.get_mapping(default_tosca_normative_types, tosca_normative_types_map)
                else:
                    self.warning(' no normative types loaded')
                    tosca_normatives_type = None
            if tosca_normative_types == None:
                pass # nothing to do.
            elif type(tosca_normative_types) == str:
                self.load_tosca_yaml_template(tosca_normative_types, self.tosca_service_template)
            elif type(tosca_normative_types) == list:
                for value in tosca_normative_types:
                    self.load_tosca_yaml_template(value, self.tosca_service_template)
            else:
                raise ValueError(TYPE_CHECKER + ':' + TOSCA_NORMATIVE_TYPES + ' must be a string or list')

        # Load the tosca template.
        self.load_tosca_yaml_template(self.tosca_service_template.get_filename(), self.tosca_service_template)

        # TODO: add type checks

        return True

    def load_tosca_yaml_template(self, path, importer, namescape_prefix = '', already_loaded_paths = {}):
        # Load the tosca service template if not already loaded.
        tosca_service_template = already_loaded_paths.get(path)
        if tosca_service_template == None:
            tosca_service_template = importer.imports(path)
            already_loaded_paths[path] = tosca_service_template
        elif namescape_prefix == '':
            return
        template_yaml = tosca_service_template.get_yaml()

        # Load imported templates.
        index = 0
        for import_yaml in syntax.get_imports(template_yaml):
            try:
                import_filepath = self.get_import_full_filepath(import_yaml)
                import_namespace_prefix = syntax.get_import_namespace_prefix(import_yaml)
                if import_namespace_prefix == None:
                    import_namespace_prefix = '' # no prefix
                else:
                    import_namespace_prefix = import_namespace_prefix + ':'
                self.load_tosca_yaml_template(import_filepath, tosca_service_template, import_namespace_prefix, already_loaded_paths)
            except FileNotFoundError:
                # It seems that we get a program crash here but I didn't figure out 
                # how to deal with yet !
                # This case occurs when a file imported is not present
                # JLC 20201126
                self.error(':imports[' + str(index) + ']:file: ' + import_filepath + ' not found')
            index = index + 1

        # Put types of the loaded template into the type cache.
        for type_kind in [syntax.ARTIFACT_TYPES, syntax.DATA_TYPES, syntax.INTERFACE_TYPES, syntax.CAPABILITY_TYPES, syntax.REQUIREMENT_TYPES, syntax.RELATIONSHIP_TYPES, syntax.NODE_TYPES, syntax.GROUP_TYPES, syntax.POLICY_TYPES]:
            types = template_yaml.get(type_kind)
            if types:
                # Cache node types of the current YAML file.
                for (type_name, type_yaml) in types.items():
                    self.type_system.types[namescape_prefix + type_name] = type_yaml

        # Associate file extensions to artifact types.
        artifact_types = syntax.get_artifact_types(template_yaml)
        if artifact_types == None:
            artifact_types = {}
        for artifact_name, artifact_yaml in artifact_types.items():
            for file_ext in artifact_yaml.get(syntax.FILE_EXT, []):
                artifact_type = self.type_system.get_artifact_type_by_file_ext(file_ext)
                if artifact_type:
                    self.warning("file extension '" + file_ext + "' already associated to " + artifact_type)
                    continue
                self.type_system.artifact_types_by_file_ext[file_ext] = namescape_prefix + artifact_name
