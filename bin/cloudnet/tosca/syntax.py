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

from cloudnet.tosca.processors import Checker
from cloudnet.tosca.utils import normalize_dict

import cloudnet.tosca.configuration as configuration
SYNTAX='Syntax'
TOSCA_DEFINITIONS_VERSION = 'tosca_definitions_version'
DEFAULT_TOSCA_DEFINITIONS_VERSION='default_tosca_definitions_version'
configuration.DEFAULT_CONFIGURATION[SYNTAX] = {
    TOSCA_DEFINITIONS_VERSION: {},
    DEFAULT_TOSCA_DEFINITIONS_VERSION: 'tosca_simple_yaml_1_2',
}

import os
profiles_directory = 'file:' + os.path.dirname(__file__) + '/profiles'

mappings = configuration.DEFAULT_CONFIGURATION[SYNTAX][TOSCA_DEFINITIONS_VERSION]
for tosca_definitions_version in [
        'tosca_simple_yaml_1_0',
        'tosca_simple_yaml_1_1',
        'tosca_simple_yaml_1_2',
        'tosca_simple_yaml_1_3',
        'alien_dsl_1_2_0',
        'alien_dsl_1_4_0',
        'alien_dsl_2_0_0']:
    mappings[tosca_definitions_version] = profiles_directory + '/' + tosca_definitions_version + '/schema.yaml'

configuration.DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

#
# TOSCA YAML keywords.
#
# TODO: sort following keywords


ATTRIBUTES = 'attributes'
IMPORTS = 'imports'
ARTIFACT_TYPES = 'artifact_types'
ARTIFACTS = 'artifacts'
DATA_TYPES = 'data_types'
DESCRIPTION = 'description'
CAPABILITY_TYPES = 'capability_types'
CAPABILITIES = 'capabilities'
INTERFACE_TYPES = 'interface_types'
INTERFACES = 'interfaces'
REQUIREMENT_TYPES = 'requirement_types'
REQUIREMENTS = 'requirements'
RELATIONSHIP_TYPES = 'relationship_types'
NODE_TYPES = 'node_types'
NODE_TEMPLATES = 'node_templates'
RELATIONSHIP_TEMPLATES = 'relationship_templates'
GROUP_TYPES = 'group_types'
MEMBERS = 'members'
GROUPS = 'groups'
POLICY_TYPES = 'policy_types'
POLICIES = 'policies'
TARGETS = 'targets'

ENTRY_SCHEMA = 'entry_schema'
EXTERNAL_SCHEMA = 'external_schema'
FILE = 'file'
IMPLEMENTATION = 'implementation'
INPUTS = 'inputs'
TYPE = 'type'
VALUE = 'value'
REQUIRED = 'required'
DEFAULT = 'default'
STATUS = 'status'

OCCURRENCES = 'occurrences'

PROPERTIES = 'properties'

DERIVED_FROM = 'derived_from'

UNBOUNDED = 'UNBOUNDED'

MIME_TYPE = 'mime_type'
FILE_EXT = 'file_ext'

CONSTRAINTS = 'constraints'

SUBSTITUTION_MAPPINGS = 'substitution_mappings'
NODE_TYPE = 'node_type'

METADATA = 'metadata'

TOPOLOGY_TEMPLATE = 'topology_template'

CAPABILITY = 'capability'
RELATIONSHIP ='relationship'

NODE = 'node'
NODE_FILTER = 'node_filter'

GET_INPUT = 'get_input'
GET_ARTIFACT = 'get_artifact'
GET_ATTRIBUTE = 'get_attribute'
GET_PROPERTY = 'get_property'

OUTPUTS = 'outputs'

VALID_TARGET_TYPES='valid_target_types'
VALID_SOURCE_TYPES='valid_source_types'

REPOSITORIES = 'repositories'
REPOSITORY = 'repository'
URL = 'url'

NAMESPACE_PREFIX = 'namespace_prefix'

#
# Getter functions.
#

def get_list(yaml, keyword):
    result = yaml.get(keyword)
    if result == None:
        return []
    type_result = type(result)
    if type_result == list:
        return result
    else:
        raise ValueError('YAML list expected')

def get_dict(yaml, keyword):
    if type(yaml) != dict:
        return {}
    result = yaml.get(keyword)
    if result == None:
        return {}
    type_result = type(result)
    if type_result == dict:
        return result
    elif type_result == list:
        return normalize_dict(result)
    else:
        raise ValueError('YAML map expected')

def get_repositories(yaml):
    return get_dict(yaml, REPOSITORIES)

def get_repository_url(yaml):
    if type(yaml) == str:
        return yaml
    if type(yaml) == dict:
        return yaml.get(URL)
    return None

def get_imports(yaml):
    return get_list(yaml, IMPORTS)

def get_import_file(yaml):
    if type(yaml) == str:
        return yaml
    if type(yaml) == dict:
        file = yaml.get(FILE)
        if file != None:
            return file
        if len(yaml) == 1:
            for key, value in yaml.items():
                if type(value) == str:
                    return value
                if type(value) == dict:
                    return value.get(FILE)
    return None

def get_import_repository(yaml):
    if type(yaml) == str:
        return None
    if type(yaml) == dict:
        repository = yaml.get(REPOSITORY)
        if repository != None:
            return repository
        if len(yaml) == 1:
            for key, value in yaml.items():
                if type(value) == str:
                    return None
                if type(value) == dict:
                    return value.get(REPOSITORY)
    return None

def get_import_namespace_prefix(yaml):
    if type(yaml) == str:
        return None
    if type(yaml) == dict:
        repository = yaml.get(NAMESPACE_PREFIX)
        if repository != None:
            return repository
        if len(yaml) == 1:
            for key, value in yaml.items():
                if type(value) == str:
                    return None
                if type(value) == dict:
                    return value.get(NAMESPACE_PREFIX)
    return None

def get_data_types(yaml):
    return get_dict(yaml, DATA_TYPES)

def get_artifact_types(yaml):
    return get_dict(yaml, ARTIFACT_TYPES)

def get_capability_types(yaml):
    return get_dict(yaml, CAPABILITY_TYPES)

def get_relationship_types(yaml):
    return get_dict(yaml, RELATIONSHIP_TYPES)

def get_interface_types(yaml):
    return get_dict(yaml, INTERFACE_TYPES)

def get_node_types(yaml):
    return get_dict(yaml, NODE_TYPES)

def get_group_types(yaml):
    return get_dict(yaml, GROUP_TYPES)

def get_policy_types(yaml):
    return get_dict(yaml, POLICY_TYPES)

def get_topology_template(yaml):
    return yaml.get(TOPOLOGY_TEMPLATE)

def get_substitution_mappings(yaml):
    return yaml.get(SUBSTITUTION_MAPPINGS)

def get_substitution_mappings_requirements(yaml):
    if type(yaml) == dict:
        requirements = yaml.get(REQUIREMENTS)
        if type(requirements) == dict:
            return requirements
        if type(requirements) == list:
            result = {}
            for requirement in requirements:
                for k, v in requirement.items():
                    result[k] = v
            return result
    return {}

def get_node_type(yaml):
    return yaml.get(NODE_TYPE)

def get_capabilities(yaml):
    return get_dict(yaml, CAPABILITIES)

def get_node_templates(yaml):
    return get_dict(yaml, NODE_TEMPLATES)

def get_type(yaml):
    yaml_type = type(yaml)
    if yaml_type == str:
        return yaml
    if yaml_type == dict:
        return yaml.get(TYPE)
    return None

def get_derived_from(yaml):
    if type(yaml) == dict:
        return yaml.get(DERIVED_FROM)
    return None

def get_requirements_list(yaml):
    return get_list(yaml, REQUIREMENTS)

def get_requirements_dict(yaml):
    return get_dict(yaml, REQUIREMENTS)

def get_property_type(yaml):
    if type(yaml) == dict:
        return yaml.get(TYPE, 'string')
    return 'string'

def get_property_default(yaml):
    if type(yaml) == dict:
        return yaml.get(DEFAULT)
    return None

def is_property_required(yaml):
    if type(yaml) == dict:
        return yaml.get(REQUIRED, True)
    return True

def get_default(yaml):
    if type(yaml) == dict:
        return yaml.get(DEFAULT)
    return None

def get_entry_schema(yaml):
    if type(yaml) == dict:
      return yaml.get(ENTRY_SCHEMA)
    return None

def get_entry_schema_type(yaml):
    entry_schema = yaml.get(ENTRY_SCHEMA)
    if type(entry_schema) == dict:
        return entry_schema.get(TYPE)
    elif type(entry_schema) == str:
        return entry_schema
    return 'string'

def get_capability_type(capability_yaml):
    type_capability_yaml = type(capability_yaml)
    if type_capability_yaml == str:
        return capability_yaml
    elif type_capability_yaml == dict:
        return capability_yaml.get(TYPE)
    else:
        raise ValueError('invalid value for ' + str(capability_yaml))

def get_capability_occurrences(capability_yaml):
    type_capability_yaml = type(capability_yaml)
    if type_capability_yaml == dict:
        return capability_yaml.get(OCCURRENCES, [1, UNBOUNDED])
    elif type_capability_yaml == str:
        return [1, UNBOUNDED]
    else:
        raise ValueError('invalid value for ' + str(capability_yaml))

# ACK for Alien4Cloud
def get_type_requirement(yaml, name):
    if type(yaml) == dict:
        return yaml.get('type_requirement', name)
    return name

def get_requirement_capability(requirement_yaml):
    type_requirement_yaml = type(requirement_yaml)
    if type_requirement_yaml == str:
        return requirement_yaml
    elif type_requirement_yaml == dict:
        capability = requirement_yaml.get(CAPABILITY)
        # ACK for Alien4Cloud
        if capability == None:
            capability = requirement_yaml.get(TYPE)
        return capability
    return None

def get_requirement_node_type(requirement_yaml):
    type_requirement_yaml = type(requirement_yaml)
    if type_requirement_yaml == str:
        return None
    elif type_requirement_yaml == dict:
        return requirement_yaml.get(NODE)
    else:
        return None

def get_requirement_node_template(requirement_yaml):
    type_requirement_yaml = type(requirement_yaml)
    if type_requirement_yaml == str:
        return requirement_yaml
    elif type_requirement_yaml == dict:
        return requirement_yaml.get(NODE)
    else:
        return None

def get_requirement_node_filter(requirement_yaml):
    type_requirement_yaml = type(requirement_yaml)
    if type_requirement_yaml == str:
        return None
    elif type_requirement_yaml == dict:
        return requirement_yaml.get(NODE_FILTER)
    return None

def get_requirement_relationship(requirement_yaml):
    if type(requirement_yaml) == dict:
        return requirement_yaml.get(RELATIONSHIP)
    return None

def get_relationship_type(relationship_yaml):
    type_relationship_yaml = type(relationship_yaml)
    if type_relationship_yaml == str:
        return relationship_yaml
    elif type_relationship_yaml == dict:
        return relationship_yaml.get(TYPE)
    return None

def get_relationship_interfaces(relationship_yaml):
    type_relationship_yaml = type(relationship_yaml)
    if type_relationship_yaml == str:
        return None
    elif type_relationship_yaml == dict:
        return relationship_yaml.get(INTERFACES)
    return None

def get_requirement_occurrences(requirement_yaml):
    if type(requirement_yaml) == dict:
        return requirement_yaml.get(OCCURRENCES, [1, 1])
    return [1, 1]

def get_inputs(yaml):
    if type(yaml) == dict:
        return yaml.get(INPUTS)
    return None

def get_input_type(yaml):
    if type(yaml) == dict:
        return yaml.get(TYPE, 'string')
    return 'string'

def get_input_description(yaml):
    if type(yaml) == dict:
        return yaml.get(DESCRIPTION)
    return None

def get_input_value(yaml):
    if type(yaml) == dict:
        return yaml.get(VALUE)
    return yaml

def get_input_default(yaml):
    if type(yaml) == dict:
        return yaml.get(DEFAULT)
    return None

def get_input_status(yaml):
    if type(yaml) == dict:
        return yaml.get(STATUS, 'supported')
    return 'supported'

def get_input_external_schema(yaml):
    if type(yaml) == dict:
        return yaml.get(EXTERNAL_SCHEMA)
    return None

def get_input_metadata(yaml):
    if type(yaml) == dict:
        return yaml.get(METADATA)
    return None

def get_constraints(yaml):
    if type(yaml) == dict:
        return yaml.get(CONSTRAINTS)
    return None

def get_occurrences(yaml):
    if type(yaml) == dict:
        return yaml.get(OCCURRENCES)
    return None

def get_artifact_file(yaml):
    if type(yaml) == dict:
        return yaml.get(FILE)
    elif type(yaml) == str:
        return yaml
    return None

def get_artifact_type(yaml):
    if type(yaml) == dict:
        return yaml.get(TYPE)
    return None

class SyntaxChecker(Checker):
    '''
        TOSCA syntax checker
    '''
    def check(self):
        self.info('TOSCA syntax checking')

        default_tosca_definitions_version = self.configuration.get(SYNTAX, DEFAULT_TOSCA_DEFINITIONS_VERSION)

        template_yaml = self.tosca_service_template.get_yaml()
        if type(template_yaml) != dict:
            self.error(' invalid YAML file as a map is expected')
            return False

        tosca_definitions_version = template_yaml.get(TOSCA_DEFINITIONS_VERSION)
        if tosca_definitions_version == None:
            self.error('tosca_definitions_version undefined')
        elif type(tosca_definitions_version) != str:
            self.error('tosca_definitions_version: string expected')
            tosca_definitions_version = None
        if tosca_definitions_version == None:
            self.warning('tosca_definitions_version: ' + default_tosca_definitions_version + ' used instead of')
            tosca_definitions_version = default_tosca_definitions_version
            template_yaml[TOSCA_DEFINITIONS_VERSION] = tosca_definitions_version

        # Load the schema.
        tosca_definitions_version_map = self.configuration.get(SYNTAX, TOSCA_DEFINITIONS_VERSION)
        schema_file = self.get_mapping(tosca_definitions_version, tosca_definitions_version_map)
        if schema_file == None:
            self.error('tosca_definitions_version: ' + tosca_definitions_version + ' unsupported')
            if tosca_definitions_version.startswith('cloudify_dsl'):
                return False
            self.warning('tosca_definitions_version: ' + default_tosca_definitions_version + ' used instead of')
            schema_file = self.get_mapping(default_tosca_definitions_version, tosca_definitions_version_map)
        tosca_schema = self.tosca_service_template.imports(schema_file).get_yaml()

        # Validate the TOSCA template against the schema.

        is_validated = True

        import jsonschema

#        jsonschema.validate(
#            instance=template_yaml,
#            schema=tosca_schema,
#            format_checker=jsonschema.draft4_format_checker) # TODO use draft7_format_checker

        validator = jsonschema.Draft4Validator(tosca_schema,
                                               format_checker=jsonschema.draft4_format_checker) # TODO use draft7_format_checker
        errors = validator.iter_errors(template_yaml)

        # Log all errors.
        for error in errors:
            error_message = error.message
            if error_message.startswith('Additional'):
                error_message = error_message[error_message.find('(')+1:-1]
            elif error_message.startswith("None is not of type 'object'"):
                error_message = 'can not be empty'
            elif error_message.endswith(" is not of type 'object'"):
                value = error_message[: error_message.index(" is not of type 'object'")]
                error_message = value + ' was unexpected'
            error_path = ''
            for value in error.path:
                if type(value) is int:
                    error_path = error_path[:-1] + '[' + str(value) + ']:'
                else:
                    error_path += str(value) + ':'
            self.error(error_path + ' ' + error_message)
            is_validated = False

        return is_validated
