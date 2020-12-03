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
        self.artifact_types = {}
        self.data_types = {}
        self.capability_types = {}
        self.interface_types = {}
        self.requirement_types = {}
        self.relationship_types = {}
        self.node_types = {}
        self.group_types = {}
        self.policy_types = {}
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

        self.info('TOSCA type checking...')

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

        self.check_service_template_definition(self.tosca_service_template.get_yaml())

        self.info('TOSCA type checking done.')

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
                self.error(':imports[' + str(index) + ']:file: ' + import_filepath + ' not found')
            index = index + 1

        # Put all types of the loaded template into the type system.
        for type_kind in [syntax.ARTIFACT_TYPES, syntax.DATA_TYPES, syntax.INTERFACE_TYPES, syntax.CAPABILITY_TYPES, syntax.REQUIREMENT_TYPES, syntax.RELATIONSHIP_TYPES, syntax.NODE_TYPES, syntax.GROUP_TYPES, syntax.POLICY_TYPES]:
            # Iterate over types.
            for (type_name, type_yaml) in template_yaml.get(type_kind, {}).items():
                full_type_name = namescape_prefix + type_name
                # TODO: check that this type is not already defined
                if self.type_system.types.get(full_type_name):
                    self.error(type_kind + ':' + type_name + ' already defined')
                else:
                    self.type_system.types[full_type_name] = type_yaml
                    getattr(self.type_system, type_kind)[full_type_name] = type_yaml

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

    def iterate_over_map(self, method, yaml, keyword, context_error_message = None):
        if context_error_message == None:
            context_error_message = ''
        else:
            context_error_message = context_error_message + ':'
        for key, value in yaml.get(keyword, {}).items():
            method(key, value, context_error_message + keyword)

    def check_service_template_definition(self, service_template_definition):
        # check tosca_definitions_version
        # check namespace
        # check metadata
        # check description
        # check dsl_definitions
        # check repositories
        for name, repository_definition in syntax.get_repositories(service_template_definition).items():
            self.check_repository_definition(name, repository_definition)
        # check imports
        # check artifact_types
        self.iterate_over_map(self.check_artifact_type, service_template_definition, syntax.ARTIFACT_TYPES)
        # check data_types
        self.iterate_over_map(self.check_data_type, service_template_definition, syntax.DATA_TYPES)
        # check capability_types
        self.iterate_over_map(self.check_capability_type, service_template_definition, syntax.CAPABILITY_TYPES)
        # check interface_types
        self.iterate_over_map(self.check_interface_type, service_template_definition, syntax.INTERFACE_TYPES)
        # check relationship_types
        self.iterate_over_map(self.check_relationship_type, service_template_definition, syntax.RELATIONSHIP_TYPES)
        # check node_types
        self.iterate_over_map(self.check_node_type, service_template_definition, syntax.NODE_TYPES)
        # check group_types
        self.iterate_over_map(self.check_group_type, service_template_definition, syntax.GROUP_TYPES)
        # check policy_types
        self.iterate_over_map(self.check_policy_type, service_template_definition, syntax.POLICY_TYPES)
        # check topology_template
        self.check_topology_template(syntax.get_topology_template(service_template_definition))

    def check_repository_definition(self, repository_name, repository_definition, context_error_message):
        pass # TODO

    def array_to_string_with_or_separator(self, array):
        return str(array).replace("['", '').replace("']", '').replace("', '", ' or ')

    def check_type_existence(self, type_kinds, type_name, context_error_message):
        if type_name == None:
            return True
        if type(type_kinds) == str:
            type_kinds = [ type_kinds ]
        for type_kind in type_kinds:
            if getattr(self.type_system, type_kind + '_types').get(type_name):
                return True
        if self.type_system.types.get(type_name) == None:
            self.error(context_error_message + ': ' + type_name + ' undefined, ' + self.array_to_string_with_or_separator(type_kinds) + ' type required')
        else:
            self.error(context_error_message + ': ' + type_name + ' not ' + self.array_to_string_with_or_separator(type_kinds) + ' type')
        return False

    def check_derived_from(self, type_kind, type_name, type_definition):
        context_error_message = type_kind + '_types:' + type_name + ':' + syntax.DERIVED_FROM
        derived_from = syntax.get_derived_from(type_definition)
        self.check_type_existence(type_kind, derived_from, context_error_message)
        if self.type_system.is_derived_from(derived_from, type_name):
            self.error(context_error_message + ': ' + derived_from + ' cyclically derived from ' + type_name)

    def get_derived_from_merged_type(self, type_name, type_yaml):
        derived_from = syntax.get_derived_from(type_yaml)
        if derived_from == None:
            return {}
        if self.type_system.is_derived_from(derived_from, type_name):
            return {}
        return self.type_system.merge_type(derived_from)

    def check_array_of_types(self, type_name, type_yaml, field_name, field_type_kinds, context_error_message):
        derived_from_type = self.get_derived_from_merged_type(type_name, type_yaml)
        derived_from_type_field_values = derived_from_type.get(field_name)
        idx = 0
        for field_value in type_yaml.get(field_name, []):
            self.check_type_existence(field_type_kinds, field_value, context_error_message + ':' + type_name + ':' + field_name + '[' + str(idx) + ']')
            if derived_from_type_field_values:
                # check that field value is compatible with derived_from values
                not_compatible_with_derived_from_field_values = True
                for derived_from_field_value in derived_from_type_field_values:
                    if self.type_system.is_derived_from(field_value, derived_from_field_value):
                        not_compatible_with_derived_from_field_values = False
                        break
                if not_compatible_with_derived_from_field_values:
                    self.error(context_error_message + ':' + type_name + ':' + field_name + '[' + str(idx) + ']: ' + field_value + ' not compatible with derived from ' + field_name + ', i.e. ' + self.array_to_string_with_or_separator(derived_from_type_field_values))
            idx = idx + 1

    def check_datatype(self, datatype, context_error_message):
        # TODO complete with map list scalar* shortname to datatype
        # if not self.type_system.is_yaml_type(datatype):
        #    self.check_type_existence('data', datatype, context_error_message)
        pass

    def check_attribute_definition(self, attribute_name, attribute_definition, context_error_message):
        context_error_message = context_error_message + ':' + attribute_name
        # check type
        self.check_datatype(attribute_definition.get(syntax.TYPE), context_error_message + ':' + syntax.TYPE)
        # TODO check that type is compatible with previous attribute definition
        # check description
        # check default # TODO
        # check status
        # check entry_schema # TODO

    def check_property_definition(self, property_name, property_definition, context_error_message):
        context_error_message = context_error_message + ':' + property_name
        # check type
        self.check_datatype(property_definition.get(syntax.TYPE), context_error_message + ':' + syntax.TYPE)
        # TODO check that type is compatible with previous attribute definition
        # check description
        # check required
        # check default # TODO
        # check status
        # check constraints # TODO check_constraint_clause
        # check entry_schema # TODO check_entry_schema
        # check external_schema
        # check metadata

    def check_requirement_definition(self, requirement_name, requirement_definition, context_error_message):
        context_error_message = context_error_message + ':' + requirement_name
        # check description
        # check capability
        self.check_type_existence('capability', syntax.get_requirement_capability(requirement_definition), context_error_message + ':capability')
        # TODO check compatibility with previous definition
        # check node
        self.check_type_existence('node', syntax.get_requirement_node_type(requirement_definition), context_error_message + ':node')
        # TODO check compatibility with previous definition
        # check relationship type
        self.check_type_existence('relationship', syntax.get_requirement_relationship(requirement_definition), context_error_message + ':relationship')
        # TODO check compatibility with previous definition
        # check relationship interfaces
        # TODO check_interface_definition
        # check occurrences
        # TODO

    def check_capability_definition(self, capability_name, capability_definition, context_error_message):
        context_error_message = context_error_message + ':' + capability_name
        # check description
        # check type
        self.check_type_existence('capability', syntax.get_capability_type(capability_definition), context_error_message + ':type')
        # TODO check compatibility with previous definition
        # stop checking when capability_definition is just a string
        if type(capability_definition) == str:
            return
        # check properties # TODO
        # check attributes # TODO
        # check valid_source_types
        self.check_array_of_types(capability_name, capability_definition, syntax.VALID_SOURCE_TYPES, 'node', context_error_message)
        # TODO check valid_source_types compatible with previous capability definition
        # check occurrences # TODO

    def check_interface_definition(self, interface_name, interface_definition, context_error_message):
        context_error_message = context_error_message + ':' + interface_name
        # check description
        # check type
        self.check_type_existence('interface', interface_definition.get(syntax.TYPE), context_error_message + ':type')
        # TODO check compatibility with previous definition
        # check inputs # TODO check_property_definition
        # check operations # TODO check_operation_definition

    def check_artifact_definition(self, artifact_name, artifact_definition, context_error_message):
        pass # TODO
        # check type
        self.check_type_existence('artifact', artifact_definition.get(syntax.TYPE), context_error_message + ':type')
        # TODO check compatibility with previous definition
        # check file
        # check repository # TODO
        # check description
        # check deploy_path
        # check properties # TODO

    def check_artifact_type(self, artifact_type_name, artifact_type, context_error_message):
        # check derived_from
        self.check_derived_from('artifact', artifact_type_name, artifact_type)
        # check version
        # check metadata
        # check description
        # check mime_type
        # check file_ext
        # check properties
        self.iterate_over_map(self.check_property_definition, artifact_type, syntax.PROPERTIES, context_error_message)

    def check_data_type(self, data_type_name, data_type, context_error_message):
        # check derived_from
        if not self.type_system.is_yaml_type(syntax.get_derived_from(data_type)):
            self.check_derived_from('data', data_type_name, data_type)
        # check version
        # check metadata
        # check description
        # check constraints
        # TODO check_constraint_clause
        # check properties
        self.iterate_over_map(self.check_property_definition, data_type, syntax.PROPERTIES, context_error_message)

    def check_capability_type(self, capability_type_name, capability_type, context_error_message):
        # check derived_from
        self.check_derived_from('capability', capability_type_name, capability_type)
        # check version
        # check metadata
        # check description
        # check properties
        self.iterate_over_map(self.check_property_definition, capability_type, syntax.PROPERTIES, context_error_message)
        # check attributes
        self.iterate_over_map(self.check_attribute_definition, capability_type, syntax.ATTRIBUTES, context_error_message)
        # check valid_source_types
        self.check_array_of_types(capability_type_name, capability_type, syntax.VALID_SOURCE_TYPES, 'node', syntax.CAPABILITY_TYPES)

    def check_interface_type(self, interface_type_name, interface_type, context_error_message):
        # check derived_from
        self.check_derived_from('interface', interface_type_name, interface_type)
        # check version
        # check metadata
        # check description
        # check inputs
        self.iterate_over_map(self.check_property_definition, interface_type, syntax.INPUTS, context_error_message)
        # check operations
        # TODO check_operation_definition

    def check_relationship_type(self, relationship_type_name, relationship_type, context_error_message):
        # check derived_from
        self.check_derived_from('relationship', relationship_type_name, relationship_type)
        # check version
        # check metadata
        # check description
        # check attributes
        self.iterate_over_map(self.check_attribute_definition, relationship_type, syntax.ATTRIBUTES, context_error_message)
        # check properties
        self.iterate_over_map(self.check_property_definition, relationship_type, syntax.PROPERTIES, context_error_message)
        # check interfaces
        self.iterate_over_map(self.check_interface_definition, relationship_type, syntax.INTERFACES, context_error_message)
        # check valid_target_types
        self.check_array_of_types(relationship_type_name, relationship_type, syntax.VALID_TARGET_TYPES, 'capability', syntax.RELATIONSHIP_TYPES)

    def check_node_type(self, node_type_name, node_type, context_error_message):
        # check derived_from
        self.check_derived_from('node', node_type_name, node_type)
        # check version
        # check metadata
        # check description
        # check attributes
        self.iterate_over_map(self.check_attribute_definition, node_type, syntax.ATTRIBUTES, context_error_message)
        # check properties
        self.iterate_over_map(self.check_property_definition, node_type, syntax.PROPERTIES, context_error_message)
        # check requirements
        for name, definition in syntax.get_requirements_dict(node_type).items():
            self.check_requirement_definition(name, definition, context_error_message + ':' + syntax.REQUIREMENTS)
        # check capabilities
        self.iterate_over_map(self.check_capability_definition, node_type, syntax.CAPABILITIES, context_error_message)
        # check interfaces
        self.iterate_over_map(self.check_interface_definition, node_type, syntax.INTERFACES, context_error_message)
        # check artifacts
        self.iterate_over_map(self.check_artifact_definition, node_type, syntax.ARTIFACTS, context_error_message)

    def check_group_type(self, group_type_name, group_type, context_error_message):
        context_error_message = syntax.GROUP_TYPES + ':' + group_type_name
        # check derived_from
        self.check_derived_from('group', group_type_name, group_type)
        # check version
        # check metadata
        # check description
        # check attributes
        self.iterate_over_map(self.check_attribute_definition, group_type, syntax.ATTRIBUTES, context_error_message)
        # check properties
        self.iterate_over_map(self.check_property_definition, group_type, syntax.PROPERTIES, context_error_message)
        # check members
        self.check_array_of_types(group_type_name, group_type, syntax.MEMBERS, 'node', syntax.GROUP_TYPES)
        # check requirements
        for name, definition in syntax.get_dict(group_type, syntax.REQUIREMENTS).items():
            self.check_requirement_definition(name, definition, context_error_message + ':' + syntax.REQUIREMENTS)
        # check capabilities
        self.iterate_over_map(self.check_capability_definition, group_type, syntax.CAPABILITIES, context_error_message)
        # check interfaces
        self.iterate_over_map(self.check_interface_definition, group_type, syntax.INTERFACES, context_error_message)

    def check_policy_type(self, policy_type_name, policy_type, context_error_message):
        context_error_message = syntax.POLICY_TYPES + ':' + policy_type_name
        # check derived_from
        self.check_derived_from('policy', policy_type_name, policy_type)
        # check version
        # check metadata
        # check properties
        self.iterate_over_map(self.check_property_definition, policy_type, syntax.PROPERTIES, context_error_message)
        # check targets
        self.check_array_of_types(policy_type_name, policy_type, syntax.TARGETS, ['node', 'group'], syntax.POLICY_TYPES)
        # check triggers
        # TODO

    def check_topology_template(self, topology_template):
        pass # TODO
