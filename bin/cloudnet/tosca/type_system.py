######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-22 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import datetime
import logging  # for logging purposes.
import os
import re
from copy import deepcopy

import cloudnet.tosca.configuration as configuration
import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.diagnostics import diagnostic
from cloudnet.tosca.processors import CEND, CRED, Checker
from cloudnet.tosca.utils import merge_dict, normalize_dict
from cloudnet.tosca.yaml_line_numbering import Coord as YamlCoord

profiles_directory = "file:" + os.path.dirname(__file__) + "/profiles"

TYPE_SYSTEM = "TypeSystem"
SERVICE_TEMPLATE_CATALOG = "Service-Template-Catalog"
TOSCA_NORMATIVE_TYPES = "tosca_normative_types"
DEFAULT_TOSCA_NORMATIVE_TYPES = "default_tosca_normative_types"
SHORT_NAMES = "short_names"
configuration.DEFAULT_CONFIGURATION[TYPE_SYSTEM] = {
    SERVICE_TEMPLATE_CATALOG: None,
    TOSCA_NORMATIVE_TYPES: {
        "tosca_simple_yaml_1_0": profiles_directory
        + "/tosca_simple_yaml_1_0/types.yaml",
        "tosca_simple_yaml_1_1": profiles_directory
        + "/tosca_simple_yaml_1_1/types.yaml",
        "tosca_simple_yaml_1_2": profiles_directory
        + "/tosca_simple_yaml_1_2/types.yaml",
        "tosca_simple_yaml_1_3": profiles_directory
        + "/tosca_simple_yaml_1_3/types.yaml",
    },
    DEFAULT_TOSCA_NORMATIVE_TYPES: None,  # 'tosca_simple_yaml_1_2',
    SHORT_NAMES: {  # TODO: separate short names for TOSCA 1.0, TOSCA 1.1, TOSCA 1.2 and TOSCA 1.3
        "AttachesTo": "tosca.relationships.AttachesTo",
        "BlockStorage": "tosca.nodes.BlockStorage",  # TODO warning not same in 1.0 and 1.2 Storage. removed
        "ObjectStorage": "tosca.nodes.ObjectStorage",
        "Compute": "tosca.nodes.Compute",
        "ConnectsTo": "tosca.relationships.ConnectsTo",
        "Database": "tosca.nodes.Database",
        "DBMS": "tosca.nodes.DBMS",
        "DependsOn": "tosca.relationships.DependsOn",
        "Deployment.Image.VM": "tosca.artifacts.Deployment.Image.VM",
        "Endpoint": "tosca.capabilities.Endpoint",
        "LoadBalancer": "tosca.nodes.LoadBalancer",
        "HostedOn": "tosca.relationships.HostedOn",
        "Node": "tosca.capabilities.Node",
        "PortDef": "tosca.datatypes.network.PortDef",
        "PortInfo": "tosca.datatypes.network.PortInfo",
        "PortSpec": "tosca.datatypes.network.PortSpec",
        "SoftwareComponent": "tosca.nodes.SoftwareComponent",
        "Root": "tosca.nodes.Root",
        "WebApplication": "tosca.nodes.WebApplication",
        "WebServer": "tosca.nodes.WebServer",
        "tosca:Container": "tosca.capabilities.Container",
        "tosca:Compute": "tosca.nodes.Compute",
        "tosca:WebApplication": "tosca.nodes.WebApplication",
        # TODO: must be completed with all short names
        "tosca.nodes.ObjectStorage": "tosca.nodes.Storage.ObjectStorage",  # TODO remove later
        "tosca.nodes.BlockStorage": "tosca.nodes.Storage.BlockStorage",  # TODO remove later
    },
    # predefined workflows
    "predefined_workflows": {
        "deploy": {},
        "undeploy": {},
    },

    "check-useless-value-assigments": True,
    "check-unmapped-substitution-mappings-requirements": True,
    "warning-on-definitions-allowing-negative-values": True,
}

configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}

LOGGER = logging.getLogger(__name__)

def is_required(definition):
    return definition.get(syntax.REQUIRED, True) if isinstance(definition, dict) else True

class TypeSystem(object):
    """
    TOSCA Type System.
    """

    def __init__(self, configuration):
        self.types = {}
        self.merged_types = {}
        self.artifact_types = {}
        self.data_types = {
            # YAML types
            "string": {},
            "integer": {},
            "float": {},
            "boolean": {},
            "timestamp": {},
            "null": {},
            # TOSCA types
            "version": {},
            "range": {},
            "list": {},
            "map": {},
            "scalar-unit.size": {},
            "scalar-unit.time": {},
            "scalar-unit.frequency": {},
            "scalar-unit.bitrate": {},
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
        return type_name in [
            "string",
            "integer",
            "float",
            "boolean",
            "timestamp",
            "null",
            "version",
        ]

    def get_type_uri(self, short_type_name):
        result = short_type_name
        if self.types.get(short_type_name) is None:
            type_name = self.short_names.get(short_type_name)
            if type_name is not None:
                result = self.get_type_uri(type_name)
        return result

    def get_type(self, type_name):
        result = self.types.get(type_name)
        if result is None:
            type_name = self.short_names.get(type_name)
            if type_name is not None:
                result = self.get_type(type_name)
        return result

    def is_derived_from(self, type_name, derived_from_type_name):
        if type_name is None:
            return False
        # normalize short names
        type_name = self.get_type_uri(type_name)
        if isinstance(derived_from_type_name, str):
            derived_from_type_name = self.get_type_uri(derived_from_type_name)
            #
            if type_name == derived_from_type_name:
                return True
        elif isinstance(derived_from_type_name, list):
            if type_name in derived_from_type_name:
                return True
        type_type = self.get_type(type_name)
        if type_type is None:
            return False
        return self.is_derived_from(
            type_type.get(syntax.DERIVED_FROM), derived_from_type_name
        )

    def merge_type(self, type_name):
        if type_name is None:
            raise ValueError("type_name is None")

        # Search the result in the cache.
        result = self.merged_types.get(type_name)
        if result is not None:
            return result

        result = self.get_type(type_name)
        if result is None:
            # TBR            LOGGER.error(CRED + type_name + ' unknown!' + CEND)
            # diagnostic(gravity="error", file="", message=type_name + " unknown!", cls="TypeSystem",value=type_name )
            # TBR also ?     diagnostic(gravity='error', file="", message=type_name + ' unknown!', cls='TypeSystem')
            return dict()

        requirements = result.get(syntax.REQUIREMENTS)
        if requirements:
            result[syntax.REQUIREMENTS] = normalize_dict(requirements)

        derived_from = result.get(syntax.DERIVED_FROM)
        if derived_from is None or self.is_derived_from(derived_from, type_name):
            result = deepcopy(result)
            requirements = result.get(syntax.REQUIREMENTS)
            if requirements:
                result[syntax.REQUIREMENTS] = normalize_dict(requirements)
        else:
            # TBR            if not self.is_yaml_type(derived_from):
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
                    interfaces[interface_name] = merge_dict(
                        interface_type, interfaces[interface_name]
                    )
        for (capability_name, capability_yaml) in syntax.get_capabilities(
            result
        ).items():
            if isinstance(capability_yaml, dict):
                value = capability_yaml.get(
                    "value"
                )  # TODO: rename 'value' to '_old_value_'
                if value is not None:
                    capability_yaml[syntax.TYPE] = value
        return result

    def get_artifact_type_by_file_ext(self, file_ext):
        return self.artifact_types_by_file_ext.get(file_ext)

    def get_artifact_type_by_filename(self, filename):
        file_ext = filename[filename.rfind(".")+1:]
        return self.artifact_types_by_file_ext.get(file_ext)

    def get_relationship_types_compatible_with_capability_type(
        self, capability_type_name
    ):
        found_relationship_types = []
        for relationship_type_name in list(self.relationship_types):
            if self.is_relationship_type_compatible_with_capability_type(
                relationship_type_name, capability_type_name
            ):
                found_relationship_types.append(relationship_type_name)
        return found_relationship_types

    def is_relationship_type_compatible_with_capability_type(
        self, relationship_type_name, capability_type_name
    ):
        relationship_type = self.merge_type(relationship_type_name)
        for valid_target_type in relationship_type.get(syntax.VALID_TARGET_TYPES, []):
            if self.is_derived_from(
                capability_type_name, valid_target_type
            ):
                return True
        return False

    def get_compatible_capabilities(
        self,
        node_type_name,
        capability_name,
        capability_type_name
    ):
        node_type_def = self.merge_type(
                            self.get_type_uri(
                                node_type_name
                            )
                        )
        compatible_capabilities = []
        for cap_name, cap_def in node_type_def.get(
            syntax.CAPABILITIES, {}
        ).items():
            if(cap_name == capability_name
                or self.is_derived_from(
                        syntax.get_capability_type(cap_def),
                        capability_type_name
                   )
            ):
                compatible_capabilities.append(cap_name)
        return compatible_capabilities

# TOSCA scalar units.

SCALAR_SIZE_UNITS = {
    "B": 1,  # byte
    "kB": 1000,  # kilobyte
    "KiB": 1024,  # kibibyte
    "MB": 1000000,  # megabyte
    "MiB": 1048576,  # mebibyte
    "GB": 1000000000,  # gigabyte
    "GiB": 1073741824,  # gibibyte
    "TB": 1000000000000,  # terabyte
    "TiB": 1099511627776,  # tebibyte
}

SCALAR_TIME_UNITS = {
    "d": 86400,  # day
    "h": 3600,  # hour
    "m": 60,  # minute
    "s": 1,  # second
    "ms": 10 ** -3,  # millisecond
    "us": 10 ** -6,  # microsecond
    "ns": 10 ** -9,  # nanosecond
}

SCALAR_FREQUENCY_UNITS = {
    "Hz": 1,  # Hertz
    "kHz": 10 ** 3,  # Kilohertz
    "MHz": 10 ** 6,  # Megahertz
    "GHz": 10 ** 9,  # Gigahertz
}

SCALAR_BITRATE_UNITS = {
    "bps": 1,  # bit per second
    "Kbps": 1000,  # kilobit (1000 bits) per second
    "Kibps": 1024,  # kibibits (1024 bits) per second
    "Mbps": 1000000,  # megabit (1000000 bits) per second
    "Mibps": 1048576,  # mebibit (1048576 bits) per second
    "Gbps": 1000000000,  # gigabit (1000000000 bits) per second
    "Gibps": 1073741824,  # gibibits (1073741824 bits) per second
    "Tbps": 1000000000000,  # terabit (1000000000000 bits) per second
    "Tibps": 1099511627776,  # tebibits (1099511627776 bits) per second
    "Bps": 8,  # byte per second
    "KBps": 8 * 1000,  # kilobyte (1000 bytes) per second
    "KiBps": 8 * 1024,  # kibibytes (1024 bytes) per second
    "MBps": 8 * 1000000,  # megabyte (1000000 bytes) per second
    "MiBps": 8 * 1048576,  # mebibyte (1048576 bytes) per second
    "GBps": 8 * 1000000000,  # gigabyte (1000000000 bytes) per second
    "GiBps": 8 * 1073741824,  # gibibytes (1073741824 bytes) per second
    "TBps": 8 * 1000000000000,  # terabytes (1000000000000 bytes) per second
    "TiBps": 8 * 1099511627776,  # tebibytes (1099511627776 bytes) per second
}


def array_to_string_with_or_separator(a_list):
    return str(a_list).replace("['", "").replace("']", "").replace("', '", " or ")


SCALAR_UNIT_RE = re.compile("^([0-9]+(\.[0-9]+)?)( )*([A-Za-z]+)$")


def split_scalar_unit(a_string, units):
    match = SCALAR_UNIT_RE.fullmatch(a_string)
    if match is None:
        raise ValueError("<scalar> <unit> expected instead of " + a_string)
    values = [match.group(1), match.group(4)]
    try:
        scalar = float(values[0])
    except ValueError:
        raise ValueError("<scalar> expected instead of " + values[0])
    if scalar < 0:
        raise ValueError("positive <scalar> expected instead of " + str(scalar))
    unit = values[1]
    if units.get(unit) is None:
        raise ValueError(
            array_to_string_with_or_separator(list(units.keys()))
            + " expected instead of "
            + unit
        )
    return scalar, unit


def check_scalar_unit(a_string, units):
    scalar, unit = split_scalar_unit(a_string, units)
    return True


def normalize_scalar_unit(a_string, units):
    scalar, unit = split_scalar_unit(a_string, units)
    return scalar * units.get(unit)


VERSION_RE = re.compile("^([0-9]+)\.([0-9]+)(((\.[0-9]+)?)(\.[A-Za-z]+(\-[0-9]+)?)?)?$")


def check_version(a_string):
    return VERSION_RE.fullmatch(a_string) is not None


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
                processor.error(
                    context_error_message
                    + ": "
                    + str(value)
                    + " - "
                    + self.type_name
                    + " expected",
                    value,
                )
                return False
        except ValueError as exc:
            processor.error(
                context_error_message + ": " + str(value) + " - " + str(exc), value
            )
            return False
        return True


class ListTypeChecker(AbstractTypeChecker):
    def __init__(self, type_checker, item_type_definition):
        AbstractTypeChecker.__init__(self, type_checker.type_name)
        self.type_checker = type_checker
        self.item_type_definition = item_type_definition

    def check_type(self, the_list, processor, context_error_message):
        if self.type_checker.check_type(the_list, processor, context_error_message):
            idx = 0
            result = True
            for item in the_list:
                processor.check_value_assignment(
                    "item",
                    item,
                    self.item_type_definition,
                    context_error_message + "[" + str(idx) + "]",
                )
                idx += 1
            return result
        return False


class MapTypeChecker(AbstractTypeChecker):
    def __init__(self, type_checker, key_type_definition, value_type_definition):
        AbstractTypeChecker.__init__(self, type_checker.type_name)
        self.type_checker = type_checker
        self.key_type_definition = key_type_definition
        self.value_type_definition = value_type_definition

    def check_type(self, the_map, processor, context_error_message):
        if self.type_checker.check_type(the_map, processor, context_error_message):
            for key, value in the_map.items():
                processor.check_value_assignment(
                    "key",
                    key,
                    self.key_type_definition,
                    context_error_message + ":" + str(key),
                )
                processor.check_value_assignment(
                    "value",
                    value,
                    self.value_type_definition,
                    context_error_message + ":" + str(key),
                )
            return True
        return False


class DataTypeChecker(AbstractTypeChecker):
    def __init__(self, data_type_name, data_type):
        AbstractTypeChecker.__init__(self, data_type_name)
        self.data_type = data_type

    def check_type(self, values, processor, context_error_message):
        if not isinstance(values, dict):
            processor.error(
                context_error_message
                + ": "
                + str(values)
                + " - "
                + self.type_name
                + " expected",
                values,
            )
        else:
            properties = {syntax.PROPERTIES: values}
            processor.iterate_over_map_of_assignments(
                processor.check_value_assignment,
                syntax.PROPERTIES,
                properties,
                self.data_type,
                self.type_name,
                context_error_message,
            )
            processor.check_required_properties(
                properties, self.data_type, context_error_message
            )


isInt = lambda value: not isinstance(value, bool) and isinstance(value, int)


class ValidValuesChecker(AbstractTypeChecker):
    def __init__(self, type_checker, item_type_checker):
        AbstractTypeChecker.__init__(self, type_checker.type_name)
        self.type_checker = type_checker
        self.item_type_checker = item_type_checker

    def check_type(self, the_list, processor, context_error_message):
        if self.type_checker.check_type(the_list, processor, context_error_message):
            idx = 0
            result = True
            for item in the_list:
                if not self.item_type_checker.check_type(
                    item, processor, context_error_message + "[" + str(idx) + "]"
                ):
                    result = False
                idx += 1
            return result
        return False


BASIC_TYPE_CHECKERS = {
    # YAML types
    "string": BasicTypeChecker("string", lambda value: isinstance(value, str)),
    "integer": BasicTypeChecker("integer", lambda value: isInt(value)),
    "float": BasicTypeChecker(
        "float", lambda value: isinstance(value, float) or isInt(value)
    ),
    "boolean": BasicTypeChecker("boolean", lambda value: isinstance(value, bool)),
    "timestamp": BasicTypeChecker(
        "timestamp",
        lambda value: isinstance(value, datetime.datetime)
        or (isinstance(value, str) and datetime.datetime.fromisoformat(value)),
    ),
    "null": BasicTypeChecker("null", lambda value: value is None),
    # TOSCA types
    "version": BasicTypeChecker(
        "version",
        lambda value: (isinstance(value, float))
        or (isinstance(value, str) and check_version(value)),
    ),
    "range": BasicTypeChecker(
        "range",
        lambda value: isinstance(value, list)
        and len(value) == 2
        and isInt(value[0])
        and isInt(value[1]),
    ),
    "list": BasicTypeChecker("list", lambda value: isinstance(value, list)),
    "map": BasicTypeChecker("map", lambda value: isinstance(value, dict)),
    "scalar-unit.size": BasicTypeChecker(
        "scalar-unit.size",
        lambda value: isinstance(value, str)
        and check_scalar_unit(value, SCALAR_SIZE_UNITS),
    ),
    "scalar-unit.time": BasicTypeChecker(
        "scalar-unit.time",
        lambda value: isinstance(value, str)
        and check_scalar_unit(value, SCALAR_TIME_UNITS),
    ),
    "scalar-unit.frequency": BasicTypeChecker(
        "scalar-unit.frequency",
        lambda value: isinstance(value, str)
        and check_scalar_unit(value, SCALAR_FREQUENCY_UNITS),
    ),
    "scalar-unit.bitrate": BasicTypeChecker(
        "scalar-unit.bitrate",
        lambda value: isinstance(value, str)
        and check_scalar_unit(value, SCALAR_BITRATE_UNITS),
    ),
}

def normalize_constraint_clause(constraint_clause):
    if not isinstance(constraint_clause, dict):
        constraint_clause = {
            "equal": constraint_clause
        }
    return constraint_clause

class ConstraintClauseChecker(object):
    def __init__(
        self,
        constraint_name,
        check_value,
        check_constraint_operand=lambda value, type_checker: True,
    ):
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
    return v >= normalize_scalar_unit(v2[0], units) and v <= normalize_scalar_unit(
        v2[1], units
    )


type_check_operand = lambda operand, type_checker: type_checker(operand)
type_check_in_range_operand = (
    lambda operand, type_checker: isinstance(operand, list)
    and len(operand) == 2
    and type_checker(operand[0])
    and type_checker(operand[1])
)
type_check_in_range_range_operand = (
    lambda operand, type_checker: isinstance(operand, list)
    and len(operand) == 2
    and type_checker(operand)
)

BASIC_CONSTRAINT_CLAUSES = {
    "equal": {
        "string": ConstraintClauseChecker(
            "equal", CONSTRAINT_EQUAL, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "equal", CONSTRAINT_EQUAL, type_check_operand
        ),
        "float": ConstraintClauseChecker("equal", CONSTRAINT_EQUAL, type_check_operand),
        "boolean": ConstraintClauseChecker(
            "equal", CONSTRAINT_EQUAL, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "equal", CONSTRAINT_EQUAL, type_check_operand
        ),
        "null": ConstraintClauseChecker("equal", CONSTRAINT_EQUAL, type_check_operand),
        "version": ConstraintClauseChecker(
            "equal", CONSTRAINT_EQUAL, type_check_operand
        ),
        "range": ConstraintClauseChecker("equal", CONSTRAINT_EQUAL, type_check_operand),
# Following are not defined into the table of Section 3.6.3.1 of TOSCA v1.3
#        "list": ConstraintClauseChecker("equal", CONSTRAINT_EQUAL, type_check_operand),
#        "map": ConstraintClauseChecker("equal", CONSTRAINT_EQUAL, type_check_operand),
        "scalar-unit.size": ConstraintClauseChecker(
            "equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS)
            == normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS)
            == normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS)
            == normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_BITRATE_UNITS)
            == normalize_scalar_unit(v2, SCALAR_BITRATE_UNITS),
            type_check_operand,
        ),
    },
    "greater_than": {
        "string": ConstraintClauseChecker(
            "greater_than", CONSTRAINT_GREATER_THAN, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "greater_than", CONSTRAINT_GREATER_THAN, type_check_operand
        ),
        "float": ConstraintClauseChecker(
            "greater_than", CONSTRAINT_GREATER_THAN, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "greater_than", CONSTRAINT_GREATER_THAN, type_check_operand
        ),
        "version": ConstraintClauseChecker(
            "greater_than", CONSTRAINT_GREATER_THAN, type_check_operand
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "greater_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS)
            > normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "greater_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS)
            > normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "greater_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS)
            > normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "greater_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_BITRATE_UNITS)
            > normalize_scalar_unit(v2, SCALAR_BITRATE_UNITS),
            type_check_operand,
        ),
    },
    "greater_or_equal": {
        "string": ConstraintClauseChecker(
            "greater_or_equal", CONSTRAINT_GREATER_OR_EQUAL, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "greater_or_equal", CONSTRAINT_GREATER_OR_EQUAL, type_check_operand
        ),
        "float": ConstraintClauseChecker(
            "greater_or_equal", CONSTRAINT_GREATER_OR_EQUAL, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "greater_or_equal", CONSTRAINT_GREATER_OR_EQUAL, type_check_operand
        ),
        "version": ConstraintClauseChecker(
            "greater_or_equal", CONSTRAINT_GREATER_OR_EQUAL, type_check_operand
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "greater_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS)
            >= normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "greater_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS)
            >= normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "greater_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS)
            >= normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "greater_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_BITRATE_UNITS)
            >= normalize_scalar_unit(v2, SCALAR_BITRATE_UNITS),
            type_check_operand,
        ),
    },
    "less_than": {
        "string": ConstraintClauseChecker(
            "less_than", CONSTRAINT_LESS_THAN, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "less_than", CONSTRAINT_LESS_THAN, type_check_operand
        ),
        "float": ConstraintClauseChecker(
            "less_than", CONSTRAINT_LESS_THAN, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "less_than", CONSTRAINT_LESS_THAN, type_check_operand
        ),
        "version": ConstraintClauseChecker(
            "less_than", CONSTRAINT_LESS_THAN, type_check_operand
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "less_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS)
            < normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "less_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS)
            < normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "less_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS)
            < normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "less_than",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_BITRATE_UNITS)
            < normalize_scalar_unit(v2, SCALAR_BITRATE_UNITS),
            type_check_operand,
        ),
    },
    "less_or_equal": {
        "string": ConstraintClauseChecker(
            "less_or_equal", CONSTRAINT_LESS_OR_EQUAL, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "less_or_equal", CONSTRAINT_LESS_OR_EQUAL, type_check_operand
        ),
        "float": ConstraintClauseChecker(
            "less_or_equal", CONSTRAINT_LESS_OR_EQUAL, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "less_or_equal", CONSTRAINT_LESS_OR_EQUAL, type_check_operand
        ),
        "version": ConstraintClauseChecker(
            "less_or_equal", CONSTRAINT_LESS_OR_EQUAL, type_check_operand
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "less_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_SIZE_UNITS)
            <= normalize_scalar_unit(v2, SCALAR_SIZE_UNITS),
            type_check_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "less_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_TIME_UNITS)
            <= normalize_scalar_unit(v2, SCALAR_TIME_UNITS),
            type_check_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "less_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_FREQUENCY_UNITS)
            <= normalize_scalar_unit(v2, SCALAR_FREQUENCY_UNITS),
            type_check_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "less_or_equal",
            lambda v1, v2: normalize_scalar_unit(v1, SCALAR_BITRATE_UNITS)
            <= normalize_scalar_unit(v2, SCALAR_BITRATE_UNITS),
            type_check_operand,
        ),
    },
    "in_range": {
        "string": ConstraintClauseChecker(
            "in_range", CONSTRAINT_IN_RANGE, type_check_in_range_operand
        ),
        "integer": ConstraintClauseChecker(
            "in_range", CONSTRAINT_IN_RANGE, type_check_in_range_operand
        ),
        "float": ConstraintClauseChecker(
            "in_range", CONSTRAINT_IN_RANGE, type_check_in_range_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "in_range", CONSTRAINT_IN_RANGE, type_check_in_range_operand
        ),
        "version": ConstraintClauseChecker(
            "in_range", CONSTRAINT_IN_RANGE, type_check_in_range_operand
        ),
        "range": ConstraintClauseChecker(
            "in_range",
            lambda v1, v2: v1[0] >= v2[0] and v1[1] <= v2[1],
            type_check_in_range_range_operand,
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "in_range",
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_SIZE_UNITS),
            type_check_in_range_operand,
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "in_range",
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_TIME_UNITS),
            type_check_in_range_operand,
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "in_range",
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_FREQUENCY_UNITS),
            type_check_in_range_operand,
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "in_range",
            lambda v1, v2: in_range_scalar_unit(v1, v2, SCALAR_BITRATE_UNITS),
            type_check_in_range_operand,
        ),
    },
    "valid_values": {
        "string": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "integer": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "float": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "boolean": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "timestamp": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "null": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "version": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "range": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "list": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "map": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "scalar-unit.size": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "scalar-unit.time": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "scalar-unit.frequency": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
        "scalar-unit.bitrate": ConstraintClauseChecker(
            "valid_values", CONSTRAINT_VALID_VALUES, type_check_operand
        ),
    },
    "length": {
        "string": ConstraintClauseChecker("length", CONSTRAINT_LENGTH),
        "list": ConstraintClauseChecker("length", CONSTRAINT_LENGTH),
        "map": ConstraintClauseChecker("length", CONSTRAINT_LENGTH),
    },
    "min_length": {
        "string": ConstraintClauseChecker("min_length", CONSTRAINT_MIN_LENGTH),
        "list": ConstraintClauseChecker("min_length", CONSTRAINT_MIN_LENGTH),
        "map": ConstraintClauseChecker("min_length", CONSTRAINT_MIN_LENGTH),
    },
    "max_length": {
        "string": ConstraintClauseChecker("max_length", CONSTRAINT_MAX_LENGTH),
        "list": ConstraintClauseChecker("max_length", CONSTRAINT_MAX_LENGTH),
        "map": ConstraintClauseChecker("max_length", CONSTRAINT_MAX_LENGTH),
    },
    "pattern": {
        "string": ConstraintClauseChecker(
            "pattern", lambda v1, v2: re.fullmatch(v2, v1) is not None
        ),
    },
    "schema": {
        "string": ConstraintClauseChecker("schema", lambda v1, v2: True),  # TODO
    },
}

class ToscaFunction(object):
    def get_return_data_type(self, parameters, type_checker, context_error_message):
        return None

    def get_template_type(self, attributes_or_properties, parameters, type_checker, context_error_message):
        topology_template = type_checker.get_topology_template()
        template_name = parameters[0]
        template = topology_template.get('node_templates', {}).get(template_name)
        if template is None:
            template = topology_template.get('relationship_templates', {}).get(template_name)
            if template is None:
                return None
        merged_template_type = type_checker.type_system.merge_type(type_checker.type_system.get_type_uri(template.get('type')))
        return merged_template_type.get(attributes_or_properties, {}).get(parameters[1], {}).get('type')

class ToscaGetAttributeFunction(ToscaFunction):
    def get_return_data_type(self, parameters, type_checker, context_error_message):
        return self.get_template_type('attributes', parameters, type_checker, context_error_message)

class ToscaGetPropertyFunction(ToscaFunction):
    def get_return_data_type(self, parameters, type_checker, context_error_message):
        return self.get_template_type('properties', parameters, type_checker, context_error_message)

#TODO: add all other TOSCA functions such as concat, join, token, etc.
TOSCA_FUNCTIONS = {
    "get_attribute": ToscaGetAttributeFunction(),
    "get_property": ToscaGetPropertyFunction(),
}


REFINE_OR_NEW = None
PREVIOUSLY_UNDEFINED = {}


class NodeTemplateRequirement(object):
    def __init__(self, node_template_name, requirement_name, requirement_definition):
        self.node_template_name = node_template_name
        self.requirement_name = requirement_name
        self.requirement_definition = requirement_definition
        self.occurrences = requirement_definition.get(syntax.OCCURRENCES, [1, 1])
        self.lower_bound = self.occurrences[0]
        self.upper_bound = self.occurrences[1]
        self.connections = 0

    def connectIt(self):
        self.connections += 1

class TypeChecker(Checker):
    """
    TOSCA type system checker
    """

    def _processor_initialize_(self):
        self.substituting_topology_templates = []
        service_template_catalog = self.configuration.get(
            TYPE_SYSTEM, SERVICE_TEMPLATE_CATALOG
        )
        if service_template_catalog is None:
            self.info("No service template catalog to load.")
        else:
            self.info("Loading service template catalog...")
            from cloudnet.tosca.importers import FilesystemImporter

            importer = FilesystemImporter("")
            for service_template in service_template_catalog:
                self.load_tosca_yaml_template(service_template, importer)
            self.info("Service template catalog loaded.")

    def check(self):
        # initialize global variables
        self.current_type_name = None
        self.current_targets = None
        self.current_targets_activity_type = None
        self.current_targets_condition_type = None
        self.current_default_inputs = {}
        self.current_default_inputs_location = None
        self.current_imperative_workflow = None
        self.reserved_function_keywords = {}
        self.current_allowed_operation_host_keynames = []
        self.all_the_node_template_requirements = {}

        self.info("TOSCA type checking...")

        # Load the used TOSCA normative types according to tosca_definitions_version.
        if not self.is_tosca_definitions_version_file():
            tosca_normative_types_map = self.configuration.get(
                TYPE_SYSTEM, TOSCA_NORMATIVE_TYPES
            )
            tosca_normative_types = self.get_mapping(
                self.get_tosca_definitions_version(), tosca_normative_types_map
            )
            if tosca_normative_types is None:
                default_tosca_normative_types = self.configuration.get(
                    TYPE_SYSTEM, DEFAULT_TOSCA_NORMATIVE_TYPES
                )
                if default_tosca_normative_types is not None:
                    self.warning(
                        " " + default_tosca_normative_types + " normative types loaded",
                        default_tosca_normative_types,
                    )
                    tosca_normative_types = self.get_mapping(
                        default_tosca_normative_types, tosca_normative_types_map
                    )
                else:
                    self.warning(" no normative types loaded")
                    tosca_normatives_type = None
            if tosca_normative_types is None:
                pass  # nothing to do.
            elif isinstance(tosca_normative_types, str):
                self.load_tosca_yaml_template(
                    tosca_normative_types, self.tosca_service_template
                )
            elif isinstance(tosca_normative_types, list):
                for value in tosca_normative_types:
                    self.load_tosca_yaml_template(value, self.tosca_service_template)
            else:
                raise ValueError(
                    TYPE_CHECKER
                    + ":"
                    + TOSCA_NORMATIVE_TYPES
                    + " must be a string or list"
                )

        # Load the tosca template.
        self.load_tosca_yaml_template(
            self.tosca_service_template.get_filename(), self.tosca_service_template
        )

        self.check_service_template_definition(self.tosca_service_template.get_yaml())

        self.info("TOSCA type checking done.")

        return True

    def load_tosca_yaml_template(
        self, path, importer, namescape_prefix="", already_loaded_paths={}
    ):
        # Load the tosca service template if not already loaded.

        # TBR
        # tosca_service_template = already_loaded_paths.get(path)
        # if tosca_service_template == None:
        #    tosca_service_template = importer.imports(path)
        #    already_loaded_paths[path] = tosca_service_template
        # elif namescape_prefix == '':
        #    return
        tosca_service_template = importer.imports(path)
        import os.path

        fullname = namescape_prefix + os.path.normpath(
            tosca_service_template.get_fullname()
        )
        if already_loaded_paths.get(fullname) is None:
            already_loaded_paths[fullname] = tosca_service_template
        else:
            return

        template_yaml = tosca_service_template.get_yaml()

        # Load imported templates.
        index = 0
        for import_yaml in syntax.get_imports(template_yaml):
            try:
                import_filepath = self.get_import_full_filepath(import_yaml)
            except ValueError as exc:
                self.error("imports[%d]:%s" % (index, exc), import_yaml)
                continue
            try:
                import_namespace_prefix = syntax.get_import_namespace_prefix(
                    import_yaml
                )
                if import_namespace_prefix is None:
                    import_namespace_prefix = (
                        namescape_prefix  # reuse current namespace_prefix
                    )
                else:
                    import_namespace_prefix = import_namespace_prefix + ":"
                self.load_tosca_yaml_template(
                    import_filepath,
                    tosca_service_template,
                    import_namespace_prefix,
                    already_loaded_paths,
                )
            except FileNotFoundError:
                # It seems that we get a program crash here but I didn't figure out
                # how to deal with yet !
                #    This case occurs when a file imported is not present
                #    JLC 20201126
                self.error(
                    "imports["
                    + str(index)
                    + "]:file: "
                    + import_filepath
                    + " - file not found",
                    import_yaml,
                )
            except ValueError as exc:
                self.error(
                    "imports["
                    + str(index)
                    + "]:file: "
                    + import_filepath
                    + " - "
                    + str(exc),
                    import_yaml,
                )
            index = index + 1

        # Put all types of the loaded template into the type system.
        for type_kind in [
            syntax.ARTIFACT_TYPES,
            syntax.DATA_TYPES,
            syntax.INTERFACE_TYPES,
            syntax.CAPABILITY_TYPES,
            syntax.REQUIREMENT_TYPES,
            syntax.RELATIONSHIP_TYPES,
            syntax.NODE_TYPES,
            syntax.GROUP_TYPES,
            syntax.POLICY_TYPES,
        ]:
            # Iterate over types.
            for (type_name, type_yaml) in template_yaml.get(type_kind, {}).items():
                full_type_name = namescape_prefix + type_name
                # check that this type is not already defined
                if self.type_system.types.get(full_type_name):
                    self.error(
                        " - "
                        + path
                        + ":"
                        + type_kind
                        + ":"
                        + type_name
                        + " - type already defined",
                        type_yaml
                    )
                else:
                    self.type_system.types[full_type_name] = type_yaml
                    getattr(self.type_system, type_kind)[full_type_name] = type_yaml
                    self.debug(" %s registered" % full_type_name)

                if namescape_prefix != "":
                    osn = self.type_system.short_names.get(type_name)
                    if osn != None:
                        self.warning(
                            "short_names[%s] = %s replaced by %s"
                            % (type_name, osn, full_type_name)
                        )
                    self.debug("short_names[%s] = %s" % (type_name, full_type_name))
                    self.type_system.short_names[type_name] = full_type_name

        # Associate file extensions to artifact types.
        artifact_types = syntax.get_artifact_types(template_yaml)
        if artifact_types is None:
            artifact_types = {}
        for artifact_name, artifact_yaml in artifact_types.items():
            for file_ext in artifact_yaml.get(syntax.FILE_EXT, []):
                artifact_type = self.type_system.get_artifact_type_by_file_ext(file_ext)
                if artifact_type:
                    self.warning(
                        " - "
                        + path
                        + " - file extension '"
                        + file_ext
                        + "' already associated to "
                        + artifact_type
                    )
                    continue
                self.type_system.artifact_types_by_file_ext[file_ext] = (
                    namescape_prefix + artifact_name
                )

        # register substituting topology templates
        substitution_mappings_node_type = (
            template_yaml.get("topology_template", {})
            .get("substitution_mappings", {})
            .get("node_type")
        )
        if substitution_mappings_node_type != None:
            self.info(
                "register %s as susbtitution topology template for %s node type"
                % (
                    tosca_service_template.get_fullname(),
                    substitution_mappings_node_type,
                )
            )
            self.substituting_topology_templates.append(tosca_service_template)

    def get_topology_template(self):
        return self.tosca_service_template.get_yaml().get(syntax.TOPOLOGY_TEMPLATE, {})

    def unchecked(self, definition, keyword, context_error_message):
        value = definition.get(keyword) if isinstance(definition, dict) else None
        if value is not None:
            self.error(
                context_error_message
                + ":"
                + keyword
                + ": "
                + str(value)
                + " - currently unchecked",
                value,
            )

    def check_keyword(
        self, definition, keyword, lambda_expression, context_error_message
    ):
        value = definition.get(keyword)
        if value is not None:
            lambda_expression(value, context_error_message + ":" + keyword)

    def check_type_existence(self, type_kinds, type_name, context_error_message):
        if type_name is None:
            return False
        type_name = self.type_system.get_type_uri(type_name)
        if isinstance(type_kinds, str):
            type_kinds = [type_kinds]
        for type_kind in type_kinds:
            if (
                getattr(self.type_system, type_kind + "_types").get(type_name)
                is not None
            ):
                return True
        if self.type_system.types.get(type_name) is None:
            self.error(
                context_error_message
                + ": "
                + type_name
                + " - undefined type but "
                + array_to_string_with_or_separator(type_kinds)
                + " type expected",
                type_name,
            )
        else:
            self.error(
                context_error_message
                + ": "
                + type_name
                + " - defined type but "
                + array_to_string_with_or_separator(type_kinds)
                + " type expected",
                type_name,
            )
        return False

    def check_type(self, type_kinds, the_type, previous_type, context_error_message):
        if self.check_type_existence(type_kinds, the_type, context_error_message):
            # check that the_type is compatible with previous type definition
            if previous_type is not None:
                LOGGER.debug(
                    context_error_message
                    + ": "
                    + the_type
                    + " - overload "
                    + previous_type,
                    the_type
                )
                if not self.type_system.is_derived_from(the_type, previous_type):
                    self.error(
                        context_error_message
                        + ": "
                        + the_type
                        + " - incompatible with previous declared type "
                        + previous_type,
                        the_type,
                    )
                    return False
            return True
        return False

    def check_type_in_definition(
        self,
        type_kinds,
        keyword,
        definition,
        previous_definition,
        context_error_message,
    ):
        definition_type_name = definition.get(keyword) if isinstance(definition, dict) else definition
        previous_definition_type_name = previous_definition.get(keyword)
        checked = self.check_type(
            type_kinds,
            definition_type_name,
            previous_definition_type_name,
            context_error_message + ":" + keyword,
        )
        if definition_type_name is None:
            definition_type_name = previous_definition_type_name
        # compute merged type that is the union of relationship type and previous_requirement_relationship
        if definition_type_name is None:
            self.error(
                context_error_message
                + ":"
                + keyword
                + " - "
                + type_kinds
                + " type missed",
                definition,
            )
            merged_type = previous_definition
        else:
            merged_type = merge_dict(
                self.type_system.merge_type(
                    self.type_system.get_type_uri(definition_type_name)
                ),
                previous_definition,
            )
        return checked, definition_type_name, merged_type

    def check_types_in_definition(
        self,
        type_kinds,
        keyword,
        definition,
        previous_definition,
        context_error_message,
        additional_check=None,
    ):
        previous_types = previous_definition.get(keyword)
        idx = 0
        for value in definition.get(keyword, []):
            cem = context_error_message + ":" + keyword + "[" + str(idx) + "]"
            if self.check_type_existence(type_kinds, value, cem):
                if previous_types:
                    # check that value is compatible with previous types
                    not_compatible_with_previous_types = True
                    for previous_type in previous_types:
                        if self.type_system.is_derived_from(value, previous_type):
                            not_compatible_with_previous_types = False
                            break
                    if not_compatible_with_previous_types:
                        self.error(
                            cem
                            + ": "
                            + value
                            + " - incompatible with "
                            + array_to_string_with_or_separator(previous_types),
                            value,
                        )
                if additional_check:
                    additional_check(value, cem + ": ")
            idx = idx + 1

    def check_type_compatible_with_valid_source_types(
        self, type_name, valid_source_types
    ):
        if valid_source_types is None or len(valid_source_types) == 0:
            return True
        for valid_source_type in valid_source_types:
            if self.type_system.is_derived_from(type_name, valid_source_type):
                return True
        return False

    def iterate_over_list(
        self, definition, keyword, lambda_expression, context_error_message
    ):
        the_list = definition.get(
            keyword
        )  # get the list value associated to the keyword
        if the_list is not None:  # if list defined then iterate over items
            cem = context_error_message + ":" + keyword
            idx = 0  # current item index
            for item in the_list:
                lambda_expression(item, cem + "[" + str(idx) + "]")
                idx += 1

    def iterate_over_map_of_definitions(
        self,
        method,
        keyword,
        definition1,
        definition2,
        refined_interface_name,
        context_error_message,
    ):
        context_error_message += ":" + keyword + ":"
        definition2_keyword = definition2.get(keyword, {})
        for key, value in definition1.get(keyword, {}).items():
            previous_value = definition2_keyword.get(key)
            if previous_value is None:
                if refined_interface_name != REFINE_OR_NEW:
                    self.error(
                        context_error_message
                        + key
                        + " - undefined in "
                        + refined_interface_name,
                        key,
                    )
                previous_value = PREVIOUSLY_UNDEFINED
            method(key, value, previous_value, context_error_message + key)

    def search_relationship_types_compatible_with_capability_type(
        self, capability_type_name, context_error_message
    ):
        # Check that there is one relationship where capability_type_name is compatible with at least one valid target type
        found_relationship_types = \
            self.type_system.get_relationship_types_compatible_with_capability_type(
                capability_type_name
            )
        nb_found_relationship_types = len(found_relationship_types)
        if nb_found_relationship_types == 0:
            self.error(
                context_error_message
                + " undefined but no relationship type is compatible with "
                + capability_type_name
            )
        elif nb_found_relationship_types == 1:
            self.warning(
                context_error_message
                + " undefined but "
                + found_relationship_types[0]
                + " is compatible with "
                + capability_type_name,
                capability_type_name
            )
        else:
            self.warning(
                context_error_message
                + ": undefined but "
                + array_to_string_with_or_separator(found_relationship_types)
                + " are compatible with "
                + capability_type_name,
                capability_type_name
            )
        return found_relationship_types

    def check_service_template_definition(self, service_template_definition):
        # check tosca_definitions_version - already done
        # check namespace - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check dsl_definitions - nothing to do
        # check repositories
        for repository_name, repository_definition in syntax.get_repositories(
            service_template_definition
        ).items():
            self.check_repository_definition(
                repository_name, repository_definition, syntax.REPOSITORIES
            )
        # check imports - already done

        def iterate_over_types(check_method, service_template_definition, keyword):
            base_context_error_message = keyword + ":"
            for type_name, type_definition in service_template_definition.get(
                keyword, {}
            ).items():
                context_error_message = base_context_error_message + type_name
                # Store the current type name
                self.current_type_name = type_name
                # check derived_from
                cem = context_error_message + ":" + syntax.DERIVED_FROM
                derived_from = syntax.get_derived_from(type_definition)
                # check derived_from existence
                self.check_type_existence(
                    keyword[: keyword.find("_")], derived_from, cem
                )
                # check acyclic derived_from
                if self.type_system.is_derived_from(derived_from, type_name):
                    self.error(
                        cem
                        + ": "
                        + derived_from
                        + " - cyclically derived from "
                        + type_name,
                        type_name,
                    )
                # execute check_method
                if (
                    derived_from is None
                    or self.type_system.get_type(derived_from) is None
                    or self.type_system.is_derived_from(derived_from, type_name)
                ):
                    derived_from_type = {}
                else:
                    derived_from_type = self.type_system.merge_type(derived_from)
                check_method(
                    type_name, type_definition, derived_from_type, context_error_message
                )

        # check artifact_types
        iterate_over_types(
            self.check_artifact_type, service_template_definition, syntax.ARTIFACT_TYPES
        )
        # check data_types
        iterate_over_types(
            self.check_data_type, service_template_definition, syntax.DATA_TYPES
        )
        # check capability_types
        iterate_over_types(
            self.check_capability_type,
            service_template_definition,
            syntax.CAPABILITY_TYPES,
        )
        # check interface_types
        iterate_over_types(
            self.check_interface_type,
            service_template_definition,
            syntax.INTERFACE_TYPES,
        )
        # check relationship_types
        iterate_over_types(
            self.check_relationship_type,
            service_template_definition,
            syntax.RELATIONSHIP_TYPES,
        )
        # check node_types
        iterate_over_types(
            self.check_node_type, service_template_definition, syntax.NODE_TYPES
        )
        # check group_types
        iterate_over_types(
            self.check_group_type, service_template_definition, syntax.GROUP_TYPES
        )
        # check policy_types
        iterate_over_types(
            self.check_policy_type, service_template_definition, syntax.POLICY_TYPES
        )
        # check topology_template
        topology_template = service_template_definition.get(syntax.TOPOLOGY_TEMPLATE)
        if topology_template is not None:
            self.check_topology_template(topology_template, syntax.TOPOLOGY_TEMPLATE)

    def check_repository_definition(
        self, repository_name, repository_definition, context_error_message
    ):
        # Normalize repository_definition
        if isinstance(repository_definition, str):
            repository_definition = {syntax.URL: repository_definition}
        # check description - nothing to do
        # check url - nothing to do
        # check credential - nothing to do

    def check_attribute_definition(
        self,
        attribute_name,
        attribute_definition,
        previous_attribute_definition,
        context_error_message,
    ):
        # check type
        self.check_type_in_definition(
            "data",
            syntax.TYPE,
            attribute_definition,
            previous_attribute_definition,
            context_error_message,
        )
        self.check_yaml_type(attribute_definition, context_error_message)
        # check description - nothing to do
        # check default
        if 'default' in attribute_definition:
            default = attribute_definition.get(syntax.DEFAULT)
            self.check_value(
                default,
                attribute_definition,
                previous_attribute_definition,
                context_error_message + ":" + syntax.DEFAULT,
            )
        # check status - nothing to do
        # check key_schema
        self.check_schema_definition(
            syntax.KEY_SCHEMA,
            attribute_definition,
            previous_attribute_definition,
            context_error_message,
        )
        # check entry_schema
        self.check_schema_definition(
            syntax.ENTRY_SCHEMA,
            attribute_definition,
            previous_attribute_definition,
            context_error_message,
        )

    def check_schema_definition(
        self, keyword, definition, previous_definition, context_error_message
    ):
        schema_definition = definition.get(keyword) if isinstance(definition, dict) else None
        if schema_definition is None:
            return

        context_error_message += ":" + keyword

        definition_type = definition.get(syntax.TYPE)
        root_type = self.get_root_data_type_name(definition_type)
        if keyword is syntax.KEY_SCHEMA and root_type != "map":
            self.error(
                context_error_message
                + ":"
                + keyword
                + " - unexpected because type is "
                + str(definition_type)
                + " instead of map",
                root_type,
            )
        if keyword is syntax.ENTRY_SCHEMA and root_type not in ["map", "list"]:
            self.error(
                context_error_message
                + ":"
                + keyword
                + " - unexpected because type is "
                + str(definition_type)
                + " instead of list or map",
                root_type,
            )

        previous_schema_definition = previous_definition.get(keyword, {})

        # check the short notation used before TOSCA 1.3
        if isinstance(schema_definition, str):
            if isinstance(previous_schema_definition, str):
                previous_schema_definition = {syntax.TYPE: previous_schema_definition}
            self.check_type_in_definition(
                "data",
                syntax.TYPE,
                {syntax.TYPE: schema_definition},
                previous_schema_definition,
                context_error_message,
            )
            return
        # check the extended notation
        # check type
        self.check_type_in_definition(
            "data",
            syntax.TYPE,
            schema_definition,
            previous_schema_definition,
            context_error_message,
        )
        type_checker = self.get_type_checker(
            schema_definition, previous_schema_definition, context_error_message
        )
        self.check_yaml_type(schema_definition, context_error_message)
        # check description - nothing to do
        # check constraints
        constraints = schema_definition.get(syntax.CONSTRAINTS)
        if constraints is not None:
            self.check_list_of_constraint_clauses(
                constraints,
                type_checker,
                context_error_message + ":" + syntax.CONSTRAINTS,
            )
        # check key_schema
        self.check_schema_definition(
            syntax.KEY_SCHEMA,
            schema_definition,
            previous_schema_definition,
            context_error_message,
        )
        # check entry_schema
        self.check_schema_definition(
            syntax.ENTRY_SCHEMA,
            schema_definition,
            previous_schema_definition,
            context_error_message,
        )

    def get_root_data_type_name(self, type_name):
        initial_type_name = type_name
        while True:
            data_type = self.type_system.data_types.get(
                self.type_system.get_type_uri(type_name)
            )
            if data_type is None:
                return None
            derived_from = data_type.get(syntax.DERIVED_FROM)
            if derived_from is None:
                return type_name
            type_name = derived_from
            if type_name == initial_type_name:
                return None  # stop infinite loop when derived_from is a cycle relation

    def get_type_checker(self, definition, previous_definition, context_error_message):
        definition = merge_dict(definition, previous_definition)
        data_type_name = syntax.get_type(definition)
        if data_type_name is None:
            # TBR            self.error(context_error_message + ' - type expected')
            return None
        type_checker = BASIC_TYPE_CHECKERS.get(
            self.get_root_data_type_name(data_type_name)
        )
        if type_checker is not None:
            # TODO: factorize following code
            if data_type_name == "list":
                entry_schema = definition.get(syntax.ENTRY_SCHEMA, "string")
                if isinstance(entry_schema, str):
                    entry_schema = {syntax.TYPE: entry_schema}
                type_checker = ListTypeChecker(type_checker, entry_schema)
            elif data_type_name == "map":
                key_schema = definition.get(syntax.KEY_SCHEMA, "string")
                if isinstance(key_schema, str):
                    key_schema = {syntax.TYPE: key_schema}
                entry_schema = definition.get(syntax.ENTRY_SCHEMA, "string")
                if isinstance(entry_schema, str):
                    entry_schema = {syntax.TYPE: entry_schema}
                type_checker = MapTypeChecker(type_checker, key_schema, entry_schema)
        else:
            # definition_type could be a data type
            data_type = self.type_system.merge_type(
                self.type_system.get_type_uri(data_type_name)
            )
            type_checker = DataTypeChecker(data_type_name, data_type)

        return type_checker

    def check_value(
        self, value, definition, previous_definition, context_error_message
    ):
        LOGGER.debug(context_error_message + " - checking...")

        data_types = syntax.get_type(definition)
        if isinstance(data_types, list):
            pythontypes2toscatypes = {
                str: "string",
                int: "integer"
            }
            for k, v in pythontypes2toscatypes.items():
                if isinstance(value, k):
                    if v in data_types:
                        return
            self.error(context_error_message + ": " + str(value) + " - " + array_to_string_with_or_separator(data_types) + " type expected")
            return

        type_checker = self.get_type_checker(
            definition, previous_definition, context_error_message
        )
        if type_checker is None:
            # ISSUE: I don't know what to do when no type checker found :-(
            self.warning(
                context_error_message
                + ": "
                + str(value)
                + " - no type found to check the value",
                value
            )
            return

        if not type_checker.check_type(value, self, context_error_message):
            # value does not match type_checker
            return # don't check constraints

        def evaluate_constraints(constraint_clauses):
            def get_constraint_clause_checker(type_name, constraint_clause_checkers):
                constraint_clause_checker = constraint_clause_checkers.get(type_name)
                if constraint_clause_checker is None:
                    # type_name could be a data type
                    data_type = self.type_system.data_types.get(
                        self.type_system.get_type_uri(type_name)
                    )
                    if data_type is not None:  # data type found
                        derived_from = data_type.get(syntax.DERIVED_FROM)
                        if (
                            derived_from is not None
                            and not self.type_system.is_derived_from(
                                derived_from, type_name
                            )
                        ):
                            constraint_clause_checker = get_constraint_clause_checker(
                                derived_from, constraint_clause_checkers
                            )
                return constraint_clause_checker

            for constraint_clause in constraint_clauses:
                constraint_clause = normalize_constraint_clause(constraint_clause)
                for constraint_name, constraint_value in constraint_clause.items():
                    constraint_clause_checkers = BASIC_CONSTRAINT_CLAUSES.get(
                        constraint_name
                    )
                    if constraint_clause_checkers is None:
                        self.error(
                            context_error_message
                            + " - "
                            + constraint_name
                            + " unsupported operator",
                            constraint_name,
                        )
                        continue
                    definition_type = definition.get(
                        syntax.TYPE
                    ) or previous_definition.get(syntax.TYPE)
                    constraint_clause_checker = get_constraint_clause_checker(
                        definition_type, constraint_clause_checkers
                    )
                    if constraint_clause_checker is None:
                        self.error(
                            context_error_message
                            + " - "
                            + constraint_name
                            + " unallowed operator on "
                            + definition_type
                            + " value",
                            value,
                        )
                        continue
                    LOGGER.debug(
                        context_error_message
                        + " - evaluate "
                        + constraint_name
                        + ": "
                        + str(constraint_value),
                        constraint_name
                    )
                    if not constraint_clause_checker.check_constraint(
                        value, constraint_value, self, context_error_message
                    ):
                        self.error(
                            context_error_message
                            + ": "
                            + str(value)
                            + " - "
                            + constraint_name
                            + ": "
                            + str(constraint_value)
                            + " failed",
                            value,
                        )

        # check that value respects all constraint clauses of the definition type
        data_type_name = syntax.get_type(definition) or syntax.get_type(previous_definition)
        data_type = self.type_system.merge_type(self.type_system.get_type_uri(data_type_name))
        evaluate_constraints(data_type.get(syntax.CONSTRAINTS, []))

        # check that value respects all constraint clauses of both definition and previous_definition
        evaluate_constraints(definition.get(syntax.CONSTRAINTS, []))
        evaluate_constraints(previous_definition.get(syntax.CONSTRAINTS, []))

        LOGGER.debug(context_error_message + " - checked")

    def check_constraint_clause(
        self, constraint_clause, type_checker, context_error_message
    ):
        constraint_clause = normalize_constraint_clause(constraint_clause)
        for constraint_operator, constraint_value in constraint_clause.items():
            cem = context_error_message + ":" + constraint_operator
            constraint_clause_checkers = BASIC_CONSTRAINT_CLAUSES.get(
                constraint_operator
            )
            if constraint_clause_checkers is None:
                self.error(cem + " - unsupported operator", constraint_operator)
                continue

            if type_checker is None:
                continue  # no type_checker then can't check typing of the constraint

            # check that the constraint operator is valid according to the type
            constraint_clause_checker = constraint_clause_checkers.get(
                type_checker.type_name
            )
            if constraint_clause_checker is None:
                self.error(
                    cem + " - unallowed operator on " + type_checker.type_name,
                    constraint_operator,
                )
                continue

            # check that the constraint operand is valid
            if constraint_operator == "valid_values":
                check_constraint_operand = lambda operand: ValidValuesChecker(
                    BASIC_TYPE_CHECKERS.get("list"), type_checker
                ).check_type(operand, self, cem)
            else:
                check_constraint_operand = lambda operand: type_checker.check_type(
                    operand, self, cem
                )
            constraint_clause_checker.check_operand(
                constraint_value, check_constraint_operand
            )

    def check_list_of_constraint_clauses(
        self, list_of_constraint_clauses, type_checker, context_error_message
    ):
        idx = 0
        for constraint_clause in list_of_constraint_clauses:
            self.check_constraint_clause(
                constraint_clause,
                type_checker,
                context_error_message + "[" + str(idx) + "]",
            )
            idx += 1

    # TBR?
    def check_constraint_clauses(self, definition, type_checker, context_error_message):
        constraints = definition.get(syntax.CONSTRAINTS) if isinstance(definition, dict) else None
        if constraints is not None:
            self.check_list_of_constraint_clauses(
                constraints,
                type_checker,
                context_error_message + ":" + syntax.CONSTRAINTS,
            )

    def check_yaml_type(
        self,
        definition,
        context_error_message
    ):
        if self.configuration.get(
            TYPE_SYSTEM,
            "warning-on-definitions-allowing-negative-values"
        ):
            definition_type = definition.get(syntax.TYPE)
            if definition_type in [ "integer", "float" ]:
                if definition.get(syntax.CONSTRAINTS) is None:
                    self.warning(
                        context_error_message
                        + ":type: "
                        + definition_type
                        + " - no constraints then negative values allowed",
                        definition_type
                    )

    def check_property_definition(
        self,
        property_name,
        property_definition,
        previous_property_definition,
        context_error_message,
    ):
        # normalize
        if not isinstance(property_definition, dict):
            property_definition = { "value": property_definition }
        # check type
        self.check_type_in_definition(
            "data",
            syntax.TYPE,
            property_definition,
            previous_property_definition,
            context_error_message,
        )
        self.check_yaml_type(property_definition, context_error_message)

        # check description - nothing to do
        # check required
        if previous_property_definition is not PREVIOUSLY_UNDEFINED:
            if (is_required(previous_property_definition)
                and is_required(property_definition) is False
            ):
                self.error(
                    context_error_message
                    + ":"
                    + syntax.REQUIRED
                    + ": "
                    + str(property_definition.get(syntax.REQUIRED, True))
                    + " - previously declared as required",
                    property_definition,
                )
        # check default
        if 'default' in property_definition:
            default = property_definition.get(syntax.DEFAULT)
            self.check_value(
                default,
                property_definition,
                previous_property_definition,
                context_error_message + ":" + syntax.DEFAULT,
            )
        # check status - nothing to do
        # check constraints
        type_checker = self.get_type_checker(
            property_definition, previous_property_definition, context_error_message
        )
        self.check_constraint_clauses(
            property_definition, type_checker, context_error_message
        )
        # check key_schema
        self.check_schema_definition(
            syntax.KEY_SCHEMA,
            property_definition,
            previous_property_definition,
            context_error_message,
        )
        # check entry_schema
        self.check_schema_definition(
            syntax.ENTRY_SCHEMA,
            property_definition,
            previous_property_definition,
            context_error_message,
        )
        # check external_schema # TODO
        self.unchecked(
            property_definition, syntax.EXTERNAL_SCHEMA, context_error_message
        )
        # check metadata - nothing to do
        # check value
        if syntax.VALUE in property_definition:
            value = property_definition.get(syntax.VALUE)
            self.check_value_assignment(
                property_name,
                value,
                merge_dict(property_definition, previous_property_definition),
                context_error_message + ":" + syntax.VALUE,
            )

    def check_requirement_definition(
        self,
        requirement_name,
        requirement_definition,
        previous_requirement_definition,
        context_error_message,
    ):
        # check description - nothing to do

        # check capability
        (
            checked,
            requirement_capability,
            requirement_capability_type,
        ) = self.check_type_in_definition(
            "capability",
            syntax.CAPABILITY,
            requirement_definition,
            previous_requirement_definition,
            context_error_message,
        )
        if checked is False:
            # capability undefined or not a capability type
            requirement_capability = None
        else:
            valid_source_types = requirement_capability_type.get(
                syntax.VALID_SOURCE_TYPES
            )
            if not self.check_type_compatible_with_valid_source_types(
                self.current_type_name, valid_source_types
            ):
                self.error(
                    context_error_message
                    + ":capability: "
                    + requirement_capability
                    + " - "
                    + self.current_type_name
                    + " incompatible with valid source types "
                    + str(valid_source_types)
                    + " of "
                    + requirement_capability,
                    requirement_capability,
                )

        # check node
        if self.check_type(
            "node",
            requirement_definition.get(syntax.NODE),
            previous_requirement_definition.get(syntax.NODE),
            context_error_message + ":" + syntax.NODE,
        ):
            if requirement_capability is not None:
                requirement_node = syntax.get_requirement_node_type(
                    requirement_definition
                )
                node_type = self.type_system.merge_type(requirement_node)
                capability_not_compatible = True
                for cap_name, cap_def in syntax.get_capabilities(node_type).items():
                    if self.type_system.is_derived_from(
                        syntax.get_capability_type(cap_def), requirement_capability
                    ):
                        cap_valid_source_types = (
                            cap_def.get(syntax.VALID_SOURCE_TYPES)
                            if isinstance(cap_def, dict)
                            else []
                        )
                        if self.check_type_compatible_with_valid_source_types(
                            self.current_type_name, cap_valid_source_types
                        ):
                            capability_not_compatible = False
                            break
                if capability_not_compatible:
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.NODE
                        + ": "
                        + requirement_node
                        + " - no capability compatible with "
                        + requirement_capability,
                        requirement_node,
                    )

        # check relationship
        requirement_relationship = syntax.get_requirement_relationship(
            requirement_definition
        )
        if requirement_relationship is None:
            # relationship undefined
            if requirement_capability != None:
                # but capability defined
                previous_relationship = syntax.get_requirement_relationship(
                    previous_requirement_definition
                )
                if previous_relationship != None:
                    # Check if capability is compatible with previous defined relationship
                    if isinstance(previous_relationship, str):
                        relationship_type_name = previous_relationship
                    else:
                        relationship_type_name = previous_relationship.get(TYPE)
                    if not self.type_system.is_relationship_type_compatible_with_capability_type(
                        relationship_type_name, requirement_capability
                    ):
                        self.error(
                            context_error_message
                            + ":"
                            + syntax.CAPABILITY
                            + ": "
                            + requirement_capability
                            + " - incompatible with "
                            + relationship_type_name,
                            requirement_capability
                        )
                    else:
                        self.info(
                            context_error_message
                            + ":"
                            + syntax.CAPABILITY
                            + ": "
                            + requirement_capability
                            + " - compatible with "
                            + relationship_type_name,
                            requirement_capability
                        )
                else:
                    # Search relationship types compatible with defined capability
                    self.search_relationship_types_compatible_with_capability_type(
                        requirement_capability, context_error_message + ":relationship"
                    )
        else:
            # relationship defined

            # normalize when the short notation is used
            if isinstance(requirement_relationship, str):
                requirement_relationship = {syntax.TYPE: requirement_relationship}
            previous_requirement_relationship = previous_requirement_definition.get(
                syntax.RELATIONSHIP, {}
            )
            if isinstance(previous_requirement_relationship, str):
                previous_requirement_relationship = {
                    syntax.TYPE: previous_requirement_relationship
                }

            # check relationship type
            (
                checked,
                requirement_relationship_type_name,
                merged_definition,
            ) = self.check_type_in_definition(
                "relationship",
                syntax.TYPE,
                requirement_relationship,
                previous_requirement_relationship,
                context_error_message + ":" + syntax.RELATIONSHIP,
            )

            # check that capability is compatible with requirement type valid target types
            valid_target_types = merged_definition.get(syntax.VALID_TARGET_TYPES)
            if requirement_capability is not None and valid_target_types is not None:
                # Check that requirement_capability is compatible with at least one
                # requirement_relationship valid target type
                capability_not_compatible = True
                for valid_target_type in valid_target_types:
                    if self.type_system.is_derived_from(
                        requirement_capability, valid_target_type
                    ):
                        capability_not_compatible = False
                        break
                if capability_not_compatible:
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.RELATIONSHIP
                        + ":"
                        + syntax.TYPE
                        + ": "
                        + requirement_relationship_type_name
                        + " - no valid target type compatible with "
                        + requirement_capability,
                        requirement_relationship_type_name
                    )

            # check relationship interfaces
            self.iterate_over_map_of_definitions(
                self.check_interface_definition,
                syntax.INTERFACES,
                requirement_relationship,
                merged_definition,
                requirement_relationship_type_name,
                context_error_message + ":" + syntax.RELATIONSHIP,
            )

        # check node_filter # TODO added in TOSCA 2.0
        self.unchecked(
            requirement_definition, syntax.NODE_FILTER, context_error_message
        )

        # check occurrences
        self.check_occurrences(
            requirement_definition,
            previous_requirement_definition,
            [1, 1],
            context_error_message,
        )

    def check_occurrences(
        self,
        definition,
        previous_definition,
        default_occurrences,
        context_error_message,
    ):
        occurrences = definition.get(syntax.OCCURRENCES)
        if occurrences is None:
            return

        # check lower and upper occurrences
        if occurrences[1] != syntax.UNBOUNDED and occurrences[1] < occurrences[0]:
            self.error(
                context_error_message
                + ":"
                + syntax.OCCURRENCES
                + ": "
                + str(occurrences)
                + " - lower occurrence can not be greater than upper occurrence",
                occurrences,
            )

        if previous_definition is not PREVIOUSLY_UNDEFINED:
            previous_occurrences = previous_definition.get(
                syntax.OCCURRENCES, default_occurrences
            )
            # check lower occurrence
            if occurrences[0] < previous_occurrences[0]:
                self.error(
                    context_error_message
                    + ":"
                    + syntax.OCCURRENCES
                    + ": "
                    + str(occurrences)
                    + " - lower occurrence can not be less than "
                    + str(previous_occurrences[0]),
                    occurrences,
                )
            # check upper occurrence
            if previous_occurrences[1] != syntax.UNBOUNDED:
                # then upper previous occurrence is a positive integer
                if (
                    occurrences[1] == syntax.UNBOUNDED
                    or occurrences[1] > previous_occurrences[1]
                ):
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.OCCURRENCES
                        + ": "
                        + str(occurrences)
                        + " - upper occurrence can not be greater than "
                        + str(previous_occurrences[1]),
                        occurrences,
                    )

    def check_capability_definition(
        self,
        capability_name,
        capability_definition,
        previous_capability_definition,
        context_error_message,
    ):
        # check description - nothing to do

        # Normalize capability_definition and previous_capability_definition
        if isinstance(capability_definition, str):
            capability_definition = {syntax.TYPE: capability_definition}
        if isinstance(previous_capability_definition, str):
            previous_capability_definition = {
                syntax.TYPE: previous_capability_definition
            }

        # check type
        checked, capability_type_name, capability_type = self.check_type_in_definition(
            "capability",
            syntax.TYPE,
            capability_definition,
            previous_capability_definition,
            context_error_message,
        )

        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            capability_definition,
            capability_type,
            capability_type_name,
            context_error_message,
        )
        # check attributes
        self.iterate_over_map_of_definitions(
            self.check_attribute_definition,
            syntax.ATTRIBUTES,
            capability_definition,
            capability_type,
            capability_type_name,
            context_error_message,
        )

        # check valid_source_types
        if capability_type_name is not None:

            def check_valid_source_type(valid_source_type, context_error_message):
                node_type = self.type_system.merge_type(valid_source_type)
                # check each valid_source_type has at least a requirement with
                # capability compatible with capability_type_name
                requirement_not_found = True
                for (
                    requirement_name,
                    requirement_definition,
                ) in syntax.get_requirements_dict(node_type).items():
                    if self.type_system.is_derived_from(
                        capability_type_name,
                        syntax.get_requirement_capability(requirement_definition),
                    ):
                        requirement_not_found = False
                        break
                if requirement_not_found:
                    self.error(
                        context_error_message
                        + valid_source_type
                        + " - no requirement compatible with "
                        + capability_type_name,
                        valid_source_type,
                    )

        else:
            check_valid_source_type = None
        self.check_types_in_definition(
            "node",
            syntax.VALID_SOURCE_TYPES,
            capability_definition,
            previous_capability_definition,
            context_error_message,
            check_valid_source_type,
        )

        # check occurrences
        self.check_occurrences(
            capability_definition,
            previous_capability_definition,
            [1, syntax.UNBOUNDED],
            context_error_message,
        )

    def check_interface_definition(
        self,
        interface_name,
        interface_definition,
        previous_interface_definition,
        context_error_message,
    ):
        # check description - nothing to do
        # check type
        checked, interface_type_name, interface_type = self.check_type_in_definition(
            "interface",
            syntax.TYPE,
            interface_definition,
            previous_interface_definition,
            context_error_message,
        )
        # check inputs
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.INPUTS,
            interface_definition,
            interface_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check operations
        self.check_operations(
            interface_definition,
            interface_type,
            interface_type_name,
            context_error_message,
        )
        # check notifications
        self.iterate_over_map_of_definitions(
            self.check_notification_definition,
            syntax.NOTIFICATIONS,
            interface_definition,
            interface_type,
            interface_type_name,
            context_error_message,
        )

    # TBR
    def check_operations(
        self, definition, previous_definition, mode, context_error_message
    ):
        # normalize operations
        operations = syntax.get_operations(definition)
        previous_operations = syntax.get_operations(previous_definition)

        # check operation
        self.iterate_over_map_of_definitions(
            self.check_operation_definition,
            syntax.OPERATIONS,
            operations,
            previous_operations,
            mode,
            context_error_message,
        )

    def check_operation_definition(
        self,
        operation_name,
        operation_definition,
        previous_operation_definition,
        context_error_message,
    ):
        # check the short notation
        if isinstance(operation_definition, str):
            self.check_operation_implementation_definition(
                operation_definition, context_error_message
            )
            return
        # check the extended notation
        # check description - nothing to do
        # check implementation
        implementation = operation_definition.get(syntax.IMPLEMENTATION)
        if implementation is not None:
            self.check_operation_implementation_definition(
                implementation, context_error_message + ":" + syntax.IMPLEMENTATION
            )
        # check inputs
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.INPUTS,
            operation_definition,
            previous_operation_definition,
            REFINE_OR_NEW,
            context_error_message,
        )

        # check outputs
        self.iterate_over_map_of_definitions(
            self.check_output_notification_definition,
            syntax.OUTPUTS,
            operation_definition,
            previous_operation_definition,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_operation_implementation_definition(
        self, operation_implementation_definition, context_error_message
    ):
        # check the short notation
        if isinstance(operation_implementation_definition, str):
            self.check_artifact_definition(
                "", operation_implementation_definition, {}, context_error_message
            )
            return

        # check the extended notation
        # check primary
        primary = operation_implementation_definition.get(syntax.PRIMARY)
        if primary is not None:
            self.check_artifact_definition(
                syntax.PRIMARY,
                primary,
                {},
                context_error_message + ":" + syntax.PRIMARY,
            )
        # check dependencies
        idx = 0
        for dependency in operation_implementation_definition.get(
            syntax.DEPENDENCIES, []
        ):
            dependency_name = syntax.DEPENDENCIES + "[" + str(idx) + "]"
            self.check_artifact_definition(
                dependency_name,
                dependency,
                {},
                context_error_message + ":" + dependency_name,
            )
            idx += 1
        # check timeout - nothing to do
        # check operation_host
        operation_host = operation_implementation_definition.get("operation_host")
        if operation_host is not None:
            if operation_host not in self.current_allowed_operation_host_keynames:
                self.error(
                    context_error_message
                    + ":operation_host: "
                    + operation_host
                    + " - "
                    + array_to_string_with_or_separator(
                        self.current_allowed_operation_host_keynames)
                    + " expected",
                    operation_host,
                )

    def check_notification_definition(
        self,
        notification_name,
        notification_definition,
        previous_notification_definition,
        context_error_message,
    ):
        # check the short notation
        if isinstance(notification_definition, str):
            self.check_notification_implementation_definition(
                notification_definition, context_error_message
            )
            return
        # check the extended notation
        # check description - nothing to do
        # check implementation
        implementation = notification_definition.get(syntax.IMPLEMENTATION)
        if implementation is not None:
            self.check_notification_implementation_definition(
                implementation, context_error_message + ":" + syntax.IMPLEMENTATION
            )
        # check outputs
        self.iterate_over_map_of_definitions(
            self.check_output_notification_definition,
            syntax.OUTPUTS,
            notification_definition,
            previous_notification_definition,
            REFINE_OR_NEW,
            context_error_message,
        )

    check_notification_implementation_definition = (
        check_operation_implementation_definition
    )

    def check_notification_assignment(
        self,
        notification_name,
        notification_assignment,
        notification_definition,
        context_error_message,
    ):
        # check the short notation
        if isinstance(notification_assignment, str):
            self.check_artifact_definition(
                "", notification_assignment, {}, context_error_message
            )
            return

        # check the extended notation
        # check primary
        primary = notification_assignment.get(syntax.PRIMARY)
        if primary is not None:
            self.check_artifact_definition(
                syntax.PRIMARY,
                primary,
                {},
                context_error_message + ":" + syntax.PRIMARY,
            )
        # check dependencies
        idx = 0
        for dependency in notification_assignment.get(
            syntax.DEPENDENCIES, []
        ):
            dependency_name = syntax.DEPENDENCIES + "[" + str(idx) + "]"
            self.check_artifact_definition(
                dependency_name,
                dependency,
                {},
                context_error_message + ":" + dependency_name,
            )
            idx += 1

    def check_output_notification_definition(
        self,
        output_name,
        output_definition,
        previous_output_definition,
        context_error_message,
    ):
        if isinstance(output_definition, list):
            # TOSCA 1.3 grammar
            self.check_attribute_mapping_definition(
                output_name,
                output_definition,
                previous_output_definition,
                context_error_message,
            )
        elif isinstance(output_definition, dict):
            # TOSCA 2.0 grammar
            self.check_parameter_definition(
                output_name, output_definition, context_error_message
            )
        else:
            self.error(
                context_error_message
                + ": "
                + str(output_definition)
                + " - unexpected grammar",
                output_definition
            )

    def check_attribute_mapping_definition(
        self,
        attribute_mapping_name,
        attribute_mapping_definition,
        previous_attribute_mapping_definition,
        context_error_message,
    ):
        if len(attribute_mapping_definition) != 2:
            self.error(
                context_error_message
                + ": "
                + str(attribute_mapping_definition)
                + " - currently unchecked",
                attribute_mapping_definition,
            )
            return
        if len(attribute_mapping_definition) == 2:
            keyword = attribute_mapping_definition[0]
            type_definition = self.reserved_function_keywords.get(keyword)
            if type_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(attribute_mapping_definition)
                    + " - "
                    + keyword
                    + " undefined",
                    attribute_mapping_definition,
                )
                return
            attribute_name = attribute_mapping_definition[1]
            attribute_definition = type_definition.get(syntax.ATTRIBUTES, {}).get(
                attribute_name
            )
            if attribute_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(attribute_mapping_definition)
                    + " - "
                    + attribute_name
                    + " attribute undefined",
                    attribute_mapping_definition,
                )
                return
            return

    def check_artifact_definition(
        self,
        artifact_name,
        artifact_definition,
        previous_artifact_definition,
        context_error_message,
    ):
        # if file and no type then try to find an appropriate type
        def check_file(file, context_error_message):
            if (
                self.reserved_function_keywords.get("SELF", {})
                .get(syntax.ARTIFACTS, {})
                .get(file)
                is not None
            ):
                self.info(
                    context_error_message
                    + ": "
                    + file
                    + " - artifact found",
                    file)
            else:
                artifact_type_name = self.type_system.get_artifact_type_by_filename(
                    file
                )
                if artifact_type_name is None:
                    self.warning(
                        context_error_message
                        + ": "
                        + file
                        + " - no artifact type found",
                        file,
                    )
                else:
                    self.info(
                        context_error_message
                        + ": "
                        + file
                        + " - "
                        + artifact_type_name
                        + " found",
                        file
                    )

        # check the short notation
        if isinstance(artifact_definition, str):
            check_file(artifact_definition, context_error_message)
            return

        # check type
        checked, artifact_type_name, artifact_type = self.check_type_in_definition(
            "artifact",
            syntax.TYPE,
            artifact_definition,
            {syntax.TYPE: previous_artifact_definition.get(syntax.TYPE)},
            context_error_message,
        )

        # check file
        artifact_file = artifact_definition.get(syntax.FILE)
        if artifact_file is not None:
            if (
                self.reserved_function_keywords.get("SELF", {})
                .get(syntax.ARTIFACTS, {})
                .get(artifact_file)
                is not None
            ):
                self.info(
                    context_error_message
                    + ":"
                    + syntax.FILE
                    + ": "
                    + artifact_file
                    + " - artifact found",
                    artifact_file,
                )
            else:
                # check that the artifact file is supported by the artifact type
                found = True
                for file_ext in artifact_type.get(syntax.FILE_EXT, []):
                    found = artifact_file.endswith("." + file_ext)
                    if found:
                        break
                if not found:
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.FILE
                        + ": "
                        + artifact_file
                        + " - file extension not in %s as expected for %s"
                        % (artifact_type.get(syntax.FILE_EXT), artifact_type_name),
                        artifact_file
                    )

            # check that the file exists
            # self.warning(context_error_message + ':' + syntax.FILE + ': ' + artifact_definition.get(syntax.FILE) + ' - file currently unchecked')

        # check repository
        repository = artifact_definition.get(syntax.REPOSITORY)
        if repository is not None:
            if (
                self.tosca_service_template.get_yaml()
                .get(syntax.REPOSITORIES, {})
                .get(repository)
                is None
            ):
                self.error(
                    context_error_message
                    + ":"
                    + syntax.REPOSITORY
                    + ": "
                    + repository
                    + " - repository not found",
                    repository,
                )
        # check description - nothing to do
        # check deploy_path - nothing to do
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            artifact_definition,
            artifact_type,
            artifact_type_name,
            context_error_message,
        )
        self.check_required_properties(
            artifact_definition, artifact_type, context_error_message
        )

    def check_condition_clause_definition(
        self, condition_clause_definition, context_error_message
    ):
        def check_attribute_constraints(
            attribute_name, list_of_constraint_clauses, cem
        ):
            if len(self.current_targets) != 1:
                self.error(
                    cem
                    + ":"
                    + str(list_of_constraint_clauses)
                    + " - unchecked because several targets, i.e. "
                    + str(self.current_targets),
                    list_of_constraint_clauses,
                )
                return
            # targets contains only one node
            target_template_type = self.current_targets_condition_type[0]
            attribute_definition = target_template_type.get(syntax.ATTRIBUTES, {}).get(
                attribute_name
            )
            if attribute_definition is None:
                attribute_definition = target_template_type.get(
                    syntax.PROPERTIES, {}
                ).get(attribute_name)
            if attribute_definition is None:
                self.error(
                    cem
                    + " - "
                    + attribute_name
                    + " attribute undefined in "
                    + self.current_targets[0],
                    attribute_name,
                )
                return
            self.info(
                cem
                + " - "
                + attribute_name
                + " attribute defined in "
                + self.current_targets[0],
                attribute_name,
            )
            type_checker = self.get_type_checker(attribute_definition, {}, cem)
            self.check_list_of_constraint_clauses(
                list_of_constraint_clauses, type_checker, cem
            )

        for key, value in condition_clause_definition.items():
            cem = context_error_message + ":" + key
            if key in ["and", "or", "not"]:
                idx = 0
                for cc in value:
                    self.check_condition_clause_definition(
                        cc, cem + "[" + str(idx) + "]"
                    )
                    idx += 1
            elif key == "assert":
                idx = 0
                for cc in value:
                    for k, v in cc.items():
                        check_attribute_constraints(
                            k, v, cem + "[" + str(idx) + "]" + ":" + k
                        )
                idx += 1
            else:
                check_attribute_constraints(key, value, cem)

    def check_activity_definition(self, activity_definition, context_error_message):
        ACTIVITY_CHECKERS = {
            "delegate": self.check_delegate_activity,
            "set_state": self.check_set_state_activity,
            "call_operation": self.check_call_operation_activity,
            "inline": self.check_inline_activity,
        }
        for activity_name, activity in activity_definition.items():
            ACTIVITY_CHECKERS[activity_name](
                activity, context_error_message + ":" + activity_name
            )

    def check_delegate_activity(self, delegate, context_error_message):
        def check_workflow_and_inputs(workflow_name, delegate_definition):
            workflow_definition = self.configuration.get(
                TYPE_SYSTEM, "predefined_workflows"
            ).get(workflow_name)
            if workflow_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + workflow_name
                    + " - workflow undefined",
                    workflow_name,
                )
            else:
                self.iterate_over_map_of_assignments(
                    self.check_parameter_assignment,
                    syntax.INPUTS,
                    delegate_definition,
                    workflow_definition,
                    workflow_name,
                    context_error_message,
                )
                self.check_required_parameters(
                    delegate_definition, workflow_definition, context_error_message
                )

        # check the short notation
        if isinstance(delegate, str):
            check_workflow_and_inputs(delegate, {})
            return
        # check the extended notation
        workflow_name = delegate.get("workflow")
        if workflow_name is None:
            self.error(context_error_message + " - workflow name expected", delegate)
        else:
            check_workflow_and_inputs(workflow_name, delegate)

    def check_set_state_activity(self, set_state, context_error_message):
        current_target_type = self.current_targets_activity_type[0]
        attribute_definition = current_target_type.get(syntax.ATTRIBUTES, {}).get(
            "state"
        )
        if attribute_definition is None:
            self.error(
                context_error_message
                + ": "
                + set_state
                + " - state attribute undefined",
                set_state,
            )
            return
        type_checker = self.get_type_checker(
            attribute_definition, {}, context_error_message
        )
        type_checker.check_type(set_state, self, context_error_message)

    def check_call_operation_activity(self, call_operation, context_error_message):
        def check_operation(operation, context_error_message):
            # split <interface_name>.<operation_name>
            tmp = operation.split(".")
            if len(tmp) != 2:
                self.error(
                    context_error_message
                    + ": "
                    + operation
                    + " - <interface_name>.<operation_name> expected",
                    operation,
                )
                return {}
            interface_name = tmp[0]
            operation_name = tmp[1]
            # check interface_name
            interface_definition = (
                self.current_targets_activity_type[0]
                .get(syntax.INTERFACES, {})
                .get(interface_name)
            )
            if interface_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + operation
                    + " - "
                    + interface_name
                    + " interface undefined in "
                    + self.current_targets[0],
                    operation,
                )
                return {}
            checked, unused, interface_type = self.check_type_in_definition(
                "interface",
                syntax.TYPE,
                interface_definition,
                interface_definition,
                context_error_message,
            )
            # check operation_name
            operation_definition = syntax.get_operations(interface_type).get(
                syntax.OPERATIONS, {}
            ).get(operation_name)
            if operation_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + operation
                    + " - "
                    + operation_name
                    + " operation undefined in "
                    + self.current_targets[0]
                    + ".interfaces."
                    + interface_name
                    + " interface",
                    operation,
                )
                return {}
            return operation_definition

        # check the short notation
        if isinstance(call_operation, str):
            operation_definition = check_operation(
                call_operation, context_error_message
            )
            self.check_required_parameters(
                {}, operation_definition, context_error_message + ": " + call_operation
            )
            return
        # check the extended notation
        # check operation

        operation_name = call_operation.get("operation")
        if operation_name is None:
            self.error(context_error_message + ":operation - expected", call_operation)
            return
        operation_definition = check_operation(
            operation_name, context_error_message + ":operation"
        )
        # check inputs
        self.iterate_over_map_of_assignments(
            self.check_parameter_assignment,
            syntax.INPUTS,
            call_operation,
            operation_definition,
            operation_name,
            context_error_message,
        )
        self.check_required_parameters(
            call_operation,
            operation_definition,
            context_error_message + ": " + operation_name,
        )

    def check_inline_activity(self, inline, context_error_message):
        def check_workflow_and_inputs(workflow_name, delegate_definition):
            workflow_definition = (
                self.get_topology_template()
                .get(syntax.WORKFLOWS, {})
                .get(workflow_name)
            )
            if workflow_definition is None:
                workflow_definition = self.configuration.get(
                    TYPE_SYSTEM, "predefined_workflows"
                ).get(workflow_name)
            if workflow_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + workflow_name
                    + " - workflow undefined",
                    workflow_name,
                )
            else:
                self.iterate_over_map_of_assignments(
                    self.check_parameter_assignment,
                    syntax.INPUTS,
                    delegate_definition,
                    workflow_definition,
                    workflow_name,
                    context_error_message,
                )
                self.check_required_parameters(
                    delegate_definition, workflow_definition, context_error_message
                )

        # check the short notation
        if isinstance(inline, str):
            check_workflow_and_inputs(inline, {})
            return
        # check the extended notation
        workflow_name = inline.get("workflow")
        if workflow_name is None:
            self.error(context_error_message + " - workflow name expected", inline)
        else:
            check_workflow_and_inputs(workflow_name, inline)

    def check_artifact_type(
        self,
        artifact_type_name,
        artifact_type,
        derived_from_artifact_type,
        context_error_message,
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check mime_type - nothing to do
        # check file_ext # TODO already done previously move previous code here
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            artifact_type,
            derived_from_artifact_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_data_type(
        self, data_type_name, data_type, derived_from_data_type, context_error_message
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check constraints
        type_checker = self.get_type_checker(
            {syntax.TYPE: data_type.get(syntax.DERIVED_FROM)}, {}, context_error_message
        )
        self.check_constraint_clauses(data_type, type_checker, context_error_message)
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            data_type,
            derived_from_data_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_capability_type(
        self,
        capability_type_name,
        capability_type,
        derived_from_capability_type,
        context_error_message,
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            capability_type,
            derived_from_capability_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check attributes
        self.iterate_over_map_of_definitions(
            self.check_attribute_definition,
            syntax.ATTRIBUTES,
            capability_type,
            derived_from_capability_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check valid_source_types
        self.check_types_in_definition(
            "node",
            syntax.VALID_SOURCE_TYPES,
            capability_type,
            derived_from_capability_type,
            context_error_message,
        )

    def check_interface_type(
        self,
        interface_type_name,
        interface_type,
        derived_from_interface_type,
        context_error_message,
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check inputs
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.INPUTS,
            interface_type,
            derived_from_interface_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check operations
        self.check_operations(
            interface_type,
            derived_from_interface_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check notifications
        self.iterate_over_map_of_definitions(
            self.check_notification_definition,
            syntax.NOTIFICATIONS,
            interface_type,
            derived_from_interface_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_relationship_type(
        self,
        relationship_type_name,
        relationship_type,
        derived_from_relationship_type,
        context_error_message,
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_map_of_definitions(
            self.check_attribute_definition,
            syntax.ATTRIBUTES,
            relationship_type,
            derived_from_relationship_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            relationship_type,
            derived_from_relationship_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check interfaces
        self.iterate_over_map_of_definitions(
            self.check_interface_definition,
            syntax.INTERFACES,
            relationship_type,
            derived_from_relationship_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check valid_target_types
        self.check_types_in_definition(
            "capability",
            syntax.VALID_TARGET_TYPES,
            relationship_type,
            derived_from_relationship_type,
            context_error_message,
        )

    def check_node_type(
        self, node_type_name, node_type, derived_from_node_type, context_error_message
    ):
        # set values of reserved function keywords
        self.reserved_function_keywords = {
            "SELF": merge_dict({ "type": node_type_name }, node_type)
        }
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_map_of_definitions(
            self.check_attribute_definition,
            syntax.ATTRIBUTES,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # normalize requirements
        requirements = node_type.get(syntax.REQUIREMENTS)
        if requirements is not None:
            node_type[syntax.REQUIREMENTS] = syntax.get_requirements_dict(node_type)
        # check requirements
        self.iterate_over_map_of_definitions(
            self.check_requirement_definition,
            syntax.REQUIREMENTS,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check capabilities
        self.iterate_over_map_of_definitions(
            self.check_capability_definition,
            syntax.CAPABILITIES,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check interfaces
        self.iterate_over_map_of_definitions(
            self.check_interface_definition,
            syntax.INTERFACES,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check artifacts
        self.iterate_over_map_of_definitions(
            self.check_artifact_definition,
            syntax.ARTIFACTS,
            node_type,
            derived_from_node_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # reset values of reserved function keywords
        self.reserved_function_keywords = {}

    def check_group_type(
        self,
        group_type_name,
        group_type,
        derived_from_group_type,
        context_error_message,
    ):
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check attributes
        self.iterate_over_map_of_definitions(
            self.check_attribute_definition,
            syntax.ATTRIBUTES,
            group_type,
            derived_from_group_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            group_type,
            derived_from_group_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check members
        self.check_types_in_definition(
            "node",
            syntax.MEMBERS,
            group_type,
            derived_from_group_type,
            context_error_message,
        )
        # normalize requirements
        requirements = group_type.get(syntax.REQUIREMENTS)
        if requirements is not None:
            group_type[syntax.REQUIREMENTS] = syntax.get_requirements_dict(group_type)
        # check requirements
        self.iterate_over_map_of_definitions(
            self.check_requirement_definition,
            syntax.REQUIREMENTS,
            group_type,
            derived_from_group_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check capabilities
        self.iterate_over_map_of_definitions(
            self.check_capability_definition,
            syntax.CAPABILITIES,
            group_type,
            derived_from_group_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check interfaces
        self.iterate_over_map_of_definitions(
            self.check_interface_definition,
            syntax.INTERFACES,
            group_type,
            derived_from_group_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_policy_type(
        self,
        policy_type_name,
        policy_type,
        derived_from_policy_type,
        context_error_message,
    ):
        self.reserved_function_keywords = {
            'SELF': { 'type': policy_type_name }
        }
        # check version - nothing to do
        # check metadata - nothing to do
        # check description - nothing to do
        # check properties
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.PROPERTIES,
            policy_type,
            derived_from_policy_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        # check targets
        self.check_types_in_definition(
            ["node", "group"],
            syntax.TARGETS,
            policy_type,
            derived_from_policy_type,
            context_error_message,
        )
        self.current_targets = []
        self.current_targets_activity_type = []
        self.current_targets_condition_type = []
        targets = policy_type.get(syntax.TARGETS)
        if targets != None:
            self.current_targets = targets
            for idx, target in enumerate(targets):
                current_target_type = self.type_system.merge_type(
                    self.type_system.get_type_uri(target)
                )
                self.current_targets_activity_type.append(current_target_type)
                self.current_targets_condition_type.append(current_target_type)
        # check triggers
        self.iterate_over_map_of_definitions(
            self.check_trigger_definition,
            syntax.TRIGGERS,
            policy_type,
            derived_from_policy_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_topology_template(self, topology_template, context_error_message):
        def iterate_over_map(check_method, keyword):
            for name, value in topology_template.get(keyword, {}).items():
                check_method(
                    name, value, context_error_message + ":" + keyword + ":" + name
                )

        # check description - nothing to do
        # check inputs
        iterate_over_map(self.check_parameter_definition, syntax.INPUTS)
        # check node_templates
        iterate_over_map(self.check_node_template, syntax.NODE_TEMPLATES)
        # check relationship_templates
        iterate_over_map(
            self.check_relationship_template, syntax.RELATIONSHIP_TEMPLATES
        )
        # check groups
        iterate_over_map(self.check_group_definition, syntax.GROUPS)
        # check policies
        idx = 0
        for policy in topology_template.get(syntax.POLICIES, []):
            for policy_name, policy_definition in policy.items():
                self.check_policy_definition(
                    policy_name,
                    policy_definition,
                    context_error_message
                    + ":"
                    + syntax.POLICIES
                    + "["
                    + str(idx)
                    + "]"
                    + ":"
                    + policy_name,
                )
            idx += 1
        # check outputs
        iterate_over_map(self.check_output_parameter_definition, syntax.OUTPUTS)
        # check substitution_mappings
        substitution_mapping = topology_template.get(syntax.SUBSTITUTION_MAPPINGS)
        if substitution_mapping is not None:
            self.check_substitution_mapping(
                substitution_mapping,
                context_error_message + ":" + syntax.SUBSTITUTION_MAPPINGS,
            )
        # check workflows
        iterate_over_map(self.check_imperative_workflow_definition, syntax.WORKFLOWS)

        for req_id, requirement in self.all_the_node_template_requirements.items():
            cem = (
                "topology_template:node_templates:"
                + requirement.node_template_name
                + ":requirements:"
                + requirement.requirement_name
            )
            if requirement.connections < requirement.lower_bound:
                node_type_names = []
                # get the requirement node
                requirement_node = requirement.requirement_definition.get("node")
                if requirement_node is None:
                    # search all the node types which have a capability compatible with the requirement capability
                    requirement_capability = requirement.requirement_definition.get(
                        "capability"
                    )
                    for (
                        node_type_name,
                        node_type_def,
                    ) in self.type_system.node_types.items():
                        for cap_name, cap_def in node_type_def.get(
                            "capabilities", {}
                        ).items():
                            cap_type = syntax.get_capability_type(cap_def)
                            if self.type_system.is_derived_from(
                                cap_type, requirement_capability
                            ):
                                node_type_names.append(node_type_name)
                    if len(node_type_names) == 0:
                        self.error(
                            cem + " - no node type matching " + requirement_capability
                        )
                        continue
                else:
                    node_type_names.append(requirement_node)

                node_templates = []
                for node_type_name in node_type_names:
                    # search node templates of this type
                    node_templates.extend(
                        self.select_node_templates(node_type_name, None, cem)
                    )

                if len(node_templates) == 0:
                    self.error(
                        cem
                        + " - no node template matching "
                        + array_to_string_with_or_separator(node_type_names)
                    )
                    continue
                update_requirement_node = node_templates[0]
                if len(node_templates) == 1:
                    self.info(
                        cem + " - " + update_requirement_node + " node template found"
                    )
                else:
                    self.warning(
                        cem
                        + " - "
                        + array_to_string_with_or_separator(node_templates)
                        + " node templates found, then "
                        + update_requirement_node
                        + " selected"
                    )
                node_template = self.get_topology_template()["node_templates"][
                    requirement.node_template_name
                ]
                requirements = node_template.get("requirements")
                if requirements is None:
                    requirements = []
                    node_template["requirements"] = requirements
                requirements.append(
                    {requirement.requirement_name: update_requirement_node}
                )

            if (
                requirement.upper_bound != syntax.UNBOUNDED
                and requirement.connections > requirement.upper_bound
            ):
                self.error(
                    cem
                    + " - expected occurrences: "
                    + str(requirement.occurrences)
                    + " but "
                    + str(requirement.connections)
                    + " connections"
                    + " - too many connections"
                )

    def check_type_in_template(
        self, type_kinds, template, keyword, context_error_message
    ):
        type_name = template.get(keyword)
        checked = self.check_type_existence(
            type_kinds, type_name, context_error_message + ":" + keyword
        )
        the_type = self.type_system.merge_type(self.type_system.get_type_uri(type_name))
        return checked, type_name, the_type

    def has_no_default_value(self, definition):
        if "default" in definition:
            return False # default is set
        # default is not set
        # get the type definition
        type_def = self.type_system.merge_type(definition.get(syntax.TYPE))
        type_properties = type_def.get(syntax.PROPERTIES, {})
        if len(type_properties) == 0:  # no property
            return True  # no default value
        # the type has some properties
        # iterate over all properties
        for property_name, property_definition in type_properties.items():
            if (is_required(property_definition)
                and self.has_no_default_value(property_definition)
            ):
                return True  # this is a required property without a default value
        # all required properties have a default value
        return False

    def check_required_fields(
        self,
        keyword,
        kind,
        definition,
        definition_type,
        default_fields_definition,
        default_fields_definition_location,
        context_error_message,
    ):
        fields = definition.get(keyword, {})
        for field_name, field_definition in definition_type.get(keyword, {}).items():
            if (
                isinstance(field_definition, dict)
                and field_definition.get(syntax.TYPE) != None
                and field_definition.get(syntax.REQUIRED, True)
                and self.has_no_default_value(field_definition)
                and fields.get(field_name) is None
                and field_definition.get('value') is None
            ):
                default_field_definition = default_fields_definition.get(field_name)
                if default_field_definition is None:
                    self.error(
                        context_error_message
                        + " - "
                        + field_name
                        + " required "
                        + kind
                        + " unassigned",
                        definition if isinstance(definition, YamlCoord)
                            else self.reserved_function_keywords.get("SELF"),
                    )
                else:
                    self.info(
                        context_error_message
                        + " - required "
                        + field_name
                        + " "
                        + kind
                        + " found in "
                        + default_fields_definition_location,
                    )
                    if default_field_definition.get(syntax.REQUIRED, True) is False:
                        self.warning(
                            context_error_message
                            + " - "
                            + default_fields_definition_location
                            + ":"
                            + field_name
                            + " not required but required "
                            + kind
                            + " expected",
                            field_name,
                        )
                    expected_type_name = field_definition.get(syntax.TYPE, "string")
                    default_field_type = default_field_definition.get(
                        syntax.TYPE, "string"
                    )
                    if not self.type_system.is_derived_from(
                        expected_type_name, default_field_type
                    ):
                        self.error(
                            context_error_message
                            + " - "
                            + default_fields_definition_location
                            + ":"
                            + field_name
                            + " of type "
                            + default_field_type
                            + " found but type "
                            + expected_type_name
                            + " expected",
                            field_name,
                        )

    def check_required_properties(
        self, definition, definition_type, context_error_message
    ):
        self.check_required_fields(
            syntax.PROPERTIES,
            "property",
            definition,
            definition_type,
            {},
            None,
            context_error_message,
        )

    def check_required_parameters(
        self, definition, definition_type, context_error_message
    ):
        self.check_required_fields(
            syntax.INPUTS,
            "input",
            definition,
            definition_type,
            self.current_default_inputs,
            self.current_default_inputs_location,
            context_error_message,
        )

    def check_parameter_definition(
        self, parameter_name, parameter_definition, context_error_message
    ):
        # check type
        if parameter_definition.get(syntax.TYPE) is None:
            parameter_definition[syntax.TYPE] = "string"
        checked, data_type_name, data_type = self.check_type_in_template(
            "data", parameter_definition, syntax.TYPE, context_error_message
        )
        type_checker = self.get_type_checker(
            parameter_definition, {}, context_error_message
        )
        self.check_yaml_type(parameter_definition, context_error_message)

        # check description - nothing to do
        # check required - nothing to do
        # check default
        if "default" in parameter_definition:
            default = parameter_definition.get(syntax.DEFAULT)
            self.check_value(
                default,
                parameter_definition,
                {},
                context_error_message + ":" + syntax.DEFAULT,
            )
        # check status - nothing to do
        # check constraints
        self.check_constraint_clauses(
            parameter_definition, type_checker, context_error_message
        )
        # check key_schema
        self.check_schema_definition(
            syntax.KEY_SCHEMA, parameter_definition, {}, context_error_message
        )
        # check entry_schema
        self.check_schema_definition(
            syntax.ENTRY_SCHEMA, parameter_definition, {}, context_error_message
        )
        # check external_schema - TODO
        self.unchecked(
            parameter_definition, syntax.EXTERNAL_SCHEMA, context_error_message
        )
        # check metadata - nothing to do
        # check value
        if "value" in parameter_definition:
            value = parameter_definition.get(syntax.VALUE)
            self.check_value_assignment(
                syntax.VALUE,
                value,
                parameter_definition,
                context_error_message + ":" + syntax.VALUE,
            )

    def check_output_parameter_definition(
        self,
        parameter_name,
        parameter_definition,
        context_error_message
    ):
        if parameter_definition.get(syntax.TYPE) is None:
            value = parameter_definition.get('value')
            if value != None:
                # when type undefined and value defined then the output
                # parameter inherits the data type of the assigned value
                if isinstance(value, dict):
                    for tosca_function_name, tosca_function_parameters in value.items():
                        tosca_function = TOSCA_FUNCTIONS.get(tosca_function_name)
                        if tosca_function != None:
                            value_type = tosca_function.get_return_data_type(
                                                tosca_function_parameters,
                                                self,
                                                context_error_message + ':value'
                                            )
                            self.info(
                                "INJECT %s.type: %s"
                                % (context_error_message, value_type)
                            )
                            parameter_definition['type'] = value_type
                        break

        self.check_parameter_definition(
            parameter_name,
            parameter_definition,
            context_error_message
        )

    def iterate_over_map_of_assignments(
        self,
        method,
        keyword,
        template,
        template_type,
        template_type_name,
        context_error_message,
    ):
        context_error_message += ":" + keyword + ":"
        template_type_keyword = template_type.get(keyword, {})
        for key, value in template.get(keyword, {}).items():
            definition = template_type_keyword.get(key)
            if definition is None:
                if template_type_name != REFINE_OR_NEW:
                    self.error(
                        context_error_message
                        + key
                        + " - undefined in "
                        + template_type_name,
                        key,
                    )
                    continue
                definition = {}
            if method is not None:  # TBR
                method(key, value, definition, context_error_message + key)

    def check_value_assignment(self, name, value, definition, context_error_message):
        if isinstance(value, dict) and len(value) == 1:
            if "concat" in value:
                parameters = value["concat"]
                # check that parameters are a list of strings
                expected_type_of_parameters = {
                    "type": "list",
                    "entry_schema": {
                        "type": [
                            "string",
                            "integer",
                            # TODO: add other allowed yaml types
                        ],
                    },
                    "constraints": [{"min_length": 1}],
                }
                self.check_value_assignment(
                    "concat",
                    parameters,
                    expected_type_of_parameters,
                    context_error_message + ":concat",
                )

                # check that definition type is a string
                def_type = definition.get(syntax.TYPE)
                if def_type != None and not self.type_system.is_derived_from(
                    "string", def_type
                ):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - "
                        + def_type
                        + " type expected",
                        value
                    )
                    return

                return

            if 'join' in value:
                parameters = value['join']
                # check number of parameters
                if len(parameters) not in [1, 2]:
                    self.error(
                        context_error_message
                        + ': '
                        + str(value)
                        + ' - one or two parameters expected',
                        value)
                else:
                    # check the first mandatory parameter
                    expected_type = {
                        'type': 'list',
                        'entry_schema': {
                            'type': 'string'
                        },
                    }
                    self.check_value_assignment('join', parameters[0], expected_type, context_error_message + ':join[0]')

                    # check the second optional parameter
                    if len(parameters) == 2 and not isinstance(parameters[1], str):
                        self.error(
                            context_error_message
                            + ':join[1]: '
                            + str(parameters[1])
                            + ' - string expected',
                            parameters[1])

                # check that definition type is a string
                def_type = definition.get(syntax.TYPE)
                if def_type != None and not self.type_system.is_derived_from('string', def_type):
                    self.error(
                        context_error_message
                        + ': '
                        + str(value)
                        + ' - '
                        + def_type
                        + ' type expected',
                        value
                    )
                    return

                return

            if 'token' in value:
                parameters = value['token']
                # check number of parameters
                if len(parameters) != 3:
                    self.error(
                        context_error_message
                        + ': '
                        + str(value)
                        + ' - three parameters expected',
                        value
                    )
                else:
                    # check the first mandatory parameter
                    self.check_value_assignment('token', parameters[0], {'type': 'string'}, context_error_message + ':token[0]')
                    # check the second mandatory parameter
                    if not isinstance(parameters[1], str):
                        self.error(
                            context_error_message
                            + ':token[1]: '
                            + str(parameters[1])
                            + ' - string expected',
                            parameters[1]
                        )
                    # check the third mandatory parameter
                    if not isinstance(parameters[2], int):
                        self.error(
                            context_error_message
                            + ':token[2]: '
                            + str(parameters[2])
                            + ' - integer expected',
                            parameters[2]
                        )

                # check that definition type is a string
                def_type = definition.get(syntax.TYPE)
                if def_type != None and not self.type_system.is_derived_from('string', def_type):
                    self.error(
                        context_error_message
                        + ': '
                        + str(value)
                        + ' - '
                        + def_type
                        + ' type expected',
                        value
                    )
                    return

                return

            if syntax.GET_ARTIFACT in value:
                parameters = value[syntax.GET_ARTIFACT]
                if not isinstance(parameters, list):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - list expected",
                        value,
                    )
                    return
                if len(parameters) < 2:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - at least two parameters expected",
                        parameters,
                    )
                    return
                if len(parameters) > 5:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - no more than four parameters expected",
                        parameters,
                    )
                    return

                topology_template = self.get_topology_template()

                entity_name = parameters[0]
                if entity_name in ["SELF", "SOURCE", "TARGET", "HOST"]:
                    entity_template = self.reserved_function_keywords.get(entity_name)
                    if entity_template is None:
                        self.error(
                            context_error_message
                            + ": "
                            + str(value)
                            + " - "
                            + entity_name
                            + " reserved keyword undefined",
                            entity_name,
                        )
                    if entity_template == "UNKNOWN":
                        self.warning(
                            context_error_message
                            + ': '
                            + str(value)
                            + ' - '
                            + entity_name
                            + ' unknown, then no type checking',
                            entity_name
                        )
                        return
                else:
                    entity_template = topology_template.get(
                        syntax.NODE_TEMPLATES, {}
                    ).get(entity_name)
                    if entity_template is None:
                        entity_template = topology_template.get(
                            syntax.RELATIONSHIP_TEMPLATES, {}
                        ).get(entity_name)
                        if entity_template is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + entity_name
                                + " entity template undefined",
                                entity_name,
                            )

                if entity_template is not None:
                    artifact_name = parameters[1]
                    artifact = entity_template.get(syntax.ARTIFACTS, {}).get(
                        artifact_name
                    )
                    if artifact is None:
                        self.error(
                            context_error_message
                            + ": "
                            + str(value)
                            + " - "
                            + artifact_name
                            + " artifact undefined",
                            artifact_name,
                        )

                # check 3rd parameter
                if len(parameters) > 2 and not isinstance(parameters[2], str):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - location string expected",
                        parameters[2],
                    )

                # check 4th parameter
                if len(parameters) > 3 and not isinstance(parameters[3], bool):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - remove boolean expected",
                        parameters[3],
                    )

                return

            if syntax.GET_ATTRIBUTE in value:
                parameters = value[syntax.GET_ATTRIBUTE]
                if not isinstance(parameters, list):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - list expected",
                        parameters,
                    )
                    return
                if len(parameters) < 2:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - at least two parameters expected",
                        parameters,
                    )
                    return

                topology_template = self.get_topology_template()

                entity_name = parameters[0]
                if entity_name in ["SELF", "SOURCE", "TARGET", "HOST"]:
                    entity = self.reserved_function_keywords.get(entity_name)
                    if entity is None:
                        self.error(
                            context_error_message
                            + ": "
                            + str(value)
                            + " - "
                            + entity_name
                            + " reserved keyword undefined",
                            entity_name,
                        )
                        return
                    if entity == "UNKNOWN":
                        self.warning(
                            context_error_message
                            + ': '
                            + str(value)
                            + ' - ' + entity_name
                            + ' unknown, then no type checking',
                            value
                        )
                        return
                else:
                    entity = topology_template.get(syntax.NODE_TEMPLATES, {}).get(
                        entity_name
                    )
                    if entity is None:
                        entity = topology_template.get(
                            syntax.RELATIONSHIP_TEMPLATES, {}
                        ).get(entity_name)
                        if entity is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + entity_name
                                + " entity undefined",
                                entity_name,
                            )
                            return
                entity_type = self.type_system.merge_type(
                    self.type_system.get_type_uri(entity.get(syntax.TYPE))
                )

                attribute_value = None
                parameters_idx = 2

                attribute_name = parameters[1]

                def get_attribute_or_property(entity, name):
                    value = entity.get(syntax.ATTRIBUTES, {}).get(name)
                    if value is None:
                        value = entity.get(syntax.PROPERTIES, {}).get(name)
                    return value

                attribute_definition = get_attribute_or_property(
                                            entity_type,
                                            attribute_name
                                       )
                if attribute_definition != None:
                    attribute_value = get_attribute_or_property(entity, attribute_name)
                else:
                    capability_definition = entity_type.get(
                        syntax.CAPABILITIES, {}
                    ).get(attribute_name)
                    capability_value = entity.get(syntax.CAPABILITIES, {}).get(
                        attribute_name
                    )
                    if capability_definition != None:
                        capability_type = syntax.get_capability_type(
                            capability_definition
                        )
                        capability_definition_type = self.type_system.merge_type(
                            self.type_system.get_type_uri(capability_type)
                        )
                        if capability_definition_type is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + capability_type
                                + " capability type undefined",
                                value
                            )
                            return
                        attribute_name = parameters[2]
                        attribute_definition = get_attribute_or_property(
                                                    capability_definition_type,
                                                    attribute_name
                                                )
                        if attribute_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + attribute_name
                                + " attribute undefined in "
                                + capability_type,
                                value
                            )
                            return
                        if capability_value != None:
                            attribute_value = get_attribute_or_property(
                                                capability_value,
                                                attribute_name
                                              )
                    else:
                        requirement_definition = entity_type.get(
                            syntax.REQUIREMENTS, {}
                        ).get(attribute_name)
                        if requirement_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + attribute_name
                                + " capability or requirement undefined",
                                value
                            )
                            return
                        requirement = syntax.get_requirements_dict(entity).get(
                            attribute_name
                        )
                        requirement_capability = requirement_definition.get(
                            syntax.CAPABILITY
                        )
                        capability_definition_type = self.type_system.merge_type(
                            self.type_system.get_type_uri(requirement_capability)
                        )
                        capability_name = attribute_name  # TODO: could be different
                        attribute_name = parameters[2]
                        attribute_definition = get_attribute_or_property(
                                                capability_definition_type,
                                                attribute_name
                                               )
                        if attribute_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + attribute_name
                                + " attribute undefined in "
                                + requirement_capability,
                                value
                            )
                            return
                        requirement_node = syntax.get_requirement_node_template(
                            requirement
                        )
                        if requirement_node is None:
                            attribute_value = None
                        else:
                            entity = topology_template.get(
                                syntax.NODE_TEMPLATES, {}
                            ).get(requirement_node)
                            if entity is None:
                                attribute_value = None
                            else:
                                attribute_value = get_attribute_or_property(
                                                    entity
                                                    .get(syntax.CAPABILITIES, {})
                                                    .get(capability_name, {}),
                                                    attribute_name
                                )

                    parameters_idx = 3

                for parameter in parameters[parameters_idx:]:
                    t = attribute_definition.get(syntax.TYPE)
                    rt = self.get_root_data_type_name(t)
                    if rt == "map":
                        type_checker = self.get_type_checker(
                            {
                                syntax.TYPE: attribute_definition.get(
                                    syntax.KEY_SCHEMA, {}
                                ).get(syntax.TYPE, "string")
                            },
                            {},
                            context_error_message + ": " + str(value),
                        )
                        type_checker.check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        attribute_definition = attribute_definition.get(
                            syntax.ENTRY_SCHEMA
                        )
                        if attribute_value != None:
                            attribute_value = attribute_value.get(parameter)
                    elif rt == "list":
                        BASIC_TYPE_CHECKERS["integer"].check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        attribute_definition = attribute_definition.get(
                            syntax.ENTRY_SCHEMA
                        )
                        if attribute_value != None:
                            attribute_value = attribute_value[parameter]
                    else:
                        attribute_definition = (
                            self.type_system.merge_type(
                                self.type_system.get_type_uri(t)
                            )
                            .get(syntax.PROPERTIES, {})
                            .get(parameter)
                        )
                        if attribute_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + str(parameter)
                                + " property undefined",
                                parameter,
                            )
                            return
                        if attribute_value != None:
                            attribute_value = attribute_value.get(parameter)

                attribute_type = attribute_definition.get(syntax.TYPE)
                value_type = definition.get(syntax.TYPE)
                if value_type is not None and not self.type_system.is_derived_from(
                    attribute_type, value_type
                ):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - "
                        + attribute_type
                        + " type but "
                        + value_type
                        + " type expected",
                        attribute_type,
                    )
                    return

                # check if the assigned definition is required then the assigning attribute is required
                if (
                    attribute_value is None
                    and value_type is not None
                    and is_required(definition)
                    and is_required(attribute_definition) is False
                ):
                    self.warning(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - property "
                        + str(parameters)
                        + " is not required, but the actual value is expected from the system",
                        value
                    )
                return

            if syntax.GET_PROPERTY in value:
                parameters = value[syntax.GET_PROPERTY]
                if not isinstance(parameters, list):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - list expected",
                        parameters,
                    )
                    return
                if len(parameters) < 2:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - at least two parameters expected",
                        parameters,
                    )
                    return

                topology_template = self.get_topology_template()

                entity_name = parameters[0]
                if entity_name in ["SELF", "SOURCE", "TARGET", "HOST"]:
                    entity = self.reserved_function_keywords.get(entity_name)
                    if entity is None:
                        self.error(
                            context_error_message
                            + ": "
                            + str(value)
                            + " - "
                            + entity_name
                            + " reserved keyword undefined",
                            entity_name,
                        )
                        return
                    if entity == "UNKNOWN":
                        self.warning(
                            context_error_message
                            + ': '
                            + str(value)
                            + ' - '
                            + entity_name
                            + ' unknown, then no type checking',
                            value
                        )
                        return
                else:
                    entity = topology_template.get(syntax.NODE_TEMPLATES, {}).get(
                        entity_name
                    )
                    if entity is None:
                        entity = topology_template.get(
                            syntax.RELATIONSHIP_TEMPLATES, {}
                        ).get(entity_name)
                        if entity is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + entity_name
                                + " entity undefined",
                                entity_name,
                            )
                            return
                entity_type = self.type_system.merge_type(
                    self.type_system.get_type_uri(entity.get(syntax.TYPE))
                )

                property_value = None
                parameters_idx = 2

                property_name = parameters[1]
                property_definition = entity_type.get(syntax.PROPERTIES, {}).get(
                    property_name
                )
                if property_definition != None:
                    property_value = entity.get(syntax.PROPERTIES, {}).get(
                        property_name
                    )
                else:
                    capability_definition = entity_type.get(
                        syntax.CAPABILITIES, {}
                    ).get(property_name)
                    capability_value = entity.get(syntax.CAPABILITIES, {}).get(
                        property_name
                    )
                    if capability_definition != None:
                        capability_type = syntax.get_capability_type(
                            capability_definition
                        )
                        capability_definition_type = self.type_system.merge_type(
                            self.type_system.get_type_uri(capability_type)
                        )
                        if capability_definition_type is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + capability_type
                                + " capability type undefined",
                                value
                            )
                            return
                        property_name = parameters[2]
                        property_definition = capability_definition_type.get(
                            syntax.PROPERTIES, {}
                        ).get(property_name)
                        if property_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + property_name
                                + " property undefined in "
                                + capability_type,
                                value
                            )
                            return
                        if capability_value != None:
                            property_value = capability_value.get(
                                syntax.PROPERTIES, {}
                            ).get(property_name)
                    else:
                        requirement_definition = entity_type.get(
                            syntax.REQUIREMENTS, {}
                        ).get(property_name)
                        if requirement_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + property_name
                                + " capability or requirement undefined",
                                value
                            )
                            return
                        requirement = syntax.get_requirements_dict(entity).get(
                            property_name
                        )
                        requirement_capability = requirement_definition.get(
                            syntax.CAPABILITY
                        )
                        capability_definition_type = self.type_system.merge_type(
                            self.type_system.get_type_uri(requirement_capability)
                        )
                        capability_name = property_name  # TODO: could be different
                        property_name = parameters[2]
                        property_definition = capability_definition_type.get(
                            syntax.PROPERTIES, {}
                        ).get(property_name)
                        if property_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + property_name
                                + " property undefined in "
                                + requirement_capability,
                                value
                            )
                            return
                        requirement_node = syntax.get_requirement_node_template(
                            requirement
                        )
                        if requirement_node is None:
                            property_value = None
                        else:
                            entity = topology_template.get(
                                syntax.NODE_TEMPLATES, {}
                            ).get(requirement_node)
                            if entity is None:
                                property_value = None
                            else:
                                property_value = (
                                    entity.get(syntax.CAPABILITIES, {})
                                    .get(capability_name, {})
                                    .get(syntax.PROPERTIES, {})
                                    .get(property_name)
                                )

                    parameters_idx = 3

                for parameter in parameters[parameters_idx:]:
                    t = property_definition.get(syntax.TYPE)
                    rt = self.get_root_data_type_name(t)
                    if rt == "map":
                        type_checker = self.get_type_checker(
                            {
                                syntax.TYPE: property_definition.get(
                                    syntax.KEY_SCHEMA, {}
                                ).get(syntax.TYPE, "string")
                            },
                            {},
                            context_error_message + ": " + str(value),
                        )
                        type_checker.check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        property_definition = property_definition.get(
                            syntax.ENTRY_SCHEMA
                        )
                        if property_value != None:
                            property_value = property_value.get(parameter)
                    elif rt == "list":
                        BASIC_TYPE_CHECKERS["integer"].check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        property_definition = property_definition.get(
                            syntax.ENTRY_SCHEMA
                        )
                        if property_value != None:
                            property_value = property_value[parameter]
                    else:
                        property_definition = (
                            self.type_system.merge_type(
                                self.type_system.get_type_uri(t)
                            )
                            .get(syntax.PROPERTIES, {})
                            .get(parameter)
                        )
                        if property_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + str(parameter)
                                + " property undefined",
                                value
                            )
                            return
                        if property_value != None:
                            property_value = property_value.get(parameter)

                property_type = property_definition.get(syntax.TYPE)
                value_type = syntax.get_type(definition)
                if value_type != None and not self.type_system.is_derived_from(
                    property_type, value_type
                ):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - "
                        + property_type
                        + " type but "
                        + value_type
                        + " type expected",
                        value
                    )
                    return

                # check if the assigned definition is required then the assigning property is required
                if (
                    property_value is None
                    and value_type is not None
                    and definition.get(syntax.REQUIRED, True)
                    and is_required(property_definition) is False
                ):
                    self.warning(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - property "
                        + str(parameters)
                        + " is not required, but the actual value is expected from the system",
                        value
                    )

                return

            if syntax.GET_INPUT in value:
                parameters = value[syntax.GET_INPUT]
                if isinstance(parameters, str):
                    input_name = parameters
                    parameters = []
                elif isinstance(parameters, list):
                    input_name = parameters[0]
                    parameters = parameters[1:]
                else:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - string or list expected",
                        value
                    )
                    return
                input_definition = (
                    self.get_topology_template().get(syntax.INPUTS, {}).get(input_name)
                )
                if input_definition is None:
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - "
                        + input_name
                        + " input undefined",
                        value
                    )
                    return

                for parameter in parameters:
                    t = input_definition.get(syntax.TYPE)
                    rt = self.get_root_data_type_name(t)
                    if rt == "map":
                        type_checker = self.get_type_checker(
                            {
                                syntax.TYPE: input_definition.get(
                                    syntax.KEY_SCHEMA, {}
                                ).get(syntax.TYPE, "string")
                            },
                            {},
                            context_error_message + ": " + str(value),
                        )
                        type_checker.check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        input_definition = input_definition.get(syntax.ENTRY_SCHEMA)
                    elif rt == "list":
                        BASIC_TYPE_CHECKERS["integer"].check_type(
                            parameter, self, context_error_message + ": " + str(value)
                        )
                        input_definition = input_definition.get(syntax.ENTRY_SCHEMA)
                    else:
                        input_definition = (
                            self.type_system.merge_type(
                                self.type_system.get_type_uri(t)
                            )
                            .get(syntax.PROPERTIES, {})
                            .get(parameter)
                        )
                        if input_definition is None:
                            self.error(
                                context_error_message
                                + ": "
                                + str(value)
                                + " - "
                                + str(parameter)
                                + " property undefined",
                                value
                            )
                            return

                input_type = input_definition.get(syntax.TYPE)
                value_type = syntax.get_type(definition)
                if value_type is not None and not self.type_system.is_derived_from(
                    input_type, value_type
                ):
                    self.error(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - "
                        + input_type
                        + " type but "
                        + value_type
                        + " type expected",
                        value,
                    )
                    return

                # check if the assigned definition is required then the assigning input is required
                if (
                    value_type != None
                    and definition.get(syntax.REQUIRED, True)
                    and input_definition.get(syntax.REQUIRED, True) is False
                ):
                    self.warning(
                        context_error_message
                        + ": "
                        + str(value)
                        + " - input "
                        + str(parameter)
                        + " is not required, but the actual value is expected from the system",
                        value
                    )
                return

        self.check_value(value, definition, {}, context_error_message)

        # Check useless assignents
        if self.configuration.get(
            TYPE_SYSTEM,
            "check-useless-value-assigments"
        ):
            if 'default' in definition:
                default = definition.get(syntax.DEFAULT)
                if value == default:
                    self.warning(
                        context_error_message
                        + ': '
                        + str(value)
                        + ' - useless assignment as the value equals to the defined default value',
                        name,
                    )

    def check_property_assignment(
        self,
        property_name,
        property_assignment,
        property_definition,
        context_error_message,
    ):
        self.check_value_assignment(
            property_name,
            property_assignment,
            property_definition,
            context_error_message,
        )

    def check_parameter_assignment(
        self,
        parameter_name,
        parameter_assignment,
        parameter_definition,
        context_error_message,
    ):
        if isinstance(parameter_assignment, dict):
            value = parameter_assignment.get("value")
            if value is not None:
                parameter_assignment = value
            # TODO: check other keynames like type, etc.
        elif len(parameter_definition) == 0:
            parameter_definition = { "type": "string"}
        self.check_value_assignment(
            parameter_name,
            parameter_assignment,
            parameter_definition,
            context_error_message,
        )

    def check_attribute_assignment(
        self,
        attribute_name,
        attribute_assignment,
        attribute_definition,
        context_error_message,
    ):
        self.check_value_assignment(
            attribute_name,
            attribute_assignment,
            attribute_definition,
            context_error_message,
        )

    def check_capability_assignment(
        self,
        capability_name,
        capability_assignment,
        capability_definition,
        context_error_message,
    ):
        # obtain the capability type
        if isinstance(capability_definition, str):
            capability_definition = {"type": capability_definition}
        checked, capability_type_name, capability_type = self.check_type_in_definition(
            "capability", syntax.TYPE, capability_definition, capability_definition, context_error_message
        )
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            capability_assignment,
            capability_type,
            capability_type_name,
            context_error_message,
        )
        self.check_required_properties(
            capability_assignment, capability_type, context_error_message
        )
        # check attributes
        self.iterate_over_map_of_assignments(
            self.check_attribute_assignment,
            syntax.ATTRIBUTES,
            capability_assignment,
            capability_type,
            capability_type_name,
            context_error_message,
        )

    def check_requirement_assignment(
        self,
        requirement_name,
        requirement_assignment,
        requirement_definition,
        context_error_message,
    ):
        def check_compatible_capabilities(
            node_type_name,
            capability_name,
            capability_type_name,
            cem
        ):
            compatible_capabilities = \
                self.type_system.get_compatible_capabilities(
                                    node_type_name,
                                    capability_name,
                                    capability_type_name
                )
            if len(compatible_capabilities) == 0:
                self.error(
                    cem
                    + " - "
                    + requirement_capability
                    + " capability expected",
                    requirement_assignment
                )
            elif len(compatible_capabilities) == 1:
                self.info(
                    cem
                    + " - "
                    + compatible_capabilities[0]
                    + " capability found",
                    requirement_assignment
                )
            else:
                self.warning(
                    cem
                    + " - "
                    + array_to_string_with_or_separator(compatible_capabilities)
                    + " capabilities found, then "
                    + compatible_capabilities[0]
                    + " selected",
                    requirement_assignment
                )

        # check the short notation
        if isinstance(requirement_assignment, str):
            node_template = (
                self.get_topology_template()
                .get(syntax.NODE_TEMPLATES, {})
                .get(requirement_assignment)
            )
            if node_template is None:
                self.error(
                    context_error_message
                    + ": "
                    + requirement_assignment
                    + " - node template undefined",
                    requirement_assignment,
                )
                return

            requirement_capability = requirement_definition.get(
                                        syntax.CAPABILITY
                                     )
            if requirement_capability is None:
                self.error(
                    context_error_message
                    + ": "
                    + requirement_assignment
                    + " - no capability type in "
                    + str(requirement_definition),
                    requirement_assignment
                )
                return

            requirement_node_type_name = requirement_definition.get(syntax.NODE)
            if requirement_node_type_name is not None:
                # check node_template type is compatible with requirement_definition node
                if not self.type_system.is_derived_from(
                    node_template.get(syntax.TYPE), requirement_node_type_name
                ):
                    self.error(
                        context_error_message
                        + ": "
                        + requirement_assignment
                        + " - "
                        + node_template.get(syntax.TYPE)
                        + " but "
                        + requirement_node_type_name
                        + " expected",
                        requirement_assignment
                    )
                    return

            check_compatible_capabilities(
                node_template.get(syntax.TYPE),
                None,
                requirement_capability,
                context_error_message + ": " + requirement_assignment
            )

            if requirement_definition.get(syntax.RELATIONSHIP) != None:
                (
                    checked,
                    relationship_type_name,
                    relationship_type,
                ) = self.check_type_in_definition(
                    "relationship",
                    syntax.RELATIONSHIP,
                    requirement_definition,
                    {},
                    context_error_message,
                )
                # but the required properties without default of the relationship type must be assigned
                self.check_required_properties({}, relationship_type, context_error_message + ":relationship")

            return

        # check the extended notation

        # check capability
        capability = requirement_assignment.get(syntax.CAPABILITY)

        # check node
        update_requirement_node = None
        node = requirement_assignment.get(syntax.NODE)
        if node is not None:
            node_template = (
                self.get_topology_template().get(syntax.NODE_TEMPLATES, {}).get(node)
            )
            if node_template is not None:
                requirement_node_type_name = requirement_definition.get(syntax.NODE)
                if requirement_node_type_name is not None:
                    # check node_template type is compatible with requirement_definition node
                    if not self.type_system.is_derived_from(
                        node_template.get(syntax.TYPE), requirement_node_type_name
                    ):
                        self.error(
                            context_error_message
                            + ": "
                            + str(requirement_assignment)
                            + " - "
                            + node_template.get(syntax.TYPE)
                            + " but "
                            + requirement_node_type_name
                            + " expected",
                            requirement_assignment,
                        )

                if capability is not None:
                    requirement_capability = capability
                else:
                    requirement_capability = requirement_definition.get(
                            syntax.CAPABILITY
                    )
                if requirement_capability is None:
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.NODE
                        + ": "
                        + node
                        + " - no capability type in "
                        + str(requirement_definition),
                        node,
                    )
                else:
                    check_compatible_capabilities(
                        node_template.get(syntax.TYPE),
                        requirement_capability,
                        requirement_capability,
                        context_error_message + ":" + syntax.NODE + ": " + node
                    )
            else:
                node_type = self.type_system.merge_type(node)
                if node_type is None:
                    self.error(
                        context_error_message
                        + ":"
                        + syntax.NODE
                        + ": "
                        + node
                        + " - node template or type undefined",
                        node,
                    )
                else:
                    requirement_node_type_name = requirement_definition.get(syntax.NODE)
                    if requirement_node_type_name is not None:
                        # check node_template type is compatible with requirement_definition node
                        if not self.type_system.is_derived_from(
                            node, requirement_node_type_name
                        ):
                            self.error(
                                context_error_message
                                + ":"
                                + syntax.NODE
                                + ": "
                                + node
                                + " - "
                                + requirement_node_type_name
                                + " expected",
                                node,
                            )

                    if capability is not None:
                        requirement_capability = capability
                    else:
                        requirement_capability = requirement_definition.get(
                            syntax.CAPABILITY
                        )
                    if requirement_capability is None:
                        self.error(
                            context_error_message
                            + ":"
                            + syntax.NODE
                            + ": "
                            + node
                            + " - no capability type in "
                            + str(requirement_definition),
                            node,
                        )
                    else:
                        check_compatible_capabilities(
                            node,
                            requirement_capability,
                            requirement_capability,
                            context_error_message + ":" + syntax.NODE + ": " + node
                        )

                    if requirement_assignment.get(syntax.NODE_FILTER) is None:
                        # search node templates conform to node_type
                        cem = context_error_message + ":" + syntax.NODE + ": " + node
                        node_templates = self.select_node_templates(node, None, cem)
                        if len(node_templates) == 0:
                            self.error(cem + " - no node template found", node)
                        else:
                            node_template = node_templates[0]
                            if len(node_templates) == 1:
                                self.info(
                                    cem
                                    + " - "
                                    + node_template
                                    + " node template found",
                                    requirement_assignment
                                )
                            else:
                                self.warning(
                                    cem
                                    + " - "
                                    + array_to_string_with_or_separator(node_templates)
                                    + " node templates found, then "
                                    + node_template
                                    + " selected",
                                    requirement_assignment,
                                )
                            update_requirement_node = node_template

        # check relationship
        relationship = requirement_assignment.get(syntax.RELATIONSHIP)
        if relationship is not None:
            cem = context_error_message + ":" + syntax.RELATIONSHIP
            # check short notation
            if isinstance(relationship, str):
                relationship_template = (
                    self.get_topology_template()
                    .get(syntax.RELATIONSHIP_TEMPLATES, {})
                    .get(relationship)
                )
                if relationship_template is None:
                    relationship_type = relationship
                    if (
                        self.type_system.relationship_types.get(
                            self.type_system.get_type_uri(relationship_type)
                        )
                        is None
                    ):
                        self.error(
                            cem
                            + ": "
                            + relationship
                            + " - relationship template or type undefined",
                            relationship,
                        )
                else:
                    relationship_type = relationship_template.get(syntax.TYPE)
                requirement_relationship = requirement_definition.get(
                    syntax.RELATIONSHIP
                )
                if requirement_relationship != None:
                    if not self.type_system.is_derived_from(
                        relationship_type, requirement_relationship
                    ):
                        self.error(
                            cem
                            + ": "
                            + relationship
                            + " - "
                            + relationship_type
                            + " but "
                            + requirement_relationship
                            + " relationship type expected",
                            relationship
                        )
                else:
                    if not self.type_system.is_relationship_type_compatible_with_capability_type(
                        relationship_type, requirement_capability
                    ):
                        self.error(
                            cem
                            + ": "
                            + relationship
                            + " - not compatible with "
                            + requirement_capability,
                            relationship
                        )
                    else:
                        self.info(
                            cem
                            + ": "
                            + relationship
                            + " compatible with "
                            + requirement_capability,
                            relationship
                        )
            else:
                # check extended notation
                # check relationship type
                if relationship.get(syntax.TYPE) is not None:
                    (
                        checked,
                        relationship_type_name,
                        relationship_type,
                    ) = self.check_type_in_definition(
                        "relationship", syntax.TYPE, relationship, {}, cem
                    )
                else:
                    (
                        checked,
                        relationship_type_name,
                        relationship_type,
                    ) = self.check_type_in_definition(
                        "relationship",
                        syntax.RELATIONSHIP,
                        requirement_definition,
                        {},
                        cem,
                    )
                # Keep in mind current reserved_function_keywords
                previous_reserved_function_keywords = self.reserved_function_keywords
                # change reserved_function_keywords for relationship
                self.reserved_function_keywords = {
                    "SELF": relationship,
                    "SOURCE": self.reserved_function_keywords[
                        "SELF"
                    ],  # SOURCE is the current SELF
                    #                    'TARGET': , #TODO
                }
                # check relationship properties
                self.iterate_over_map_of_assignments(
                    self.check_property_assignment,
                    syntax.PROPERTIES,
                    relationship,
                    relationship_type,
                    relationship_type_name,
                    cem,
                )
                self.check_required_properties(
                    relationship, relationship_type, context_error_message
                )
                # check relationship interfaces
                self.iterate_over_map_of_assignments(
                    self.check_interface_assignment,
                    syntax.INTERFACES,
                    relationship,
                    relationship_type,
                    relationship_type_name,
                    cem,
                )
                # Restore previous reserved_function_keywords
                self.reserved_function_keywords = previous_reserved_function_keywords
        else:
            # no relationship declared
            cem = context_error_message + ":" + syntax.RELATIONSHIP
            if requirement_definition.get(syntax.RELATIONSHIP) != None:
                (
                    checked,
                    relationship_type_name,
                    relationship_type,
                ) = self.check_type_in_definition(
                    "relationship",
                    syntax.TYPE,
                    requirement_definition.get(syntax.RELATIONSHIP),
                    {},
                    context_error_message,
                )
                # but the required properties without default of the relationship type must be assigned
                self.check_required_properties({}, relationship_type, cem)
            else:
                relationship_types = (
                    self.search_relationship_types_compatible_with_capability_type(
                        requirement_capability, cem
                    )
                )
                if len(relationship_types) > 0:
                    self.warning(
                        cem
                        + " - set to "
                        + relationship_types[0],
                        requirement_assignment
                    )
                    # WARNING: modify the template
                    requirement_assignment[syntax.RELATIONSHIP] = relationship_types[0]

        # check node_filter
        node_filter = requirement_assignment.get(syntax.NODE_FILTER)
        if node_filter is not None:
            # TODO: node_filter and node: <node_template_name> are exclusive!
            checked, node_type_name, node_type = self.check_type_in_definition(
                "node",
                syntax.NODE,
                requirement_assignment,
                requirement_definition,
                context_error_message,
            )
            self.check_node_filter_definition(
                node_filter,
                node_type_name,
                node_type,
                context_error_message + ":" + syntax.NODE_FILTER,
            )

            # search node templates conform to node_type
            cem = context_error_message + ":" + syntax.NODE_FILTER
            node_templates = self.select_node_templates(
                node_type_name, node_filter, cem
            )
            if len(node_templates) == 0:
                self.error(
                    cem
                    + " - no node template found",
                    requirement_assignment
                )
            else:
                update_requirement_node = node_templates[0]
                if len(node_templates) == 1:
                    self.info(
                        cem
                        + " - "
                        + update_requirement_node
                        + " node template found",
                        requirement_assignment
                    )
                else:
                    self.warning(
                        cem
                        + " - "
                        + array_to_string_with_or_separator(node_templates)
                        + " node templates found, then "
                        + update_requirement_node
                        + " selected",
                        node_templates,
                    )
            # WARNING: remove the node_filter from requirement_assignment!
            del requirement_assignment[syntax.NODE_FILTER]

        # update the node of requirement_assignment if a node template found
        if update_requirement_node is not None:
            requirement_assignment[syntax.NODE] = update_requirement_node

    def eval_node_filter(self, node_filter, node_template, context_error_message):
        def eval_property_filters(filter, template, template_type):
            template_properties = template.get(syntax.PROPERTIES, {})
            template_type_properties = template_type.get(syntax.PROPERTIES, {})
            for property_filter in filter.get(syntax.PROPERTIES, []):
                for (
                    property_name,
                    property_constraint_clauses,
                ) in property_filter.items():
                    property_value = template_properties.get(property_name)
                    property_type = template_type_properties.get(property_name, {}).get(
                        syntax.TYPE
                    )
                    if property_value is None:
                        # TODO: dealt with default or value defined in the property definition
                        return False  # no value for the property
                    if isinstance(property_value, dict) and ("get_input" in property_value):
                        # Skip properties set by an input
                        continue
                    if not isinstance(property_constraint_clauses, list):
                        property_constraint_clauses = [property_constraint_clauses]
                    for property_constraint_clause in property_constraint_clauses:
                        property_constraint_clause = \
                            normalize_constraint_clause(property_constraint_clause)
                        for (
                            constraint_name,
                            constraint_value,
                        ) in property_constraint_clause.items():
                            constraint_clause_checkers = BASIC_CONSTRAINT_CLAUSES.get(
                                constraint_name
                            )
                            if constraint_clause_checkers is None:
                                self.error(
                                    context_error_message
                                    + " - "
                                    + constraint_name
                                    + " unsupported operator",
                                    constraint_name
                                )
                                return False
                            constraint_clause_checker = constraint_clause_checkers.get(
                                property_type
                            )
                            if constraint_clause_checker is None:
                                self.error(
                                    context_error_message
                                    + " - "
                                    + constraint_name
                                    + " unallowed operator on "
                                    + property_type
                                    + " value",
                                    constraint_name
                                )
                                return False
                            LOGGER.debug(
                                context_error_message
                                + " - evaluate "
                                + constraint_name
                                + ": "
                                + str(constraint_value),
                                constraint_name
                            )
                            if not constraint_clause_checker.check_constraint(
                                property_value,
                                constraint_value,
                                self,
                                context_error_message,
                            ):
                                return False
            # all property constraints are matched ;-)
            return True

        node_template_type = self.type_system.merge_type(node_template.get(syntax.TYPE))
        # evaluation node_filter properties
        if not eval_property_filters(node_filter, node_template, node_template_type):
            return False
        # evaluation node_filter capabilities
        node_template_capabilities = node_template.get(syntax.CAPABILITIES, {})
        node_template_type_capabilities = node_template_type.get(
            syntax.CAPABILITIES, {}
        )
        for node_filter_capability in node_filter.get(syntax.CAPABILITIES, []):
            for capability_name, capability_filter in node_filter_capability.items():
                capability_type_name = node_template_type_capabilities.get(
                    capability_name, {}
                ).get(syntax.TYPE)
                if (
                    capability_type_name is None
                ):  # capability not found! so node_filter is incorrectly typed!
                    return False
                capability_type = self.type_system.merge_type(capability_type_name)
                if not eval_property_filters(
                    capability_filter,
                    node_template_capabilities.get(capability_name, {}),
                    capability_type,
                ):
                    return False
        # all node filter constraints are matched ;-)
        return True

    def select_node_templates(self, node_type_name, node_filter, context_error_message):
        self.logger.debug(
            context_error_message
            + "- select_node_templates with node_filter =%s" % node_filter
        )
        found_node_templates = []
        for node_template_name, node_template in (
            self.get_topology_template().get(syntax.NODE_TEMPLATES, {}).items()
        ):
            if self.type_system.is_derived_from(
                node_template.get(syntax.TYPE), node_type_name
            ):
                if node_filter is None or self.eval_node_filter(
                    node_filter, node_template, context_error_message
                ):
                    found_node_templates.append(node_template_name)
        self.logger.debug(
            context_error_message
            + "- select_node_templates found_node_templates =%s" % found_node_templates
        )
        return found_node_templates

    def search_substituting_topology_templates(
        self, node_template, context_error_message
    ):
        node_template_type = node_template["type"]
        self.debug(
            context_error_message
            + " - search_substituting_topology_templates %s" % node_template_type
        )
        found_substituting_topology_templates = []
        for tosca_service_template in self.substituting_topology_templates:
            substitution_mappings = tosca_service_template.get_yaml()[
                "topology_template"
            ]["substitution_mappings"]
            self.debug("substitution_mappings = %s" % substitution_mappings)
            if self.type_system.is_derived_from(
                node_template_type, substitution_mappings["node_type"]
            ):
                substitution_filter = substitution_mappings.get("substitution_filter")
                self.debug("substitution_filter = %s" % substitution_filter)
                if substitution_filter is None or self.eval_node_filter(
                    substitution_filter, node_template, context_error_message
                ):
                    found_substituting_topology_templates.append(tosca_service_template)
        self.debug(
            context_error_message
            + "- search_substituting_topology_templates returns %s"
            % found_substituting_topology_templates
        )
        return found_substituting_topology_templates

    def check_interface_assignment(
        self,
        interface_name,
        interface_assignment,
        interface_definition,
        context_error_message,
    ):
        # check description - nothing to do
        # check type
        checked, interface_type_name, interface_type = self.check_type_in_definition(
            "interface",
            syntax.TYPE,
            interface_assignment,
            interface_definition,
            context_error_message,
        )
        # check inputs
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.INPUTS,
            interface_assignment,
            interface_type,
            REFINE_OR_NEW,
            context_error_message,
        )
        self.check_required_parameters(
            interface_assignment, interface_type, context_error_message
        )
        # check operations
        operations = syntax.get_operations(interface_assignment)
        type_operations = syntax.get_operations(interface_type)
        self.iterate_over_map_of_assignments(
            self.check_operation_assignment,
            syntax.OPERATIONS,
            operations,
            type_operations,
            interface_type_name,
            context_error_message,
        )
        # check notifications
        notifications = interface_assignment.get(syntax.NOTIFICATIONS)
        if notifications is not None:
            self.iterate_over_map_of_assignments(
                self.check_notification_assignment,
                syntax.NOTIFICATIONS,
                interface_assignment,
                interface_type,
                interface_type_name,
                context_error_message,
            )

    def check_operation_assignment(
        self,
        operation_name,
        operation_assignment,
        operation_definition,
        context_error_message,
    ):
        # check the short notation
        if isinstance(operation_assignment, str):
            self.check_operation_implementation_definition(
                operation_assignment, context_error_message
            )
            return
        # check the extended notation
        # check description - nothing to do
        # check implementation
        implementation = operation_assignment.get(syntax.IMPLEMENTATION)
        if implementation is not None:
            self.check_operation_implementation_definition(
                implementation, context_error_message + ":" + syntax.IMPLEMENTATION
            )
        # check inputs
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.INPUTS,
            operation_assignment,
            operation_definition,
            REFINE_OR_NEW,
            context_error_message,
        )
        self.check_required_parameters(
            operation_assignment, operation_definition, context_error_message
        )

    def check_node_template(self, node_name, node_template, context_error_message):
        # set values of reserved function keywords
        self.reserved_function_keywords = {"SELF": node_template}
        # set allowed operation_host keynames
        self.current_allowed_operation_host_keynames = [ "SELF", "HOST", "ORCHESTRATOR"]

        # check type
        checked, node_type_name, node_type = self.check_type_in_template(
            "node", node_template, syntax.TYPE, context_error_message
        )
        # check description - nothing to do
        # check metadata - nothing to do
        # check directives
        def check_directive_substitute(cem, directive):
            substituting_topology_templates = (
                self.search_substituting_topology_templates(node_template, cem)
            )
            nb_substituting_topology_templates = len(substituting_topology_templates)
            if nb_substituting_topology_templates == 0:
                self.warning(
                    cem
                    + " - no substituting topology template found for %s node type"
                    % node_type_name,
                    directive,
                )
            elif nb_substituting_topology_templates == 1:
                self.info(
                    cem
                    + " - one substituting topology template found: "
                    + substituting_topology_templates[0].get_fullname(),
                    directive,
                )
            else:
                self.warning(
                    cem
                    + " - several substituting topology templates found: "
                    + array_to_string_with_or_separator(
                        [item.get_fullname() for item in substituting_topology_templates]
                    ),
                    directive,
                )

        idx = 0
        for directive in node_template.get(syntax.DIRECTIVES, []):
            cem = (
                context_error_message
                + ":"
                + syntax.DIRECTIVES
                + "["
                + str(idx)
                + "]: "
                + directive
            )
            if directive == "substitute":
                check_directive_substitute(cem, directive)
            elif directive == "substitutable":
                self.warning(
                    cem + " - deprecated directive, instead use substitute directive",
                    directive,
                )
                check_directive_substitute(cem)
            elif directive == "select":
                self.error(
                    cem + " - unchecked currently",
                    directive,
                )
            elif directive == "selectable":
                self.warning(
                    cem + " - deprecated directive, instead use select directive",
                    directive,
                )
                self.error(
                    cem + " - unchecked currently",
                    directive,
                )
            else:
                self.error(
                    cem + " - unsupported directive",
                    directive,
                )
            idx += 1
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            node_template,
            node_type,
            node_type_name,
            context_error_message,
        )
        node_filter = node_template.get(syntax.NODE_FILTER)
        if node_filter is None:
            self.check_required_properties(
                node_template, node_type, context_error_message
            )
        # check attributes
        self.iterate_over_map_of_assignments(
            self.check_attribute_assignment,
            syntax.ATTRIBUTES,
            node_template,
            node_type,
            node_type_name,
            context_error_message,
        )
        # check requirements
        node_type_requirements = syntax.get_requirements_dict(node_type)
        if node_filter is None:
            # declare all the requirements of this node template
            for (
                requirement_name,
                requirement_definition,
            ) in node_type_requirements.items():
                self.all_the_node_template_requirements[
                    node_name + "." + requirement_name
                ] = NodeTemplateRequirement(
                    node_name, requirement_name, requirement_definition
                )
        idx = 0
        for requirement in node_template.get(syntax.REQUIREMENTS, []):
            cem1 = (
                context_error_message
                + ":"
                + syntax.REQUIREMENTS
                + "["
                + str(idx)
                + "]:"
            )
            for requirement_name, requirement_assignment in requirement.items():
                requirement_definition = node_type_requirements.get(requirement_name)
                if requirement_definition is None:
                    self.error(
                        cem1
                        + requirement_name
                        + " - undefined in "
                        + node_type_name,
                        requirement_name
                    )
                else:
                    self.check_requirement_assignment(
                        requirement_name,
                        requirement_assignment,
                        requirement_definition,
                        cem1 + requirement_name,
                    )
                    # mark that the requirement <node_template_name>.<node_template_reference_name> is connected
                    self.all_the_node_template_requirements.get(
                        node_name + "." + requirement_name
                    ).connectIt()
            idx += 1
        # check capabilities
        self.iterate_over_map_of_assignments(
            self.check_capability_assignment,
            syntax.CAPABILITIES,
            node_template,
            node_type,
            node_type_name,
            context_error_message,
        )
        capabilities = node_template.get(syntax.CAPABILITIES, {})
        for capability_name, capability_definition in node_type.get(
            syntax.CAPABILITIES, {}
        ).items():
            if isinstance(capability_definition, str):
                capability_type = self.type_system.merge_type(capability_definition)
            else:
                (
                    checked,
                    capability_type_name,
                    capability_type,
                ) = self.check_type_in_definition(
                    "capability",
                    syntax.TYPE,
                    capability_definition,
                    {},
                    context_error_message,
                )

                # Merge capability type and refined properties and attributes
                capability_type = merge_dict(capability_type, capability_definition)

            self.check_required_properties(
                capabilities.get(capability_name, {}),
                capability_type,
                context_error_message
                + ":"
                + syntax.CAPABILITIES
                + ":"
                + capability_name,
            )
        # check interfaces
        self.iterate_over_map_of_assignments(
            self.check_interface_assignment,
            syntax.INTERFACES,
            node_template,
            node_type,
            node_type_name,
            context_error_message,
        )
        # check artifacts
        self.iterate_over_map_of_definitions(
            self.check_artifact_definition,
            syntax.ARTIFACTS,
            node_template,
            {},
            REFINE_OR_NEW,
            context_error_message,
        )
        # check node_filter
        if node_filter is not None:
            self.check_node_filter_definition(
                node_filter,
                node_type_name,
                node_type,
                context_error_message + ":" + syntax.NODE_FILTER,
            )
        # check copy - TODO
        self.unchecked(node_template, syntax.COPY, context_error_message)

        # reset values of reserved function keywords
        self.reserved_function_keywords = {}
        # reset allowed operation_host keynames
        self.current_allowed_operation_host_keynames = []

    def check_node_filter_definition(
        self, node_filter, node_type_name, node_type, context_error_message
    ):
        # check properties
        properties = node_filter.get(syntax.PROPERTIES)
        if properties is not None:
            node_type_properties = node_type.get(syntax.PROPERTIES, {})
            idx = 0
            for property in properties:
                cem = (
                    context_error_message
                    + ":"
                    + syntax.PROPERTIES
                    + "["
                    + str(idx)
                    + "]"
                )
                for property_name, property_filter_definition in property.items():
                    property_definition = node_type_properties.get(property_name)
                    if property_definition is None:
                        self.error(
                            cem
                            + ":"
                            + property_name
                            + " - property undefined in %s" % node_type_name,
                            property_name,
                        )
                    else:
                        self.check_property_filter_definition(
                            property_name,
                            property_filter_definition,
                            property_definition,
                            cem + ":" + property_name,
                        )
            idx += 1
        # check capabilities
        capabilities = node_filter.get(syntax.CAPABILITIES)
        if capabilities is not None:
            cem = context_error_message + ":" + syntax.CAPABILITIES
            node_type_capabilities = node_type.get(syntax.CAPABILITIES, {})
            idx1 = 0
            for capability in capabilities:
                cem1 = cem + "[" + str(idx1) + "]:"
                for capability_name, capability_value in capability.items():
                    capability_definition = node_type_capabilities.get(capability_name)
                    if capability_definition is None:
                        self.error(
                            cem1
                            + capability_name
                            + " - capability undefined in %s" % node_type_name,
                            capability_name,
                        )
                    else:
                        cem1 += capability_name + ":properties"
                        if isinstance(capability_definition, str):
                            capability_definition = {syntax.TYPE: capability_definition}
                        (
                            checked,
                            capability_type_name,
                            capability_type,
                        ) = self.check_type_in_definition(
                            "capability",
                            syntax.TYPE,
                            capability_definition,
                            {},
                            context_error_message,
                        )
                        capability_type_properties = capability_type.get(
                            syntax.PROPERTIES, {}
                        )
                        idx2 = 0
                        for capability_properties in capability_value.get(
                            syntax.PROPERTIES, []
                        ):
                            cem2 = cem1 + "[" + str(idx2) + "]:"
                            for (
                                property_name,
                                property_filter_definition,
                            ) in capability_properties.items():
                                property_definition = capability_type_properties.get(
                                    property_name
                                )
                                if property_definition is None:
                                    self.error(
                                        cem2
                                        + property_name
                                        + " - property undefined in "
                                        + capability_type_name,
                                        property_name,
                                    )
                                else:
                                    self.check_property_filter_definition(
                                        property_name,
                                        property_filter_definition,
                                        property_definition,
                                        cem2 + property_name,
                                    )
                            idx2 += 1
                idx1 += 1

    def check_property_filter_definition(
        self,
        property_name,
        property_filter_definition,
        property_definition,
        context_error_message,
    ):
        type_checker = self.get_type_checker(
            property_definition, {}, context_error_message
        )
        if isinstance(property_filter_definition, list):
            self.check_list_of_constraint_clauses(
                property_filter_definition, type_checker, context_error_message
            )
        else:
            self.check_constraint_clause(
                property_filter_definition, type_checker, context_error_message
            )

    def check_relationship_template(
        self, relationship_name, relationship_template, context_error_message
    ):
        # set values of reserved function keywords
        self.reserved_function_keywords = {
            "SELF": relationship_template,
            "TARGET": "UNKNOWN",
            "SOURCE": "UNKNOWN"
        }
        # set allowed operation_host keynames
        self.current_allowed_operation_host_keynames = [ "SOURCE", "TARGET", "ORCHESTRATOR"]

        # check type
        checked, relationship_type_name, relationship_type = (
            self.check_type_in_template(
                'relationship',
                relationship_template,
                syntax.TYPE,
                context_error_message
            )
        )

        # check description - nothing to do
        # check metadata - nothing to do
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            relationship_template,
            relationship_type,
            relationship_type_name,
            context_error_message,
        )
        self.check_required_properties(
            relationship_template, relationship_type, context_error_message
        )
        # check attributes
        self.iterate_over_map_of_assignments(
            self.check_attribute_assignment,
            syntax.ATTRIBUTES,
            relationship_template,
            relationship_type,
            relationship_type_name,
            context_error_message,
        )
        # check interfaces
        self.iterate_over_map_of_assignments(
            self.check_interface_assignment,
            syntax.INTERFACES,
            relationship_template,
            relationship_type,
            relationship_type_name,
            context_error_message,
        )
        # check copy - TODO
        self.unchecked(relationship_template, syntax.COPY, context_error_message)

        # reset values of reserved function keywords
        self.reserved_function_keywords = {}
        # reset allowed operation_host keynames
        self.current_allowed_operation_host_keynames = []

    def check_group_definition(
        self, group_name, group_definition, context_error_message
    ):
        # check type
        checked, group_type_name, group_type = self.check_type_in_template(
            "group", group_definition, syntax.TYPE, context_error_message
        )
        # check description - nothing to do
        # check metadata - nothing to do
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            group_definition,
            group_type,
            group_type_name,
            context_error_message,
        )
        self.check_required_properties(
            group_definition, group_type, context_error_message
        )
        # check members
        members = group_definition.get(syntax.MEMBERS)
        if members is not None:
            topology_template = self.get_topology_template()
            group_type_members = group_type.get(syntax.MEMBERS)
            idx = 0
            for member in members:
                cem = (
                    context_error_message
                    + ":"
                    + syntax.MEMBERS
                    + "["
                    + str(idx)
                    + "]: "
                    + member
                )
                node_template = topology_template.get(syntax.NODE_TEMPLATES, {}).get(
                    member
                )
                if node_template is None:
                    self.error(cem + " - node template undefined", topology_template)
                else:
                    if group_type_members is not None:
                        node_template_type = node_template.get(syntax.TYPE)
                        compatible_with_members = False
                        for group_type_member_type in group_type_members:
                            if self.type_system.is_derived_from(
                                node_template_type, group_type_member_type
                            ):
                                compatible_with_members = True
                                break
                        if not compatible_with_members:
                            self.error(
                                cem
                                + " - incompatible with "
                                + array_to_string_with_or_separator(group_type_members),
                                member,
                            )
                idx += 1
        # check interfaces
        self.iterate_over_map_of_assignments(
            self.check_interface_assignment,
            syntax.INTERFACES,
            group_definition,
            group_type,
            group_type_name,
            context_error_message,
        )

    def check_policy_definition(
        self, policy_name, policy_definition, context_error_message
    ):
        # check type
        checked, policy_type_name, policy_type = self.check_type_in_template(
            "policy", policy_definition, syntax.TYPE, context_error_message
        )
        policy_type_targets = policy_type.get(syntax.TARGETS)
        # check description - nothing to do
        # check metadata - nothing to do
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_assignment,
            syntax.PROPERTIES,
            policy_definition,
            policy_type,
            policy_type_name,
            context_error_message,
        )
        self.check_required_properties(
            policy_definition, policy_type, context_error_message
        )
        # check targets
        self.current_targets = []
        self.current_targets_activity_type = []
        self.current_targets_condition_type = []
        targets = policy_definition.get(syntax.TARGETS)
        if targets is not None:
            self.current_targets = targets
            topology_template = self.get_topology_template()
            idx = 0
            for target in targets:
                cem = (
                    context_error_message
                    + ":"
                    + syntax.TARGETS
                    + "["
                    + str(idx)
                    + "]: "
                    + target
                )
                node_or_group_template = topology_template.get(
                    syntax.NODE_TEMPLATES, {}
                ).get(target)
                if node_or_group_template is None:
                    node_or_group_template = topology_template.get(
                        syntax.GROUPS, {}
                    ).get(target)
                if node_or_group_template is None:
                    self.error(
                        cem + " - node template or group undefined", target
                    )
                else:
                    node_or_group_template_type = node_or_group_template.get(
                        syntax.TYPE
                    )
                    current_target_type = self.type_system.merge_type(
                        self.type_system.get_type_uri(node_or_group_template_type)
                    )
                    self.current_targets_activity_type.append(current_target_type)
                    self.current_targets_condition_type.append(current_target_type)
                    if policy_type_targets is not None:
                        compatible_with_targets = False
                        for policy_type_target_type in policy_type_targets:
                            if self.type_system.is_derived_from(
                                node_or_group_template_type, policy_type_target_type
                            ):
                                compatible_with_targets = True
                                break
                        if not compatible_with_targets:
                            self.error(
                                cem
                                + " - incompatible with "
                                + array_to_string_with_or_separator(
                                    policy_type_targets
                                ),
                                target,
                            )
                idx += 1
        else: # no targets
            if policy_type_targets != None and len(policy_type_targets) > 0:
                self.error(
                    context_error_message
                    + ' - no targets but '
                    + array_to_string_with_or_separator(policy_type_targets)
                    + ' expected',
                    policy_definition
                    )

        # check triggers
        self.iterate_over_map_of_definitions(
            self.check_trigger_definition,
            syntax.TRIGGERS,
            policy_definition,
            policy_type,
            REFINE_OR_NEW,
            context_error_message,
        )

    def check_trigger_definition(
        self,
        trigger_name,
        trigger_definition,
        previous_trigger_definition,
        context_error_message,
    ):
        # store current_targets and current_targets_*_type
        previous_targets = self.current_targets
        previous_targets_activity_type = self.current_targets_activity_type
        previous_targets_condition_type = self.current_targets_condition_type
        # check description - nothing to do
        # check event - nothing TODO
        # check schedule

        def check_schedule(schedule, cem):
            BASIC_TYPE_CHECKERS["timestamp"].check_type(
                schedule.get("start_time"), self, cem + ":start_time"
            )
            BASIC_TYPE_CHECKERS["timestamp"].check_type(
                schedule.get("end_time"), self, cem + ":end_time"
            )

        self.check_keyword(
            trigger_definition, "schedule", check_schedule, context_error_message
        )
        # check target_filter

        def check_target_filter(target_filter, cem):
            # check node
            def check_node(node, cem):
                if node not in self.current_targets:
                    self.error(
                        cem
                        + ": "
                        + node
                        + " - not in policy targets",
                        node
                    )
                else:
                    self.info(
                        cem
                        + ": "
                        + node +
                        " - valid target_filter node",
                        node
                    )
                    self.current_targets = [node]
                    idx = self.current_targets.index(node)
                    self.current_targets_activity_type = [
                        self.current_targets_activity_type[idx]
                    ]
                    self.current_targets_condition_type = [
                        self.current_targets_condition_type[idx]
                    ]

            self.check_keyword(target_filter, "node", check_node, cem)

            # check requirement
            def check_requirement(requirement, cem):
                requirement_definition = (
                    self.current_targets_activity_type[0]
                    .get(syntax.REQUIREMENTS, {})
                    .get(requirement)
                )
                if requirement_definition is None:
                    self.error(
                        cem
                        + ": "
                        + requirement
                        + " - requirement undefined in "
                        + self.current_targets[0],
                        requirement,
                    )
                    node_type = {}
                else:
                    self.info(
                        cem
                        + ": "
                        + requirement
                        + " - valid target_filter requirement in "
                        + self.current_targets[0],
                        requirement
                    )
                    checked, node_type_name, node_type = self.check_type_in_definition(
                        "node", syntax.NODE, requirement_definition, {}, cem
                    )
                self.current_targets = [
                    self.current_targets[0] + ".requirements." + requirement + ".node"
                ]
                self.current_targets_activity_type = [node_type]
                self.current_targets_condition_type = [node_type]

            self.check_keyword(target_filter, "requirement", check_requirement, cem)

            # check capability
            def check_capability(capability, cem):
                capability_definition = (
                    self.current_targets_activity_type[0]
                    .get(syntax.CAPABILITIES, {})
                    .get(capability)
                )
                if capability_definition is None:
                    self.error(
                        cem
                        + ": "
                        + capability
                        + " - capability undefined in "
                        + self.current_targets[0],
                        capability,
                    )
                    capability_type = {}
                else:
                    self.info(
                        cem
                        + ": "
                        + capability
                        + " - valid target_filter capability in "
                        + self.current_targets[0],
                        capability
                    )
                    (
                        checked,
                        capability_type_name,
                        capability_type,
                    ) = self.check_type_in_definition(
                        "capability", syntax.TYPE, capability_definition, {}, cem
                    )
                self.current_targets = [
                    self.current_targets[0] + ".capabilities." + capability
                ]
                self.current_targets_condition_type = [capability_type]

            self.check_keyword(target_filter, "capability", check_capability, cem)

        self.check_keyword(
            trigger_definition,
            "target_filter",
            check_target_filter,
            context_error_message,
        )
        # check condition
        condition = trigger_definition.get("condition")
        if isinstance(condition, list):
            self.iterate_over_list(
                trigger_definition,
                "condition",
                self.check_condition_clause_definition,
                context_error_message,
            )
        elif isinstance(condition, dict):
            cem = context_error_message + ":" + "condition"
            # duplicate condition
            condition = dict(condition)
            # check the extended notation
            extended_notation = False

            def remove_keyword(keyword):
                if condition.get(keyword) is not None:
                    del condition[keyword]
                    extended_notation = True

            # check constraint
            def check_constraint(constraint, cem):
                if isinstance(constraint, list):
                    for item in constraint:
                        self.check_condition_clause_definition(item, cem)
                else:
                    self.check_condition_clause_definition(constraint, cem)

            self.check_keyword(
                condition, "constraint", check_constraint, cem
            )
            remove_keyword("constraint")
            # check period
            self.check_keyword(
                condition,
                "period",
                lambda period, cem: BASIC_TYPE_CHECKERS["scalar-unit.time"].check_type(
                    period, self, cem
                ),
                context_error_message,
            )
            remove_keyword("period")
            # check evaluations

            def check_evaluations(evaluations, cem):
                if evaluations < 1:
                    self.error(
                        cem
                        + ": "
                        + str(evaluations)
                        + " - must be greater than 0",
                        evaluations
                    )

            self.check_keyword(condition, "evaluations", check_evaluations, cem)
            remove_keyword("evaluations")
            # check method

            def check_method(method, cem):
                self.warning(
                    cem
                    + ": "
                    + str(method)
                    + " - unchecked",
                    method
                )

            self.check_keyword(condition, "method", check_method, cem)
            remove_keyword("method")
            # check either extended or short notation
            if extended_notation:
                if len(condition) != 0:
                    self.error(
                        cem
                        + ": "
                        + str(condition)
                        + " - unexpected",
                        condition
                    )
            else:
                # check the short notation
                self.check_condition_clause_definition(condition, cem)

        # restore current_targets and current_targets_*_type
        self.current_targets = previous_targets
        self.current_targets_activity_type = previous_targets_activity_type
        self.current_targets_condition_type = previous_targets_condition_type

        # check action
        self.iterate_over_list(trigger_definition, 'action', self.check_activity_definition, context_error_message)

    def check_substitution_mapping(self, substitution_mapping, context_error_message):

        def check_unmapped_definitions(
            node_type, keyword, kind_definition, evaluate_definition
        ):
            definitions = normalize_dict(substitution_mapping.get(keyword, {}))
            for def_name, definition in node_type.get(keyword, {}).items():
                if definitions.get(def_name) is None:
                    logger, reason = evaluate_definition(def_name, definition)
                    reason = " (" + reason + ")" if reason is not None else ""
                    if logger is not None:
                        # compute the location
                        keys = list(substitution_mapping.keys())
                        try:
                            location = keys[keys.index(keyword)]
                        except ValueError:
                            location = substitution_mapping
                        # log
                        logger(
                            context_error_message
                            + " - "
                            + kind_definition
                            + " "
                            + def_name
                            + " unmapped"
                            + reason,
                            location,
                        )

        # check node_type
        checked, node_type_name, node_type = self.check_type_in_template(
            "node", substitution_mapping, syntax.NODE_TYPE, context_error_message
        )
        # check substitution_filter
        substitution_filter = substitution_mapping.get("substitution_filter")
        if substitution_filter is not None:
            self.check_node_filter_definition(
                substitution_filter,
                node_type_name,
                node_type,
                context_error_message + ":" + "substitution_filter",
            )
        # check attributes - TODO check_attribute_mapping
        self.unchecked(substitution_mapping, syntax.ATTRIBUTES, context_error_message)
        # check that all attributes are mapped

        def check_ummapped_attribute_definition(attribute_name, attribute_definition):
            # produce an info message for each unmmapped attribute
            return self.info, None

        check_unmapped_definitions(
            node_type,
            syntax.ATTRIBUTES,
            "attribute",
            check_ummapped_attribute_definition,
        )
        # check properties
        self.iterate_over_map_of_assignments(
            self.check_property_mapping,
            syntax.PROPERTIES,
            substitution_mapping,
            node_type,
            node_type_name,
            context_error_message,
        )
        # TBR: it is not needed to check required properties of a substitution mapping
        # TBR:        self.check_required_properties(substitution_mapping, node_type, context_error_message)
        # check that all properties are mapped

        def check_ummapped_property_definition(property_name, property_definition):
            if is_required(property_definition) and not "default" in property_definition:
                # produce a warning for each unmmapped required property without default
                return self.info, "required: true, no default value"
            return None, None

        check_unmapped_definitions(
            node_type, syntax.PROPERTIES, "property", check_ummapped_property_definition
        )
        # check capabilities
        self.iterate_over_map_of_assignments(
            self.check_capability_mapping,
            syntax.CAPABILITIES,
            substitution_mapping,
            node_type,
            node_type_name,
            context_error_message,
        )

        # check that all capabilities are mapped
        def check_ummapped_capability_definition(
            capability_name, capability_definition
        ):
            # TODO factorize in syntax.py
            occurrences = [1, syntax.UNBOUNDED]
            if isinstance(capability_definition, dict):
                occurrences = capability_definition.get(syntax.OCCURRENCES, occurrences)
            if capability_name == "feature":
                # produce an info message for the feature capability
                return self.info, "occurrences: " + str(occurrences)
            # TBR
            elif occurrences[0] == 0:  # lower occurrence equals to 0
                # produce an info message for each optional requirement
                return self.warning, "occurrences: " + str(occurrences)
            ###
            else:
                # produce an error for each other unmapped capability
                return self.error, "occurrences: " + str(occurrences)

        check_unmapped_definitions(
            node_type,
            syntax.CAPABILITIES,
            "capability",
            check_ummapped_capability_definition,
        )
        # check requirements
        substitution_mapping_requirements = {
            syntax.REQUIREMENTS: syntax.get_requirements_dict(substitution_mapping)
        }
        self.iterate_over_map_of_assignments(
            self.check_requirement_mapping,
            syntax.REQUIREMENTS,
            substitution_mapping_requirements,
            node_type,
            node_type_name,
            context_error_message,
        )

        # check that all requirements are mapped
        def check_ummapped_requirement_definition(
            requirement_name, requirement_definition
        ):
            occurrences = requirement_definition.get(syntax.OCCURRENCES, [1, 1])
            if requirement_name == "dependency":
                # produce an info message for the dependency requirement
                return self.info, "occurrences: " + str(occurrences)
            if occurrences[1] == 0:  # upper occurrence equals to 0
                # produce an info message for each unboundable requirement
                return self.info, "occurrences: " + str(occurrences)
            # TBR
            elif occurrences[0] == 0:  # lower occurrence equals to 0
                # produce an info message for each optional requirement
                return self.warning, "occurrences: " + str(occurrences)
            ###
            else:
                # produce an error for each other unmapped requirement
                return self.error, "occurrences: " + str(occurrences)

        if self.configuration.get(
            TYPE_SYSTEM,
            "check-unmapped-substitution-mappings-requirements"
        ):
            check_unmapped_definitions(
                node_type,
                syntax.REQUIREMENTS,
                "requirement",
                check_ummapped_requirement_definition,
            )

        # check interfaces - TODO
        self.iterate_over_map_of_assignments(
            None,
            syntax.INTERFACES,
            substitution_mapping,
            node_type,
            node_type_name,
            context_error_message,
        )
        self.unchecked(substitution_mapping, syntax.INTERFACES, context_error_message)

        # check that all interfaces are mapped
        def check_ummapped_interface_definition(interface_name, interface_definition):
            # produce an info message for each unmapped interface
            return self.info, None
        check_unmapped_definitions(node_type, syntax.INTERFACES, 'interface', check_ummapped_interface_definition)


    def check_property_mapping(
        self,
        property_name,
        property_mapping,
        property_definition,
        context_error_message,
    ):
        def check_mapping(mapping, cem):
            expected_type = {
                "type": "list",
                "entry_schema": {"type": "string"},
                "constraints": [{"length": 1}],
            }
            self.check_value(mapping, expected_type, {}, cem)
            if not isinstance(mapping, list):
                return  # as this is not a list
            input_name = mapping[0]
            if not isinstance(input_name, str):
                return  # as this is not a string
            # TODO: following could be factorized with function get_input
            input_definition = (
                self.get_topology_template().get(syntax.INPUTS, {}).get(input_name)
            )
            if input_definition is None:
                self.error(
                    cem
                    + ": "
                    + str(mapping)
                    + " - "
                    + input_name
                    + " input undefined",
                    mapping
                )
                return
            input_type = input_definition.get(syntax.TYPE)
            value_type = property_definition.get(syntax.TYPE)
            if not self.type_system.is_derived_from(input_type, value_type):
                self.error(
                    cem
                    + ": "
                    + str(mapping)
                    + " - property of type "
                    + value_type
                    + " incompatible with input of type "
                    + input_type,
                    mapping
                )
                return

            # check if the mapped input is required but the property is not required
            if is_required(
                property_definition
            ) is False and input_definition.get(syntax.REQUIRED, True):
                self.warning(
                    cem
                    + ": "
                    + str(mapping)
                    + " - input "
                    + input_name
                    + " is required, but property "
                    + str(property_name)
                    + " is not required",
                    mapping
                )
                return

        def check_value(value, cem):
            self.warning(
                cem + ": " + str(value) + " - deprecated since TOSCA 1.3",
                value
            )
            self.check_value_assignment(property_name, value, property_definition, cem)

        if isinstance(property_mapping, dict):
            # multi-line grammar
            mapping = property_mapping.get("mapping")
            if mapping != None:
                # <property_name>:
                #   mapping: [ <input_name> ]
                check_mapping(mapping, context_error_message + ":mapping")
            value = property_mapping.get("value")
            if value != None:
                # <property_name>:
                #   value: <property_value> # This use is deprecated
                check_value(value, context_error_message + ":value")
        elif isinstance(property_mapping, list):
            # single-line grammar
            # <property_name>: [ <input_name> ]
            check_mapping(property_mapping, context_error_message)
        else:
            # single-line grammar
            # <property_name>: <property_value> # This use is deprecated
            check_value(property_mapping, context_error_message)

    def check_capability_mapping(
        self,
        capability_name,
        capability_mapping,
        capability_definition,
        context_error_message,
    ):
        topology_template = self.get_topology_template()

        def check_mapping_as_list(mapping, context_error_message):
            node_template_name = mapping[0]
            node_template_capability_name = mapping[1]

            node_template = topology_template.get(syntax.NODE_TEMPLATES, {}).get(
                node_template_name
            )
            if node_template is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + node_template_name
                    + " node template undefined",
                    node_template_name,
                )
                return
            node_template_type = self.type_system.merge_type(
                self.type_system.get_type_uri(node_template.get(syntax.TYPE))
            )
            node_template_type_capability_definitions = node_template_type.get(
                syntax.CAPABILITIES, {}
            )
            node_template_capability_definition = (
                node_template_type_capability_definitions.get(
                    node_template_capability_name
                )
            )
            if node_template_capability_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + node_template_capability_name
                    + " capability undefined",
                    node_template_capability_name,
                )
                return
            node_template_capability_type = syntax.get_capability_type(
                node_template_capability_definition
            )
            capability_type = syntax.get_capability_type(capability_definition)
            if not self.type_system.is_derived_from(
                node_template_capability_type, capability_type
            ):
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + capability_type
                    + " capability expected",
                    mapping
                )

        # check the short notation
        if isinstance(capability_mapping, list):
            check_mapping_as_list(capability_mapping, context_error_message)
            return

        # check the extended notation
        # check mapping - TODO
        self.unchecked(capability_mapping, syntax.MAPPING, context_error_message)
        # check properties - TODO check_property_assignment
        self.unchecked(capability_mapping, syntax.PROPERTIES, context_error_message)
        # check attributes - TODO check_attribute_assignment
        self.unchecked(capability_mapping, syntax.ATTRIBUTES, context_error_message)

    def check_requirement_mapping(
        self,
        requirement_name,
        requirement_mapping,
        requirement_definition,
        context_error_message,
    ):
        topology_template = self.get_topology_template()

        def check_mapping_as_list(mapping, context_error_message):
            node_template_name = mapping[0]
            node_template_requirement_name = mapping[1]
            # check occurrences
            occurrences = requirement_definition.get(syntax.OCCURRENCES, [1, 1])
            if occurrences == [0, 0]:
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - requirement mapping unexpected as defined occurrences are [0, 0]",
                    mapping)
                # mark that the requirement <node_template_name>.<node_template_reference_name> is connected
                self.all_the_node_template_requirements.get(node_template_name + '.' + node_template_requirement_name).connectIt()
                return

            node_template = topology_template.get(syntax.NODE_TEMPLATES, {}).get(
                node_template_name
            )
            if node_template is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + node_template_name
                    + " node template undefined",
                    node_template_name,
                )
                return
            node_template_type = self.type_system.merge_type(
                self.type_system.get_type_uri(node_template.get(syntax.TYPE))
            )
            node_template_type_requirement_definitions = syntax.get_requirements_dict(
                node_template_type
            )
            node_template_requirement_definition = (
                node_template_type_requirement_definitions.get(
                    node_template_requirement_name
                )
            )
            if node_template_requirement_definition is None:
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + node_template_requirement_name
                    + " requirement undefined",
                    node_template_requirement_name,
                )
                return
            node_template_requirement_capability = (
                node_template_requirement_definition.get(syntax.CAPABILITY)
            )
            requirement_capability = requirement_definition.get(syntax.CAPABILITY)
            if not self.type_system.is_derived_from(
                node_template_requirement_capability, requirement_capability
            ):
                self.error(
                    context_error_message
                    + ": "
                    + str(mapping)
                    + " - "
                    + requirement_capability
                    + " capability expected",
                    requirement_capability,
                )

            # mark that the requirement <node_template_name>.<node_template_reference_name> is connected
            self.all_the_node_template_requirements.get(
                node_template_name + "." + node_template_requirement_name
            ).connectIt()

        # check the short notation
        if isinstance(requirement_mapping, list):
            check_mapping_as_list(requirement_mapping, context_error_message)
            return

        # check the extended notation
        # check mapping - TODO
        self.unchecked(requirement_mapping, syntax.MAPPING, context_error_message)
        # check properties - TODO check_property_assignment
        self.unchecked(requirement_mapping, syntax.PROPERTIES, context_error_message)
        # check attributes - TODO check_attribute_assignment
        self.unchecked(requirement_mapping, syntax.ATTRIBUTES, context_error_message)

    def check_imperative_workflow_definition(
        self, workflow_name, workflow_definition, context_error_message
    ):
        # store the current imperative workflow used in check_step() to find current steps
        self.current_imperative_workflow = workflow_definition
        # store the current imperative workflow inputs used
        # in check_required_parameters() to find current default inputs
        self.current_default_inputs = workflow_definition.get(syntax.INPUTS, {})
        self.current_default_inputs_location = "workflows:" + workflow_name + ":inputs"
        # check description - nothing to do
        # check metadata - nothing to do
        # check inputs
        self.iterate_over_map_of_definitions(
            self.check_property_definition,
            syntax.INPUTS,
            workflow_definition,
            {},
            REFINE_OR_NEW,
            context_error_message,
        )
        # check preconditions
        self.iterate_over_list(
            workflow_definition,
            "preconditions",
            self.check_workflow_precondition_definition,
            context_error_message,
        )
        # check steps
        self.iterate_over_map_of_definitions(
            self.check_workflow_step_definition,
            "steps",
            workflow_definition,
            {},
            REFINE_OR_NEW,
            context_error_message,
        )
        # check implementation
        self.check_keyword(
            workflow_definition,
            syntax.IMPLEMENTATION,
            self.check_operation_implementation_definition,
            context_error_message,
        )
        # check outputs - TODO map of attribute_mapping
        self.unchecked(workflow_definition, syntax.OUTPUTS, context_error_message)
        # unset the current imperative workflow
        self.current_imperative_workflow = None
        self.current_default_inputs = {}
        self.current_default_inputs_location = None

    def check_workflow_precondition_definition(
        self, workflow_precondition_definition, context_error_message
    ):
        # check target
        target = workflow_precondition_definition.get("target")
        topology_template = self.get_topology_template()
        target_template = topology_template.get(syntax.NODE_TEMPLATES, {}).get(target)
        if target_template is None:
            target_template = topology_template.get(syntax.GROUPS, {}).get(target)
        if target_template is None:
            self.error(
                context_error_message
                + ":target: "
                + target
                + " - node template undefined",
                target,
            )
            target_type = {}
        else:
            checked, target_type_name, target_type = self.check_type_in_definition(
                "node",
                syntax.TYPE,
                target_template,
                target_template,
                context_error_message,
            )
        self.current_targets = [target]
        self.current_targets_activity_type = [target_type]
        self.current_targets_condition_type = [target_type]

        # check target_relationship
        def check_target_relationship(target_relationship, cem):
            requirement_definition = syntax.get_requirements_dict(target_type).get(
                target_relationship
            )
            if requirement_definition is None:
                self.error(
                    cem
                    + ": "
                    + target_relationship
                    + " - requirement undefined in "
                    + target,
                    target_relationship,
                )
            else:
                self.info(
                    cem
                    + ": "
                    + target_relationship
                    + " - requirement defined in "
                    + target,
                    target_relationship,
                )
                (
                    checked,
                    relationship_type_name,
                    relationship_type,
                ) = self.check_type_in_definition(
                    "relationship",
                    syntax.RELATIONSHIP,
                    requirement_definition,
                    {},
                    context_error_message,
                )
                self.current_targets = [
                    target + ".requirements." + target_relationship + ".relationship"
                ]
                self.current_targets_activity_type = [relationship_type]
                self.current_targets_condition_type = [relationship_type]

        self.check_keyword(
            workflow_precondition_definition,
            "target_relationship",
            check_target_relationship,
            context_error_message,
        )
        # check condition
        self.iterate_over_list(
            workflow_precondition_definition,
            "condition",
            self.check_condition_clause_definition,
            context_error_message,
        )

    def check_workflow_step_definition(
        self,
        workflow_step_name,
        workflow_step_definition,
        unused,
        context_error_message,
    ):
        # check target
        target = workflow_step_definition.get("target")
        topology_template = self.get_topology_template()
        target_template = topology_template.get(syntax.NODE_TEMPLATES, {}).get(target)
        if target_template is None:
            target_template = topology_template.get(syntax.GROUPS, {}).get(target)
        if target_template is None:
            self.error(
                context_error_message
                + ":target: "
                + target
                + " - node template or group undefined",
                target,
            )
            target_type = {}
        else:
            checked, target_type_name, target_type = self.check_type_in_definition(
                ["node", "group"],
                syntax.TYPE,
                target_template,
                target_template,
                context_error_message,
            )
        self.current_targets = [target]
        self.current_targets_activity_type = [target_type]
        self.current_targets_condition_type = [target_type]

        # check target_relationship
        def check_target_relationship(target_relationship, cem):
            requirement_definition = syntax.get_requirements_dict(target_type).get(
                target_relationship
            )
            if requirement_definition is None:
                self.error(
                    cem
                    + ": "
                    + target_relationship
                    + " - requirement undefined in "
                    + target,
                    target_relationship,
                )
            else:
                self.info(
                    cem
                    + ": "
                    + target_relationship
                    + " - requirement defined in "
                    + target,
                    target_relationship
                )
                (
                    checked,
                    relationship_type_name,
                    relationship_type,
                ) = self.check_type_in_definition(
                    "relationship",
                    syntax.RELATIONSHIP,
                    requirement_definition,
                    {},
                    context_error_message,
                )
                self.current_targets = [
                    target + ".requirements." + target_relationship + ".relationship"
                ]
                self.current_targets_activity_type = [relationship_type]
                self.current_targets_condition_type = [relationship_type]

        self.check_keyword(
            workflow_step_definition,
            "target_relationship",
            check_target_relationship,
            context_error_message,
        )
        # check operation_host - TODO string
        self.unchecked(
            workflow_step_definition, "operation_host", context_error_message
        )
        # check filter
        self.iterate_over_list(
            workflow_step_definition,
            "filter",
            self.check_condition_clause_definition,
            context_error_message,
        )
        # check activities
        activities = workflow_step_definition.get("activities")
        if activities is not None:
            if target_template is None:
                self.warning(
                    context_error_message
                    + ":activities: "
                    + str(activities)
                    + " - unchecked because target undefined",
                    activities,
                )
            else:
                self.iterate_over_list(
                    workflow_step_definition,
                    "activities",
                    self.check_activity_definition,
                    context_error_message,
                )
        # check on_success
        self.iterate_over_list(
            workflow_step_definition,
            "on_success",
            self.check_step,
            context_error_message,
        )
        # check on_failure
        self.iterate_over_list(
            workflow_step_definition,
            "on_failure",
            self.check_step,
            context_error_message,
        )

    # check that a step is defined in the current imperative workflow
    def check_step(self, step_name, cem):
        if self.current_imperative_workflow.get("steps", {}).get(step_name) is None:
            self.error(
                cem
                + ": "
                + step_name
                + " - step undefined",
                step_name
            )
