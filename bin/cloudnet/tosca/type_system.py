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
import datetime
import re

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
        self.data_types = {
            # YAML types
            'string': {},
            'integer': {},
            'float': {},
            'boolean': {},
            'timestamp': {},
            'null': {},
            # TOSCA types
            'version': {},
            'range': {},
            'list': {},
            'map': {},
            'scalar-unit.size': {},
            'scalar-unit.time': {},
            'scalar-unit.frequency': {}
        }
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
#TBR            LOGGER.error(CRED + type_name + ' unknown!' + CEND)
            return dict()

        requirements = result.get(syntax.REQUIREMENTS)
        if requirements:
            result[syntax.REQUIREMENTS] = normalize_dict(requirements)

        derived_from = result.get(syntax.DERIVED_FROM)
        if derived_from == None or self.is_derived_from(derived_from, type_name):
            result = deepcopy(result)
            requirements = result.get(syntax.REQUIREMENTS)
            if requirements:
                result[syntax.REQUIREMENTS] = normalize_dict(requirements)
        else:
#TBR            if not self.is_yaml_type(derived_from):
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

# TOSCA scalar units.

SCALAR_SIZE_UNITS = {
    'B'  : 1,             # byte
    'kB' : 1000,          # kilobyte
    'KiB': 1024,          # kibibyte
    'MB' : 1000000,       # megabyte
    'MiB': 1048576,       # mebibyte
    'GB' : 1000000000,    # gigabyte
    'GiB': 1073741824,    # gibibyte
    'TB' : 1000000000000, # terabyte
    'TiB': 1099511627776, # tebibyte
}

SCALAR_TIME_UNITS = {
    'd': 86400,   # day
    'h': 3600,    # hour
    'm': 60,      # minute
    's': 1,       # second
    'ms': 10**-3, # millisecond
    'us': 10**-6, # microsecond
    'ns': 10**-9, # nanosecond
}

SCALAR_FREQUENCY_UNITS = {
    'Hz':  1,     # Hertz
    'kHz': 10**3, # Kilohertz
    'MHz': 10**6, # Megahertz
    'GHz': 10**9, # Gigahertz
}

def array_to_string_with_or_separator(a_list):
    return str(a_list).replace("['", '').replace("']", '').replace("', '", ' or ')

def split_scalar_unit(a_string, units):
    match = re.fullmatch('^([0-9]+(\.[0-9]+)?)( )*([A-Za-z]+)$', a_string)
    if match == None:
        raise ValueError('<scalar> <unit> expected instead of ' + a_string)
    values = [ match.group(1), match.group(4) ]
    try:
        scalar = float(values[0])
    except ValueError:
        raise ValueError('<scalar> expected instead of ' + values[0])
    if scalar < 0:
        raise ValueError('positive <scalar> expected instead of ' + str(scalar))
    unit = values[1]
    if units.get(unit) == None:
        raise ValueError(array_to_string_with_or_separator(list(units.keys())) + ' expected instead of ' + unit)
    return scalar, unit

def check_scalar_unit(a_string, units):
    scalar, unit = split_scalar_unit(a_string, units)
    return True

def normalize_scalar_unit(a_string, units):
    scalar, unit = split_scalar_unit(a_string, units)
    return scalar * units.get(unit)

class AbstractTypeChecker(object):
    def __init__(self, type_name):
        self.type_name = type_name

    def check_type(self, value, processor, context_error_message):
        raise NotImplementedError()

class BasicTypeChecker(AbstractTypeChecker):
    def __init__(self, type_name, lambda_expression):
        AbstractTypeChecker.__init__(self, type_name)
        self.lambda_expression = lambda_expression

    def check_type(self, value, processor, context_error_message):
        try:
            if not self.lambda_expression(value):
                processor.error(context_error_message + ': ' + str(value) + ' - ' + self.type_name + ' expected')
                return False
        except ValueError as exc:
            processor.error(context_error_message + ': ' + str(value) + ' - ' + str(exc))
            return False
        return True

class ListTypeChecker(AbstractTypeChecker):
    def __init__(self, type_checker, item_type_checker):
        AbstractTypeChecker.__init__(self, type_checker.type_name)
        self.type_checker = type_checker
        self.item_type_checker = item_type_checker

    def check_type(self, the_list, processor, context_error_message):
        if self.type_checker.check_type(the_list, processor, context_error_message):
            idx = 0
            result = True
            for item in the_list:
                if not self.item_type_checker.check_type(item, processor, context_error_message + '[' + str(idx) + ']'):
                    result = False
                idx += 1
            return result
        return False

class MapTypeChecker(AbstractTypeChecker):
    def __init__(self, type_checker, value_type_checker):
        AbstractTypeChecker.__init__(self, type_checker.type_name)
        self.type_checker = type_checker
        self.value_type_checker = value_type_checker

    def check_type(self, the_map, processor, context_error_message):
        if self.type_checker.check_type(the_map, processor, context_error_message):
            result = True
            for key, value in the_map.items():
                if not self.value_type_checker.check_type(value, processor, context_error_message + ':' + str(key)):
                    result = False
            return result
        return False

BASIC_TYPE_CHECKERS = {
    # YAML types
    'string': BasicTypeChecker('string', lambda value : type(value) == str),
    'integer': BasicTypeChecker('integer', lambda value : type(value) == int),
    'float': BasicTypeChecker('float', lambda value : type(value) in [int, float]),
    'boolean': BasicTypeChecker('boolean', lambda value : type(value) == bool),
    'timestamp': BasicTypeChecker('timestamp', lambda value : type(value) == datetime.datetime),
    'null': BasicTypeChecker('null', lambda value : value == None),
    # TOSCA types
    'version': BasicTypeChecker('version', lambda value : type(value) in [float, str]),
    'range': BasicTypeChecker('range', lambda value : type(value) == list and len(value) == 2 and type(value[0]) == int and type(value[1]) == int),
    'list': BasicTypeChecker('list', lambda value : type(value) == list),
    'map': BasicTypeChecker('map', lambda value : type(value) == dict),
    'scalar-unit.size': BasicTypeChecker('scalar-unit.size', lambda value : type(value) == str and check_scalar_unit(value, SCALAR_SIZE_UNITS)),
    'scalar-unit.time': BasicTypeChecker('scalar-unit.time', lambda value : type(value) == str and check_scalar_unit(value, SCALAR_TIME_UNITS)),
    'scalar-unit.frequency': BasicTypeChecker('scalar-unit.time', lambda value : type(value) == str and check_scalar_unit(value, SCALAR_FREQUENCY_UNITS)),
}

class ConstraintClauseChecker(object):
    def __init__(self, constraint_name, check_value, check_constraint_operand = lambda value, type_checker : True):
        self.constraint_name = constraint_name
        self.check_value = check_value
        self.check_constraint_operand = check_constraint_operand

    def check_operand(self, value, type_checker):
        return self.check_constraint_operand(value, type_checker)

    def check_constraint(self, v1, v2, processor, context_error_message):
        return self.check_value(v1, v2)

CONSTRAINT_EQUAL = lambda v1, v2: v1 == v2
CONSTRAINT_GREATER_THAN = lambda v1, v2: v1 > v2
CONSTRAINT_GREATER_OR_EQUAL = lambda v1, v2: v1 >= v2
CONSTRAINT_LESS_THAN = lambda v1, v2: v1 < v2
CONSTRAINT_LESS_OR_EQUAL = lambda v1, v2: v1 <= v2
CONSTRAINT_IN_RANGE = lambda v1, v2: v1 >= v2[0] and v1 <= v2[1]
CONSTRAINT_VALID_VALUES = lambda v1, v2: v1 in v2
CONSTRAINT_LENGTH = lambda v1, v2: len(v1) == v2
CONSTRAINT_MIN_LENGTH = lambda v1, v2: len(v1) >= v2
CONSTRAINT_MAX_LENGTH = lambda v1, v2: len(v1) <= v2

def in_range_scalar_unit(v1, v2, units):
    v = normalize_scalar_unit(v1, units)
    return v >= normalize_scalar_unit(v2[0], units) and v <= normalize_scalar_unit(v2[1], units)

type_check_operand = lambda operand, type_checker : type_checker(operand)
type_check_in_range_operand = lambda operand, type_checker : type(operand) == list and len(operand) == 2 and type_checker(operand[0]) and type_checker(operand[1])
type_check_in_range_range_operand = lambda operand, type_checker : type(operand) == list and len(operand) == 2 and type_checker(operand)

BASIC_CONSTRAINT_CLAUSES = {
    'equal': {
        'string': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'integer': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'float': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'boolean': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'timestamp': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'null': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'version': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'range': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'list': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'map': ConstraintClauseChecker('equal', CONSTRAINT_EQUAL, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS) == normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS) == normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS) == normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand),
    },
    'greater_than': {
        'string': ConstraintClauseChecker('greater_than', CONSTRAINT_GREATER_THAN, type_check_operand),
        'integer': ConstraintClauseChecker('greater_than', CONSTRAINT_GREATER_THAN, type_check_operand),
        'float': ConstraintClauseChecker('greater_than', CONSTRAINT_GREATER_THAN, type_check_operand),
        'timestamp': ConstraintClauseChecker('greater_than', CONSTRAINT_GREATER_THAN, type_check_operand),
        'version': ConstraintClauseChecker('greater_than', CONSTRAINT_GREATER_THAN, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('greater_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS) > normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('greater_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS) > normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('greater_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS) > normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand),
    },
    'greater_or_equal': {
        'string': ConstraintClauseChecker('greater_or_equal', CONSTRAINT_GREATER_OR_EQUAL, type_check_operand),
        'integer': ConstraintClauseChecker('greater_or_equal', CONSTRAINT_GREATER_OR_EQUAL, type_check_operand),
        'float': ConstraintClauseChecker('greater_or_equal', CONSTRAINT_GREATER_OR_EQUAL, type_check_operand),
        'timestamp': ConstraintClauseChecker('greater_or_equal', CONSTRAINT_GREATER_OR_EQUAL, type_check_operand),
        'version': ConstraintClauseChecker('greater_or_equal', CONSTRAINT_GREATER_OR_EQUAL, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('greater_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS) >= normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('greater_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS) >= normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('greater_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS) >= normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand),
    },
    'less_than': {
        'string': ConstraintClauseChecker('less_than', CONSTRAINT_LESS_THAN, type_check_operand),
        'integer': ConstraintClauseChecker('less_than', CONSTRAINT_LESS_THAN, type_check_operand),
        'float': ConstraintClauseChecker('less_than', CONSTRAINT_LESS_THAN, type_check_operand),
        'timestamp': ConstraintClauseChecker('less_than', CONSTRAINT_LESS_THAN, type_check_operand),
        'version': ConstraintClauseChecker('less_than', CONSTRAINT_LESS_THAN, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('less_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS) < normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('less_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS) < normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('less_than',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS) < normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand),
    },
    'less_or_equal': {
        'string': ConstraintClauseChecker('less_or_equal', CONSTRAINT_LESS_OR_EQUAL, type_check_operand),
        'integer': ConstraintClauseChecker('less_or_equal', CONSTRAINT_LESS_OR_EQUAL, type_check_operand),
        'float': ConstraintClauseChecker('less_or_equal', CONSTRAINT_LESS_OR_EQUAL, type_check_operand),
        'timestamp': ConstraintClauseChecker('less_or_equal', CONSTRAINT_LESS_OR_EQUAL, type_check_operand),
        'version': ConstraintClauseChecker('less_or_equal', CONSTRAINT_LESS_OR_EQUAL, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('less_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS) <= normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('less_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS) <= normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('less_or_equal',
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS) <= normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand),
    },
    'in_range': {
        'string': ConstraintClauseChecker('in_range', CONSTRAINT_IN_RANGE, type_check_in_range_operand),
        'integer': ConstraintClauseChecker('in_range', CONSTRAINT_IN_RANGE, type_check_in_range_operand),
        'float': ConstraintClauseChecker('in_range', CONSTRAINT_IN_RANGE, type_check_in_range_operand),
        'timestamp': ConstraintClauseChecker('in_range', CONSTRAINT_IN_RANGE, type_check_in_range_operand),
        'version': ConstraintClauseChecker('in_range', CONSTRAINT_IN_RANGE, type_check_in_range_operand),
        'range': ConstraintClauseChecker('in_range',
            lambda v1, v2: v1[0] >= v2[0] and v1[1] <= v2[1],
            type_check_in_range_range_operand),
        'scalar-unit.size': ConstraintClauseChecker('in_range',
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_SIZE_UNITS),
            type_check_in_range_operand),
        'scalar-unit.time': ConstraintClauseChecker('in_range',
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_TIME_UNITS),
            type_check_in_range_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('in_range',
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_FREQUENCY_UNITS),
            type_check_in_range_operand),
    },
    'valid_values': {
        'string': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'integer': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'float': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'boolean': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'timestamp': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'null': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'version': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'range': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'list': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'map': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'scalar-unit.size': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'scalar-unit.time': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
        'scalar-unit.frequency': ConstraintClauseChecker('valid_values', CONSTRAINT_VALID_VALUES, type_check_operand),
    },
    'length': {
        'string': ConstraintClauseChecker('length', CONSTRAINT_LENGTH),
        'list': ConstraintClauseChecker('length', CONSTRAINT_LENGTH),
        'map': ConstraintClauseChecker('length', CONSTRAINT_LENGTH),
    },
    'min_length': {
        'string': ConstraintClauseChecker('min_length', CONSTRAINT_MIN_LENGTH),
        'list': ConstraintClauseChecker('min_length', CONSTRAINT_MIN_LENGTH),
        'map': ConstraintClauseChecker('min_length', CONSTRAINT_MIN_LENGTH),
    },
    'max_length': {
        'string': ConstraintClauseChecker('max_length', CONSTRAINT_MAX_LENGTH),
        'list': ConstraintClauseChecker('max_length', CONSTRAINT_MAX_LENGTH),
        'map': ConstraintClauseChecker('max_length', CONSTRAINT_MAX_LENGTH),
    },
    'pattern': {
        'string': ConstraintClauseChecker('pattern', lambda v1, v2: re.fullmatch(v2, v1) != None),
    },
    'schema': {
        'string': ConstraintClauseChecker('schema', lambda v1, v2: True), # TODO
    },
}

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
                # It seems that we get a program crash here but I didn't figure out
                # how to deal with yet !
                # This case occurs when a file imported is not present
                # JLC 20201126
                self.error('imports[' + str(index) + ']:file: ' + import_filepath + ' - file not found')
            index = index + 1

        # Put all types of the loaded template into the type system.
        for type_kind in [syntax.ARTIFACT_TYPES, syntax.DATA_TYPES, syntax.INTERFACE_TYPES, syntax.CAPABILITY_TYPES, syntax.REQUIREMENT_TYPES, syntax.RELATIONSHIP_TYPES, syntax.NODE_TYPES, syntax.GROUP_TYPES, syntax.POLICY_TYPES]:
            # Iterate over types.
            for (type_name, type_yaml) in template_yaml.get(type_kind, {}).items():
                full_type_name = namescape_prefix + type_name
                # check that this type is not already defined
                if self.type_system.types.get(full_type_name):
                    self.error(type_kind + ':' + type_name + ' - type already defined')
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

    def check_type_existence(self, type_kinds, type_name, context_error_message):
        if type_name == None:
            return False
        type_name = self.type_system.get_type_uri(type_name)
        if type(type_kinds) == str:
            type_kinds = [ type_kinds ]
        for type_kind in type_kinds:
            if getattr(self.type_system, type_kind + '_types').get(type_name) != None:
                return True
        if self.type_system.types.get(type_name) == None:
            self.error(context_error_message + ': ' + type_name + ' - undefined type but ' + array_to_string_with_or_separator(type_kinds) + ' type required')
        else:
            self.error(context_error_message + ': ' + type_name + ' - defined type but ' + array_to_string_with_or_separator(type_kinds) + ' type required')
        return False

    def check_type(self, type_kinds, the_type, previous_type, context_error_message):
        if self.check_type_existence(type_kinds, the_type, context_error_message):
            # check that the_type is compatible with previous type definition
            if previous_type != None:
                LOGGER.debug(context_error_message + ': ' + the_type + ' - overload ' + previous_type)
                if not self.type_system.is_derived_from(the_type, previous_type):
                    self.error(context_error_message + ': ' + the_type + ' - incompatible with previous declared type ' + previous_type)
                    return False
            return True
        return False

    def check_type_in_definition(self, type_kinds, keyword, definition, previous_definition, context_error_message):
        return self.check_type(type_kinds, definition.get(keyword), previous_definition.get(keyword), context_error_message + ':' + keyword)

    def check_types_in_definition(self, type_kinds, keyword, definition, previous_definition, context_error_message, additional_check = None):
        previous_types = previous_definition.get(keyword)
        idx = 0
        for value in definition.get(keyword, []):
            cem = context_error_message + ':' + keyword + '[' + str(idx) + ']'
            if self.check_type_existence(type_kinds, value, cem):
                if previous_types:
                    # check that value is compatible with previous types
                    not_compatible_with_previous_types = True
                    for previous_type in previous_types:
                        if self.type_system.is_derived_from(value, previous_type):
                            not_compatible_with_previous_types = False
                            break
                    if not_compatible_with_previous_types:
                        self.error(cem + ': ' + value + ' - incompatible with ' + array_to_string_with_or_separator(previous_types))
                if additional_check:
                    additional_check(value, cem + ': ')
            idx = idx + 1

    def check_type_compatible_with_valid_source_types(self, type_name, valid_source_types):
        if valid_source_types is None or len(valid_source_types) == 0:
            return True
        for valid_source_type in valid_source_types:
            if self.type_system.is_derived_from(type_name, valid_source_type):
                return True
        return False

    def iterate_over_definitions(self, method, keyword, definition1, definition2, context_error_message):
        context_error_message += ':' + keyword + ':'
        definition2_keyword = definition2.get(keyword, {})

        # Store previous_parent_definition
        try:
            previous_parent_definition = self.previous_parent_definition
        except:
            previous_parent_definition = None

        # WARNING: this a like a global variable!
        self.previous_parent_definition = definition2_keyword

        for key, value in definition1.get(keyword, {}).items():
            method(key, value, definition2_keyword.get(key, {}), context_error_message + key)

        # Restore previous_parent_definition
        self.previous_parent_definition = previous_parent_definition

    def check_service_template_definition(self, service_template_definition):
        # check tosca_definitions_version - already done
        # check namespace - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check dsl_definitions - nothing to do
        # check repositories
        for name, repository_definition in syntax.get_repositories(service_template_definition).items():
            self.check_repository_definition(name, repository_definition, syntax.REPOSITORIES)
        # check imports - already done

        def iterate_over_types(check_method, service_template_definition, keyword):
            base_context_error_message = keyword + ':'
            for type_name, type_definition in service_template_definition.get(keyword, {}).items():
                context_error_message = base_context_error_message + type_name
                # Store the current type name
                self.current_type_name = type_name
                # check derived_from
                cem = context_error_message + ':' + syntax.DERIVED_FROM
                derived_from = syntax.get_derived_from(type_definition)
                # check derived_from existence
                self.check_type_existence(keyword[:keyword.find('_')], derived_from, cem)
                # check acyclic derived_from
                if self.type_system.is_derived_from(derived_from, type_name):
                    self.error(cem + ': ' + derived_from + ' - cyclically derived from ' + type_name)
                # execute check_method
                if derived_from == None or self.type_system.get_type(derived_from) is None or self.type_system.is_derived_from(derived_from, type_name):
                    derived_from_type = {}
                else:
                    derived_from_type = self.type_system.merge_type(derived_from)
                check_method(type_name, type_definition, derived_from_type, context_error_message)

        # check artifact_types
        iterate_over_types(self.check_artifact_type, service_template_definition, syntax.ARTIFACT_TYPES)
        # check data_types
        iterate_over_types(self.check_data_type, service_template_definition, syntax.DATA_TYPES)
        # check capability_types
        iterate_over_types(self.check_capability_type, service_template_definition, syntax.CAPABILITY_TYPES)
        # check interface_types
        iterate_over_types(self.check_interface_type, service_template_definition, syntax.INTERFACE_TYPES)
        # check relationship_types
        iterate_over_types(self.check_relationship_type, service_template_definition, syntax.RELATIONSHIP_TYPES)
        # check node_types
        iterate_over_types(self.check_node_type, service_template_definition, syntax.NODE_TYPES)
        # check group_types
        iterate_over_types(self.check_group_type, service_template_definition, syntax.GROUP_TYPES)
        # check policy_types
        iterate_over_types(self.check_policy_type, service_template_definition, syntax.POLICY_TYPES)
        # check topology_template
        self.check_topology_template(syntax.get_topology_template(service_template_definition))

    def check_repository_definition(self, repository_name, repository_definition, context_error_message):
        pass # TODO

    def check_attribute_definition(self, attribute_name, attribute_definition, previous_attribute_definition, context_error_message):
        # check type
        self.check_type_in_definition('data', syntax.TYPE, attribute_definition, previous_attribute_definition, context_error_message)
        # check description - nothing to do
        # check default
        self.check_default(attribute_definition, previous_attribute_definition, context_error_message)
        # check status - nothing to do
        # check entry_schema
        self.check_entry_schema(attribute_definition, previous_attribute_definition, context_error_message)

    def check_entry_schema(self, definition, previous_definition, context_error_message):

        def get_entry_schema_type(entry_schema):
            if entry_schema == None:
                return None
            if type(entry_schema) == str:
                return entry_schema
            return entry_schema.get(syntax.TYPE)

        entry_schema = definition.get(syntax.ENTRY_SCHEMA)
        if entry_schema != None:
            definition_type = definition.get(syntax.TYPE)
            if definition_type not in ['map', 'list']:
                self.error(context_error_message + ':' + syntax.ENTRY_SCHEMA + ' - unexpected because type equals to ' + str(definition_type) + ' instead of list or map')
            self.check_type('data', get_entry_schema_type(entry_schema), get_entry_schema_type(previous_definition.get(syntax.ENTRY_SCHEMA)), context_error_message + ':' + syntax.ENTRY_SCHEMA + ':' + syntax.TYPE)

    def get_type_checker(self, definition, context_error_message):
        definition_type = definition.get(syntax.TYPE)
        if definition_type is None:
#TBR            self.error(context_error_message + ' - type expected')
            return None
        type_checker = BASIC_TYPE_CHECKERS.get(definition_type)
        if type_checker != None:
            if definition_type == 'list':
                item_type_checker = self.get_type_checker({ syntax.TYPE: syntax.get_entry_schema_type(definition) }, context_error_message)
                type_checker = ListTypeChecker(type_checker, item_type_checker)
            elif definition_type == 'map':
                value_type_checker = self.get_type_checker({ syntax.TYPE: syntax.get_entry_schema_type(definition) }, context_error_message)
                type_checker = MapTypeChecker(type_checker, value_type_checker)
        else:
            # definition_type could be a data type
            data_type = self.type_system.data_types.get(self.type_system.get_type_uri(definition_type))
            if data_type != None: # data type found
                derived_from = data_type.get(syntax.DERIVED_FROM)
                if derived_from != None and not self.type_system.is_derived_from(derived_from, definition_type):
                    type_checker = self.get_type_checker({ syntax.TYPE: derived_from }, context_error_message)

        # TBR ?
# TBR        if type_checker is None:
# TBR            self.error(context_error_message + ' - no type checker available for ' + definition_type)

        return type_checker

    def check_default(self, definition, previous_definition, context_error_message):
        default_value = definition.get(syntax.DEFAULT)
        if default_value is None:
            return

        cem = context_error_message + ':' + syntax.DEFAULT
        LOGGER.debug(cem + ' - checking...')

        type_checker = self.get_type_checker(definition, cem)
        if type_checker is None:
            return

        if not type_checker.check_type(default_value, self, cem):
            # default_value does not match type_checker
            return # don't check constraints

        def evaluate_constraints(constraint_clauses, value):
            for constraint_clause in constraint_clauses:
                for constraint_name, constraint_value in constraint_clause.items():
                    constraint_clause_checkers = BASIC_CONSTRAINT_CLAUSES.get(constraint_name)
                    if constraint_clause_checkers is None:
                        self.error(cem + ' - ' + constraint_name + ' unsupported operator')
                        continue
                    definition_type = definition.get(syntax.TYPE)
                    # TODO
                    if definition_type == 'PortDef':
                        definition_type = 'integer'
                    constraint_clause_checker = constraint_clause_checkers.get(definition_type)
                    if constraint_clause_checker is None:
                        self.error(cem + ' - ' + constraint_name + ' unallowed operator on ' + definition_type + ' value')
                        continue
                    LOGGER.debug(cem + ' - evaluate ' + constraint_name + ': ' + str(constraint_value))
                    if not constraint_clause_checker.check_constraint(value, constraint_value, self, cem):
                        self.error(cem + ': ' + str(value) + ' - ' + constraint_name + ': ' + str(constraint_value) + ' failed')

        # check that default_value respects all constraint clauses of the definition type
        data_type = self.type_system.merge_type(self.type_system.get_type_uri(definition.get(syntax.TYPE)))
        evaluate_constraints(data_type.get(syntax.CONSTRAINTS, []), default_value)

        # check that default_value respects all constraint clauses of both definition and previous_definition
        evaluate_constraints(definition.get(syntax.CONSTRAINTS, []), default_value)
        evaluate_constraints(previous_definition.get(syntax.CONSTRAINTS, []), default_value)

        LOGGER.debug(cem + ' - checked')

    def check_constraint_clauses(self, definition, type_checker, context_error_message):
        idx = -1
        for constraint_clause in definition.get(syntax.CONSTRAINTS, []):
            idx += 1
            for constraint_operator, constraint_value in constraint_clause.items():
                cem = context_error_message + ':' + syntax.CONSTRAINTS + '[' + str(idx) + ']: ' + constraint_operator
                constraint_clause_checkers = BASIC_CONSTRAINT_CLAUSES.get(constraint_operator)
                if constraint_clause_checkers is None:
                    self.error(cem + ' - unsupported operator')
                    continue

                if type_checker is None:
                    continue # no type_checker then can't check typing of the constraint

                # check that the constraint operator is valid according to the type
                constraint_clause_checker = constraint_clause_checkers.get(type_checker.type_name)
                if constraint_clause_checker is None:
                    self.error(cem + ' - unallowed operator on ' + type_checker.type_name)
                    continue

                # check that the constraint operand is valid
                if constraint_operator == 'valid_values':
                    check_constraint_operand = lambda operand : ListTypeChecker(BASIC_TYPE_CHECKERS.get('list'), type_checker).check_type(operand, self, cem)
                else:
                    check_constraint_operand = lambda operand : type_checker.check_type(operand, self, cem)
                constraint_clause_checker.check_operand(constraint_value, check_constraint_operand)

    def check_property_definition(self, property_name, property_definition, previous_property_definition, context_error_message):
        # check type
        self.check_type_in_definition('data', syntax.TYPE, property_definition, previous_property_definition, context_error_message)
        # check description - nothing to do
        # check required - nothing to do
        # check default
        self.check_default(property_definition, previous_property_definition, context_error_message)
        # check status - nothing to do
        # check constraints
        type_checker = self.get_type_checker(property_definition, context_error_message)
        self.check_constraint_clauses(property_definition, type_checker, context_error_message)
        # check entry_schema
        self.check_entry_schema(property_definition, previous_property_definition, context_error_message)
        # check external_schema # TODO
        # check metadata - nothing to do

    def check_requirement_definition(self, requirement_name, requirement_definition, previous_requirement_definition, context_error_message):
        # check description - nothing to do

        # check capability
        if self.check_type_in_definition('capability', syntax.CAPABILITY, requirement_definition, previous_requirement_definition, context_error_message):
            requirement_capability = syntax.get_requirement_capability(requirement_definition)
            valid_source_types = self.type_system.capability_types.get(requirement_capability).get(syntax.VALID_SOURCE_TYPES)
            if not self.check_type_compatible_with_valid_source_types(self.current_type_name, valid_source_types):
                self.error(context_error_message + ':capability: ' + requirement_capability + ' - ' + self.current_type_name + ' incompatible with valid source types ' + str(valid_source_types) + ' of ' + requirement_capability)
        else:
            # capability undefined or not a capability type
            requirement_capability = None

        # check node
        if self.check_type_in_definition('node', syntax.NODE, requirement_definition, previous_requirement_definition, context_error_message):
            if requirement_capability != None:
                requirement_node = syntax.get_requirement_node_type(requirement_definition)
                node_type = self.type_system.merge_type(requirement_node)
                capability_not_compatible = True
                for cap_name, cap_def in syntax.get_capabilities(node_type).items():
                    if self.type_system.is_derived_from(syntax.get_capability_type(cap_def), requirement_capability):
                        if self.check_type_compatible_with_valid_source_types(self.current_type_name, cap_def.get(syntax.VALID_SOURCE_TYPES)):
                            capability_not_compatible = False
                            break
                if capability_not_compatible:
                    self.error(context_error_message + ':' + syntax.NODE + ': ' + requirement_node + ' - no capability compatible with ' + requirement_capability)

        # check relationship
        requirement_relationship = syntax.get_requirement_relationship(requirement_definition)
        if requirement_relationship == None:
            # relationship undefined
            if requirement_capability != None:
                # Check that there is one relationship where requirement_capability is compatible with at least one valid target type
                found_relationship_types = []
                for relationship_type_name in list(self.type_system.relationship_types):
                    relationship_type = self.type_system.merge_type(relationship_type_name)
                    for valid_target_type in relationship_type.get(syntax.VALID_TARGET_TYPES, []):
                        if self.type_system.is_derived_from(requirement_capability, valid_target_type):
                            found_relationship_types.append(relationship_type_name)
                            break
                nb_found_relationship_types = len(found_relationship_types)
                if nb_found_relationship_types == 0:
                    self.error(context_error_message + ':relationship undefined but no relationship type is compatible with ' + requirement_capability)
                elif nb_found_relationship_types == 1:
                    self.warning(context_error_message + ':relationship undefined but ' + found_relationship_types[0] + ' is compatible with ' + requirement_capability)
                else:
                    self.warning(context_error_message + ':relationship undefined but ' + array_to_string_with_or_separator(found_relationship_types) + ' are compatible with ' + requirement_capability)
        else:
            # relationship defined
            if self.check_type_in_definition('relationship', syntax.RELATIONSHIP, requirement_definition, previous_requirement_definition, context_error_message):
                if requirement_capability != None:
                    # Check that requirement_capability is compatible with at least one requirement_relationship valid target type
                    relationship_type = self.type_system.merge_type(requirement_relationship)
                    capability_not_compatible = True
                    for valid_target_type in relationship_type.get(syntax.VALID_TARGET_TYPES, []):
                        if self.type_system.is_derived_from(requirement_capability, valid_target_type):
                            capability_not_compatible = False
                            break
                    if capability_not_compatible:
                        self.error(context_error_message + ':' + syntax.RELATIONSHIP + ': ' + requirement_relationship + ' - no valid target type compatible with ' + requirement_capability)

                    # check relationship interfaces
                    # TODO check_interface_definition

        # check occurrences
        self.check_occurrences(requirement_definition, self.previous_parent_definition.get(requirement_name), [1, 1], context_error_message)

    def check_occurrences(self, definition, previous_definition, default_occurrences, context_error_message):
        occurrences = definition.get(syntax.OCCURRENCES)
        if occurrences == None:
            return

        # check lower and upper occurrences
        if occurrences[1] != syntax.UNBOUNDED and occurrences[1] < occurrences[0]:
            self.error(context_error_message + ':' + syntax.OCCURRENCES + ': ' + str(occurrences) + ' - lower occurrence can not be greater than upper occurrence')

        if previous_definition != None:
            previous_occurrences = previous_definition.get(syntax.OCCURRENCES, default_occurrences)
            # check lower occurrence
            if occurrences[0] < previous_occurrences[0]:
                self.error(context_error_message + ':' + syntax.OCCURRENCES + ': ' + str(occurrences) + ' - lower occurrence can not be less than ' + str(previous_occurrences[0]))
            # check upper occurrence
            if previous_occurrences[1] != syntax.UNBOUNDED:
                # then upper previous occurrence is a positive integer
                if occurrences[1] == syntax.UNBOUNDED or occurrences[1] > previous_occurrences[1]:
                    self.error(context_error_message + ':' + syntax.OCCURRENCES + ': ' + str(occurrences) + ' - upper occurrence can not be greater than ' + str(previous_occurrences[1]))

    def check_capability_definition(self, capability_name, capability_definition, previous_capability_definition, context_error_message):
        # check description - nothing to do

        # Normalize capability_definition and previous_capability_definition
        if type(capability_definition) == str:
            capability_definition = { syntax.TYPE: capability_definition }
        if type(previous_capability_definition) == str:
            previous_capability_definition = { syntax.TYPE: previous_capability_definition }

        # check type
        if self.check_type_in_definition('capability', syntax.TYPE, capability_definition, previous_capability_definition, context_error_message):
            capability_type = syntax.get_capability_type(capability_definition)
        else:
            capability_type = None

        # check properties # TODO add tests
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, capability_definition, previous_capability_definition, context_error_message)
        # check attributes # TODO add tests
        self.iterate_over_definitions(self.check_attribute_definition, syntax.ATTRIBUTES, capability_definition, previous_capability_definition, context_error_message)

        # check valid_source_types
        if capability_type != None:
            def check_valid_source_type(valid_source_type, context_error_message):
                node_type = self.type_system.merge_type(valid_source_type)
                # check each valid_source_type has at least a requirement with capability compatible with capability_type
                requirement_not_found = True
                for requirement_name, requirement_definition in syntax.get_requirements_dict(node_type).items():
                    if self.type_system.is_derived_from(capability_type, syntax.get_requirement_capability(requirement_definition)):
                        requirement_not_found = False
                        break
                if requirement_not_found:
                    self.error(context_error_message + valid_source_type + ' - no requirement compatible with ' + capability_type)
        else:
            check_valid_source_type = None
        self.check_types_in_definition('node', syntax.VALID_SOURCE_TYPES, capability_definition, previous_capability_definition, context_error_message, check_valid_source_type)

        # check occurrences
        self.check_occurrences(capability_definition, self.previous_parent_definition.get(capability_name), [1, syntax.UNBOUNDED], context_error_message)

    def check_interface_definition(self, interface_name, interface_definition, previous_interface_definition, context_error_message):
        # check description - nothing to do
        # check type
        self.check_type_in_definition('interface', syntax.TYPE, interface_definition, previous_interface_definition, context_error_message)
        # check inputs
        self.iterate_over_definitions(self.check_property_definition, syntax.INPUTS, interface_definition, previous_interface_definition, context_error_message)
        # check operations # TODO check_operation_definition

    def check_artifact_definition(self, artifact_name, artifact_definition, previous_artifact_definition, context_error_message):
        # check type
        self.check_type_in_definition('artifact', syntax.TYPE, artifact_definition, previous_artifact_definition, context_error_message)
        # check file # TODO
        # check repository # TODO
        # check description - nothing to do
        # check deploy_path - nothing to do
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, artifact_definition, previous_artifact_definition, context_error_message)

    def check_artifact_type(self, artifact_type_name, artifact_type, derived_from_artifact_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check mime_type - nothing to do
        # check file_ext # TODO already done previously move previous code here
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, artifact_type, derived_from_artifact_type, context_error_message)

    def check_data_type(self, data_type_name, data_type, derived_from_data_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check constraints
        type_checker = self.get_type_checker({ syntax.TYPE: data_type.get(syntax.DERIVED_FROM) }, context_error_message)
        self.check_constraint_clauses(data_type, type_checker, context_error_message)
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, data_type, derived_from_data_type, context_error_message)

    def check_capability_type(self, capability_type_name, capability_type, derived_from_capability_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, capability_type, derived_from_capability_type, context_error_message)
        # check attributes
        self.iterate_over_definitions(self.check_attribute_definition, syntax.ATTRIBUTES, capability_type, derived_from_capability_type, context_error_message)
        # check valid_source_types
        self.check_types_in_definition('node', syntax.VALID_SOURCE_TYPES, capability_type, derived_from_capability_type, context_error_message)

    def check_interface_type(self, interface_type_name, interface_type, derived_from_interface_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check inputs
        self.iterate_over_definitions(self.check_property_definition, syntax.INPUTS, interface_type, derived_from_interface_type, context_error_message)
        # check operations TODO add tests
        # TODO check_operation_definition

    def check_relationship_type(self, relationship_type_name, relationship_type, derived_from_relationship_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_definitions(self.check_attribute_definition, syntax.ATTRIBUTES, relationship_type, derived_from_relationship_type, context_error_message)
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, relationship_type, derived_from_relationship_type, context_error_message)
        # check interfaces
        self.iterate_over_definitions(self.check_interface_definition, syntax.INTERFACES, relationship_type, derived_from_relationship_type, context_error_message)
        # check valid_target_types
        self.check_types_in_definition('capability', syntax.VALID_TARGET_TYPES, relationship_type, derived_from_relationship_type, context_error_message)

    def check_node_type(self, node_type_name, node_type, derived_from_node_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_definitions(self.check_attribute_definition, syntax.ATTRIBUTES, node_type, derived_from_node_type, context_error_message)
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, node_type, derived_from_node_type, context_error_message)
        # normalize requirements
        requirements = node_type.get(syntax.REQUIREMENTS)
        if requirements != None:
            node_type[syntax.REQUIREMENTS] = syntax.get_requirements_dict(node_type)
        # check requirements
        self.iterate_over_definitions(self.check_requirement_definition, syntax.REQUIREMENTS, node_type, derived_from_node_type, context_error_message)
        # check capabilities
        self.iterate_over_definitions(self.check_capability_definition, syntax.CAPABILITIES, node_type, derived_from_node_type, context_error_message)
        # check interfaces
        self.iterate_over_definitions(self.check_interface_definition, syntax.INTERFACES, node_type, derived_from_node_type, context_error_message)
        # check artifacts
        self.iterate_over_definitions(self.check_artifact_definition, syntax.ARTIFACTS, node_type, derived_from_node_type, context_error_message)

    def check_group_type(self, group_type_name, group_type, derived_from_group_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_definitions(self.check_attribute_definition, syntax.ATTRIBUTES, group_type, derived_from_group_type, context_error_message)
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, group_type, derived_from_group_type, context_error_message)
        # check members
        self.check_types_in_definition('node', syntax.MEMBERS, group_type, derived_from_group_type, context_error_message)
        # normalize requirements
        requirements = group_type.get(syntax.REQUIREMENTS)
        if requirements != None:
            group_type[syntax.REQUIREMENTS] = syntax.get_requirements_dict(group_type)
        # check requirements
        self.iterate_over_definitions(self.check_requirement_definition, syntax.REQUIREMENTS, group_type, derived_from_group_type, context_error_message)
        # check capabilities
        self.iterate_over_definitions(self.check_capability_definition, syntax.CAPABILITIES, group_type, derived_from_group_type, context_error_message)
        # check interfaces
        self.iterate_over_definitions(self.check_interface_definition, syntax.INTERFACES, group_type, derived_from_group_type, context_error_message)

    def check_policy_type(self, policy_type_name, policy_type, derived_from_policy_type, context_error_message):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check properties
        self.iterate_over_definitions(self.check_property_definition, syntax.PROPERTIES, policy_type, derived_from_policy_type, context_error_message)
        # check targets
        self.check_types_in_definition(['node', 'group'], syntax.TARGETS, policy_type, derived_from_policy_type, context_error_message)
        # check triggers
        # TODO

    def check_topology_template(self, topology_template):
        pass # TODO
