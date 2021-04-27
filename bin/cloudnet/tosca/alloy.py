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

import copy  # for deepcopy
import logging  # for logging purposes.

import cloudnet.tosca.configuration as configuration
import cloudnet.tosca.syntax as syntax
import cloudnet.tosca.utils as utils

from cloudnet.tosca.diagnostics import diagnostic
from cloudnet.tosca.processors import CEND, CRED, Generator
from cloudnet.tosca.syntax import *  # TODO to be removed

ALLOY = "Alloy"
SCOPE = "scope"
configuration.DEFAULT_CONFIGURATION[ALLOY] = {
    # Target directory where Alloy files are generated.
    Generator.TARGET_DIRECTORY: "Results/Alloy",
    SCOPE: {"for": 5, "Int": 8, "seq": 5, },
    "scalar-mapping": {
        "0.1 GHz": "1 Hz",  # for tosca_simple_yaml_1_2
        "8096 MB": "8 GB",  # for ETSI NFV SOL 001 Annex A examples
        "8192 MiB": "8 GB",  # for ETSI NFV SOL 001 Annex A examples
        "1800 MHz": "2 GHz",  # for ETSI NFV SOL 001 Annex A examples
        "4096 MB": "4 GB",  # for OASIS TOSCA/1.2/example-1.yaml
        "2048 MB": "2 GB",  # for OASIS TOSCA/1.2/example-2.yaml}
    },
    "open_tosca_definitions_version": True,
}

configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}

LOGGER = logging.getLogger(__name__)


#
# Alloy signatures and predicates.
#


class Alloy(object):
    """This class contains commodities for the Alloy specification
    language."""

    # Alloy single line comments.
    SINGLE_LINE_COMMENT = "//"

    #
    # Alloy keywords.
    #
    # TODO: add all other keywords.

    ALL = "all"
    BUT = "but"
    CHECK = "check"
    EXACTLY = "exactly"
    EXPECT = "expect"
    EXTENDS = "extends"
    FOR = "for"
    LET = "let"
    LONE = "lone"
    ONE = "one"
    OPEN = "open"
    RUN = "run"
    SEQ = "seq"
    SET = "set"
    SIG = "sig"
    SOME = "some"

    #
    # Alloy build-in sets.
    #

    univ = "univ"
    Int = "Int"
    seq = "seq"
    String = "String"

    # Following dictionary stores the extends relation between Alloy
    # signatures.
    the_extends_relation_between_signatures = {}

    def declare_signature(signature_name, extends_signature_name=None):
        """Declare that an Alloy signature extends another Alloy
        signature."""
        Alloy.the_extends_relation_between_signatures[
            signature_name
        ] = extends_signature_name

    def is_signature_declared(signature_name):
        """ Is an Alloy signature declared. """
        return (
                Alloy.the_extends_relation_between_signatures.get(signature_name)
                is not None
        )

    def get_superset(signature_name):
        """ Get the Alloy extends signature of a given Alloy signature. """
        return Alloy.the_extends_relation_between_signatures[signature_name]

    def get_all_supersets(signature_name):
        """Get all super sets of a given Alloy signature, i.e.,
        the transitive closure of the Alloy extends relation."""
        supersets = []
        try:
            extended_signature_name = Alloy.get_superset(signature_name)
        except KeyError as e:
            LOGGER.error(CRED + str(e) + CEND)
            diagnostic(
                gravity="error",
                message=str(e),
                cls=signature_name,
                file="",
                value=signature_name,
            )
            extended_signature_name = None

        while extended_signature_name:
            supersets.append(extended_signature_name)
            try:
                extended_signature_name = Alloy.get_superset(extended_signature_name)
            except KeyError as e:
                LOGGER.error(CRED + str(e) + " unknown!" + CEND)
                diagnostic(
                    gravity="error",
                    message=str(e) + " unknown",
                    cls=signature_name,
                    file="",
                    value=signature_name,
                )
                extended_signature_name = None

        return supersets


class AlloyCommandScope(object):
    """ Compute Alloy command scopes. """

    def __init__(self, type_system):
        self.type_system = type_system
        self.the_smallest_Int = 0
        self.the_biggest_Int = 0
        self.the_biggest_seq = 0
        self.signature_scopes = {}
        # By default, the scope of each declared signature is equals to zero.
        for (
                type_name,
                type_yaml,
        ) in Alloy.the_extends_relation_between_signatures.items():
            self.update_sig_scope(type_name, 0)

    def _increase_signature_scope_(self, signature_name, times):
        counter = self.signature_scopes.get(signature_name)
        if counter is None:
            counter = 0
        self.signature_scopes[signature_name] = counter + times

    def get_signature_scopes(self):
        return self.signature_scopes

    def get_seq_scope(self):
        return self.the_biggest_seq

    def update_Int_scope(self, integer):
        if integer < self.the_smallest_Int:
            self.the_smallest_Int = integer
        if integer > self.the_biggest_Int:
            self.the_biggest_Int = integer

    def update_seq_scope(self, seq):
        if len(seq) > self.the_biggest_seq:
            self.the_biggest_seq = len(seq)

    def update_sig_scope(self, signature_name, times=1):
        for superset in Alloy.get_all_supersets(signature_name):
            self._increase_signature_scope_(superset, times)
        self._increase_signature_scope_(signature_name, times)

    def print(self, file):
        print("the_smallest_Int=", self.the_smallest_Int, file=file)
        print("the_biggest_Int=", self.the_biggest_Int, file=file)
        print("the_biggest_seq=", self.the_biggest_seq, file=file)
        print("signature_scopes:", file=file)
        for name, counter in self.signature_scopes.items():
            print("*", counter, name, file=file)


class LocationGraphs(object):
    """ This class contains commodities for LocationGraphs.als. """

    # Its Alloy module name.
    LocationGraphs = "LocationGraphs"

    #
    # Its Alloy signatures.
    #
    # NOTE: Following shall be updated according to signatures declared in cloudnet/LocationGraphs.als.

    LocationGraph = LocationGraphs + "/LocationGraph"
    Location = LocationGraphs + "/Location"
    Value = LocationGraphs + "/Value"
    Name = LocationGraphs + "/Name"
    Process = LocationGraphs + "/Process"
    Sort = LocationGraphs + "/Sort"
    Role = LocationGraphs + "/Role"

    Alloy.declare_signature(LocationGraph)
    Alloy.declare_signature(Location)
    Alloy.declare_signature(Value)
    Alloy.declare_signature(Name, Value)
    Alloy.declare_signature(Process, Value)
    Alloy.declare_signature(Sort, Value)
    Alloy.declare_signature(Role, Value)


class TOSCA(object):
    """ This class contains commodities for TOSCA.als. """

    # Its Alloy module name.
    TOSCA = "TOSCA"

    #
    # Its Alloy signatures.
    #
    # NOTE: Following shall be updated according to signatures declared in cloudnet/TOSCA.als.

    Scalar = TOSCA + "/Scalar"
    scalar_unit_size = TOSCA + "/scalar_unit_size"
    scalar_unit_frequency = TOSCA + "/scalar_unit_frequency"
    scalar_unit_time = TOSCA + "/scalar_unit_time"
    ToscaComponent = TOSCA + "/ToscaComponent"
    ToscaRole = TOSCA + "/ToscaRole"
    ToscaValue = TOSCA + "/ToscaValue"
    TopologyTemplate = TOSCA + "/TopologyTemplate"
    Node = TOSCA + "/Node"
    Requirement = TOSCA + "/Requirement"
    Capability = TOSCA + "/Capability"
    Relationship = TOSCA + "/Relationship"
    Group = TOSCA + "/Group"
    Policy = TOSCA + "/Policy"
    Interface = TOSCA + "/Interface"
    Operation = TOSCA + "/Operation"
    Attribute = TOSCA + "/Attribute"
    Artifact = TOSCA + "/Artifact"
    Data = TOSCA + "/Data"
    AbstractProperty = TOSCA + "/AbstractProperty"
    Property = TOSCA + "/Property"
    Parameter = TOSCA + "/Parameter"

    Alloy.declare_signature(Scalar)
    Alloy.declare_signature(scalar_unit_size, Scalar)
    Alloy.declare_signature(scalar_unit_frequency, Scalar)
    Alloy.declare_signature(scalar_unit_time, Scalar)
    Alloy.declare_signature("TOSCA/map_integer/Map")
    Alloy.declare_signature("TOSCA/map_string/Map")
    Alloy.declare_signature("TOSCA/map_data/Map")
    Alloy.declare_signature("TOSCA/map_map_data/Map")
    Alloy.declare_signature(ToscaComponent, LocationGraphs.Location)
    Alloy.declare_signature(ToscaRole, LocationGraphs.Role)
    Alloy.declare_signature(ToscaValue, LocationGraphs.Value)
    Alloy.declare_signature(TopologyTemplate, LocationGraphs.LocationGraph)
    Alloy.declare_signature(Node, ToscaComponent)
    Alloy.declare_signature(Requirement, ToscaRole)
    Alloy.declare_signature(Capability, ToscaRole)
    Alloy.declare_signature(Relationship, ToscaComponent)
    Alloy.declare_signature(Group, ToscaComponent)
    Alloy.declare_signature(Policy, ToscaComponent)
    Alloy.declare_signature(Interface, ToscaValue)
    Alloy.declare_signature(Operation, ToscaValue)
    Alloy.declare_signature(Attribute, ToscaValue)
    Alloy.declare_signature(Artifact, ToscaValue)
    Alloy.declare_signature(Data, LocationGraphs.Value)
    Alloy.declare_signature(AbstractProperty, ToscaValue)
    Alloy.declare_signature(Property, AbstractProperty)
    Alloy.declare_signature(Parameter, AbstractProperty)

    # Declare signatures of tosca_simple_yaml_1_x.als
    Alloy.declare_signature("tosca_datatypes_Root", Data)
    Alloy.declare_signature("tosca_artifacts_Root", Artifact)
    Alloy.declare_signature("tosca_capabilities_Root", Capability)
    Alloy.declare_signature("tosca_relationships_Root", Relationship)
    Alloy.declare_signature("tosca_interfaces_Root", Interface)
    Alloy.declare_signature("tosca_nodes_Root", Node)
    Alloy.declare_signature("tosca_groups_Root", Group)
    Alloy.declare_signature("tosca_policies_Root", Policy)


# TODO: Would be removed.
def test(stream):
    acs = AlloyCommandScope()
    acs.update_Int_scope(-200)
    acs.update_Int_scope(300)
    acs.update_seq_scope([1, 2, 3])
    acs.update_sig_scope(TOSCA.Node)
    acs.update_sig_scope(TOSCA.Capability)
    acs.update_sig_scope(TOSCA.Interface)
    acs.update_sig_scope(TOSCA.Operation)
    acs.update_sig_scope("tosca_nodes_Root")
    acs.update_sig_scope("tosca_relationships_Root")
    acs.print(stream)
    return acs


#
# Alloy signature generator.
#


class AbstractAlloySigGenerator(Generator):
    def alloy_sig(self, typename):
        return utils.normalize_name(self.type_system.get_type_uri(typename))

    def get_tosca_keyword(self):
        return None

    def get_root_sig(self):
        return None

    def prefix_name(self, prefix, name):
        name = utils.normalize_name(name)
        if prefix:
            return prefix + "_" + name
        else:
            return name

    def get_max_int(self):
        return 2 ** (self.configuration.get(ALLOY, SCOPE, "Int") - 1) - 1

    def toscaProperty2alloyField(self, label):
        if label in ["version"]:
            label = "@" + label  # Suppress implicit expansion done by Alloy Analyzer.
        return label

    def get_implementation_artifact_type(self, implementation):
        result = None
        index = implementation.rfind(".")
        if index != -1:
            result = self.type_system.get_artifact_type_by_file_ext(
                implementation[index + 1:]
            )
        if result is None:
            self.warning(
                " no implementation artifact type associated to implementation '"
                + implementation
                + "'",
                implementation
            )
            result = "tosca.artifacts.Implementation"
        return result

    # TODO move to type_system.py

    def is_defined(self, node_type_name, item_kind, item_name, normalize=False):
        if node_type_name:
            node_type_yaml = self.type_system.get_type(node_type_name)
            if node_type_yaml:
                items = node_type_yaml.get(item_kind)
                if items:
                    if normalize:
                        items = utils.normalize_dict(items)
                    if items.get(item_name):
                        return True
                return self.is_defined(
                    node_type_yaml.get(DERIVED_FROM), item_kind, item_name, normalize
                )
        return False

    def is_property_defined(self, type_name, property_name):
        return self.is_defined(type_name, PROPERTIES, property_name)

    def is_attribute_defined(self, type_name, attribute_name):
        return self.is_defined(type_name, ATTRIBUTES, attribute_name)

    def is_interface_defined(self, type_name, interface_name):
        return self.is_defined(type_name, INTERFACES, interface_name)

    def is_capability_defined(self, type_name, capability_name):
        return self.is_defined(type_name, CAPABILITIES, capability_name)

    def is_requirement_defined(self, type_name, requirement_name):
        return self.is_defined(type_name, REQUIREMENTS, requirement_name, True)

    def is_artifact_defined(self, type_name, artifact_name):
        return self.is_defined(type_name, ARTIFACTS, artifact_name)

    # TODO end of move to type_system.py

    def get_cardinality(self, yaml, default_cardinality):
        if yaml is None:
            return default_cardinality
        occurrences = syntax.get_occurrences(yaml)
        if not occurrences:
            return default_cardinality
        elif occurrences[0] == 0:
            if occurrences[1] == 1:
                return Alloy.LONE
            else:
                return Alloy.SET
        elif occurrences[0] == 1:
            if occurrences[1] == 1:
                return Alloy.ONE
            else:
                return Alloy.SOME
        else:
            return Alloy.SET

    def get_capability_cardinality(self, capability_yaml):
        return self.get_cardinality(capability_yaml, Alloy.SOME)

    def get_requirement_cardinality(self, requirement_yaml):
        return self.get_cardinality(requirement_yaml, Alloy.ONE)

    def get_operation_implementation(self, operation_yaml):
        if isinstance(operation_yaml, str):
            return operation_yaml
        elif isinstance(operation_yaml, dict):
            implementation = operation_yaml.get(IMPLEMENTATION)
            if implementation is None:
                implementation = operation_yaml.get(VALUE)
            return implementation
        else:
            return None

    def generate_cardinality_fact(self, relation, size):
        if size > 0:
            self.generate("  #", relation, " = ", size, sep="")
        else:
            self.generate("  no", relation)

    def generate_occurrences_cardinality_constraints(
            self, relation_name, yaml, minimum
    ):
        occurrences = syntax.get_occurrences(yaml)
        if occurrences:
            lower_bound = int(occurrences[0])
            upper_bound = occurrences[1]
            if lower_bound <= 1 and upper_bound == 1:  # [0, 1] or [1, 1]
                return  # Already constrained when the Alloy field was declared, i.e., lone or one
            self.generate("  // YAML occurrences:", occurrences)
            if lower_bound > minimum:
                self.generate("  #", relation_name, " >= ", lower_bound, sep="")
            if upper_bound != UNBOUNDED:
                self.generate("  #", relation_name, " <= ", upper_bound, sep="")

    def generate_header(self, label, indent):
        indent = indent + Alloy.SINGLE_LINE_COMMENT
        self.generate(indent, "-" * 50)
        self.generate(indent, label)
        self.generate(indent, "-" * 50)
        self.generate()

    def generate_description(self, yaml, indent=""):
        if yaml is None:
            return
        if not isinstance(yaml, dict):
            return
        description = yaml.get(DESCRIPTION)
        if description:
            description = description.replace("\n", " ")
            indent = indent + Alloy.SINGLE_LINE_COMMENT
            self.generate(indent)
            self.generate(indent, description)
            self.generate(indent)

    def generate_sig_field(self, prefix, field_name, field_cardinality, field_type):
        self.generate(
            "  ",
            self.prefix_name(prefix, field_name),
            ": ",
            field_cardinality,
            " ",
            field_type,
            ",",
            sep="",
        )

    def generate_call_predicate(self, name, argument):
        self.generate("  ", name, "[", argument, "]", sep="")

    def get_map_module(self, property_yaml):
        entry_schema = syntax.get_entry_schema(property_yaml)
        entry_schema_type = syntax.get_entry_schema_type(property_yaml)
        if entry_schema_type == "integer":
            return "map_integer"
        elif entry_schema_type == "string":
            return "map_string"
        elif entry_schema_type == "map":
            return "map_" + self.get_map_module(entry_schema)
        # else:
        return "map_data"

    def get_map_signature(self, property_yaml):
        return "TOSCA/" + self.get_map_module(property_yaml) + "/Map"

    def stringify_value(
            self, value, value_type_definition, context_error_message, list_sep=" + "
    ):
        if isinstance(value, list):
            result = None
            index = 0
            for v in value:
                s = self.stringify_value(
                    v,
                    value_type_definition,
                    context_error_message + "[" + str(index) + "]",
                )
                if result:
                    result = result + list_sep + s
                else:
                    result = s
                index = index + 1
            return result

        if isinstance(value, dict):
            result = ""
            for key, v in value.items():
                PARAMETER_STRING_TYPE = {TYPE: "string"}
                if key == GET_INPUT:
                    if not isinstance(v, str):
                        self.error(
                            context_error_message
                            + ": get_input has only one string parameter",
                            v,
                        )
                    result = result + key + '["' + v + '"]'
                elif key == GET_PROPERTY:
                    nb_params = len(v)
                    node_name = v[0]
                    if node_name == "SELF":
                        node_name = self.SELF
                    if nb_params == 2:
                        result = result + node_name + ".property_" + v[1]
                    elif nb_params == 3:
                        # TODO: deal with v[1] as a capability name.
                        # TODO: still a lot of work to do
                        result = (
                                result
                                + node_name
                                + ".requirement_"
                                + v[1]
                                + ".relationship.target.property_"
                                + str(v[2])
                        )
                    else:
                        self.error(
                            context_error_message
                            + ": "
                            + key
                            + " - four or more parameters unsupported",
                            v,
                        )

                elif key == GET_ATTRIBUTE:
                    node_name = v[0]
                    if node_name == "SELF":
                        node_name = self.SELF
                    result += node_name + ".attribute_" + v[1]
                elif key == GET_ARTIFACT:
                    node_name = v[0]
                    if node_name == "SELF":
                        node_name = self.SELF
                    function_arguments = (
                            node_name
                            + ", "
                            + self.stringify_value(
                        v[1], PARAMETER_STRING_TYPE, context_error_message, ", "
                    )
                    )
                    result = result + key + "[" + function_arguments + "]"
                elif key in ["get_operation_output", "token", "get_secret"]:
                    self.warning(
                        context_error_message + ": " + key + " function unsupported", key
                    )
                    result = '"' + key + '[...]"'
                elif key in ["concat"]:
                    self.warning(
                        context_error_message + ": " + key + " function unsupported", key
                    )
                    result = '"' + key + '[...]"'
                else:
                    self.error(
                        context_error_message + ": " + key + " function undefined", key
                    )
                    result = '"' + key + '"'
            return result

        value_type = syntax.get_property_type(value_type_definition)

        if value_type == "boolean":
            if not isinstance(value, bool):
                self.error(
                    context_error_message + ": " + str(value) + " - boolean expected",
                    value,
                )
                return False
            return str(value).lower()

        elif value_type == "integer":
            if not isinstance(value, int):
                self.error(
                    context_error_message + ": " + str(value) + " - integer expected",
                    value,
                )
                return value
            MAX_INT = self.get_max_int()
            if value < MAX_INT:
                return str(value)
            else:
                self.warning(
                    context_error_message
                    + ": "
                    + str(value)
                    + " - integer narrowed to "
                    + str(MAX_INT),
                    value,
                )
                return str(MAX_INT)

        elif value_type == "float":
            # TODO: value must be a float else this is an error.
            self.warning(
                context_error_message
                + ": "
                + str(value)
                + " - float mapped to an Alloy string",
                value,
            )
            return '"' + str(value) + '"'

        elif value_type == "string":
            # str() is used as the value can be an integer, float, etc.
            value = str(value)
            if len(value) == 0:
                return "EMPTY_STRING"
            value = value.replace("\\.", "\\\\.")  # required for pattern.
            value = value.replace("\n", "\\n")  # required for multi-line properties.
            value = value.replace('"', '\\"')  # required for multi-line properties.
            return '"' + value + '"'

        elif value_type == "range":
            # TODO: value must be an integer else this is an error.
            return str(value)

        elif value_type.startswith("scalar-unit."):
            # TODO: value must be a string else this is an error.
            if not isinstance(value, str):
                self.error(
                    context_error_message
                    + ": "
                    + str(value)
                    + " - "
                    + value_type
                    + " expected",
                    value,
                )
                return value
            scalar_value, scalar_unit = self.split_scalar_unit(
                value, context_error_message
            )
            return str(scalar_value) + ", " + scalar_unit

        elif value_type == "version":
            # str() is used as the value can be an integer, float, etc.
            return '"' + str(value) + '"'

        # else
        self.error(context_error_message + ": " + value_type + " type unsupported", value_type)
        return None

    def split_scalar_unit(self, scalar, context_error_message):
        try:
            not_an_integer = False
            scalar_value, scalar_unit = utils.split_scalar_unit(scalar)
        except ValueError:
            not_an_integer = True
            scalar_unit = "UNKNOWN"  # TODO
        MAX_INT = self.get_max_int()
        if not_an_integer or scalar_value >= MAX_INT:
            # TODO: Improve the narrowing by changing the scalar unit, e.g. MB -> GB
            mapping = self.configuration.get(ALLOY, "scalar-mapping").get(scalar)
            if mapping:
                scalar_value, scalar_unit = self.split_scalar_unit(
                    mapping, context_error_message
                )
            else:
                scalar_value = MAX_INT
            self.warning(
                context_error_message
                + ": scalar-unit '"
                + scalar
                + "' is narrowed to '"
                + str(scalar_value)
                + " "
                + scalar_unit
                + "'",
                scalar,
            )
        return scalar_value, scalar_unit

    def generate_property(
            self, prefix, property_value, property_declaration, context_error_message
    ):
        property_type = syntax.get_property_type(property_declaration)
        if property_type is None:
            self.error(context_error_message + ": type undefined", property_declaration)
            return

        if not isinstance(property_type, str):
            self.error(
                context_error_message + ": " + str(property_type) + " invalid!",
                property_type,
            )
            return

        if property_type == "integer":  # special case to generate a comment
            comment = ""
            MAX_INT = self.get_max_int()
            if isinstance(property_value, int) and property_value >= MAX_INT:
                comment = (
                        " "
                        + Alloy.SINGLE_LINE_COMMENT
                        + " ISSUE: "
                        + str(property_value)
                        + " is a too big integer!!!"
                )
            self.generate(
                "  ",
                prefix,
                " = ",
                self.stringify_value(
                    property_value, property_declaration, context_error_message
                ),
                comment,
                sep="",
            )

        elif self.type_system.is_yaml_type(property_type):
            self.generate(
                "  ",
                prefix,
                " = ",
                self.stringify_value(
                    property_value, property_declaration, context_error_message
                ),
                sep="",
            )

        elif property_type == "range":
            if isinstance(property_value, dict):
                self.generate(
                    "  ",
                    prefix,
                    " = ",
                    self.stringify_value(
                        property_value, property_declaration, context_error_message
                    ),
                    sep="",
                )
            else:
                self.generate(
                    "  ",
                    prefix,
                    ".init[",
                    self.stringify_value(
                        property_value, property_declaration, context_error_message
                    ),
                    "]",
                    sep="",
                )

        elif property_type.startswith("scalar-unit."):
            if isinstance(property_value, dict):
                self.generate(
                    "  ",
                    prefix,
                    " = ",
                    self.stringify_value(
                        property_value, property_declaration, context_error_message
                    ),
                    sep="",
                )
            else:
                self.generate(
                    "  ",
                    prefix,
                    ".init[",
                    self.stringify_value(
                        property_value, property_declaration, context_error_message
                    ),
                    "]",
                    sep="",
                )

        elif property_type == "list":
            self.generate_cardinality_fact(prefix, len(property_value))
            index = 0
            entry_schema = property_declaration.get(ENTRY_SCHEMA)
            for value in property_value:
                tmp = "[" + str(index) + "]"
                self.generate_property(
                    prefix + tmp, value, entry_schema, context_error_message + tmp
                )
                index = index + 1

        elif property_type == "map":
            if not isinstance(property_value, dict):
                self.error(
                    context_error_message
                    + ": "
                    + str(property_value)
                    + " - map required",
                    property_value,
                )
                return

            if len(property_value):
                self.generate("  ", prefix, ".size[", len(property_value), "]", sep="")
                entry_schema = syntax.get_entry_schema(property_declaration)
                entry_schema_type = syntax.get_entry_schema_type(property_declaration)
                if entry_schema_type is None:
                    return
                if entry_schema_type == "map":
                    entry_cast_sig = self.get_map_signature(entry_schema)
                else:
                    entry_cast_sig = self.alloy_sig(entry_schema_type)
                keys = ""
                for key, value in property_value.items():
                    key = str(key)  # to be sure that key is a string
                    self.generate("  " + prefix + '.one_entry["' + key + '"]')
                    prefixed_entry = (
                            "("
                            + entry_cast_sig
                            + "<:("
                            + prefix
                            + '.entry["'
                            + key
                            + '"]))'
                    )
                    self.generate_property(
                        prefixed_entry,
                        value,
                        entry_schema,
                        context_error_message + ":" + key,
                    )
                    if keys:
                        keys = keys + " + "
                    keys = keys + '"' + key + '"'
                self.generate("  ", prefix, ".keys[", keys, "]", sep="")
            else:
                if is_property_required(property_declaration):
                    self.generate("  ", prefix, ".empty[]", sep="")
                else:
                    self.generate("  no", prefix)

        else:
            type_type = self.type_system.merge_type(property_type)
            if type_type:
                if property_value is None:
                    property_value = {}
                derived_from = syntax.get_derived_from(type_type)
                if self.type_system.is_yaml_type(derived_from):
                    self.generate_property(
                        prefix,
                        property_value,
                        {syntax.TYPE: derived_from},
                        context_error_message,
                    )
                    return
                if isinstance(property_value, dict) and property_value.get(GET_INPUT):
                    self.generate(
                        "  ",
                        prefix,
                        " = ",
                        self.stringify_value(
                            property_value, property_declaration, context_error_message
                        ),
                        sep="",
                    )
                    return
                if not isinstance(property_value, dict):
                    self.error(
                        context_error_message
                        + ": map expected instead of "
                        + str(property_value),
                        property_value,
                    )
                    return

                # self.generate_all_properties(...) produces a typing error.
                AbstractAlloySigGenerator.generate_all_properties(
                    self,
                    get_dict(type_type, PROPERTIES),
                    property_value,
                    prefix,
                    context_error_message,
                    property_name_format="%s",
                )
            else:
                self.generate("  // TODO", prefix, "=", property_value)
                self.error(
                    context_error_message
                    + ": "
                    + str(property_value)
                    + " - "
                    + property_type
                    + " type unsupported",
                    property_value,
                )

    def generate_all_properties(
            self,
            all_declared_properties,
            template_properties,
            prefixed_template_name,
            context_error_message,
            property_name_format="property_%s",
            generate_no_value=True,
    ):
        if template_properties is None:
            template_properties = {}

        # Check if each property of the template is defined in the template type.
        for property_name, property_yaml in template_properties.items():
            if not all_declared_properties.get(property_name):
                self.error(
                    context_error_message
                    + ": property '"
                    + property_name
                    + "' unknown",
                    property_name,
                )

        prefix = prefixed_template_name + "."

        for (property_name, property_declaration) in all_declared_properties.items():
            prefixed_property_name = prefix + self.toscaProperty2alloyField(
                property_name_format % utils.normalize_name(property_name)
            )
            property_value = template_properties.get(property_name)
            if property_value is not None:
                value = property_value
                if isinstance(value, str):  # escape multi-line properties
                    value = value.replace("\n", "\\n").replace('"', '\\"')
                self.generate("  // YAML ", property_name, ": ", value, sep="")
                self.generate_property(
                    prefixed_property_name,
                    property_value,
                    property_declaration,
                    context_error_message + ":" + property_name,
                )
            else:
                if is_property_required(property_declaration):
                    property_default = syntax.get_property_default(property_declaration)
                    if property_default is None:
                        self.error(
                            context_error_message
                            + ": property '"
                            + property_name
                            + "' must be set as it is required",
                            property_value,
                        )
                        self.generate(
                            "  // NOTE: The property '",
                            property_name,
                            "' must be set as it is required.",
                            sep="",
                        )
                    else:
                        self.generate(
                            "  // NOTE: The property '",
                            property_name,
                            "' is set to its default value.",
                            sep="",
                        )
                        self.generate_property(
                            prefixed_property_name,
                            property_default,
                            property_declaration,
                            context_error_message + ":" + property_name,
                        )
                else:
                    property_default = syntax.get_property_default(property_declaration)
                    if property_default:
                        self.generate(
                            "  // NOTE: The property '",
                            property_name,
                            "' is not required but has a default value.",
                            sep="",
                        )
                        self.generate_property(
                            prefixed_property_name,
                            property_default,
                            property_declaration,
                            context_error_message + ":" + property_name,
                        )
                    else:
                        if generate_no_value:
                            self.generate(
                                "  // NOTE: The property '",
                                property_name,
                                "' is not required.",
                                sep="",
                            )  # and has no default value
                            self.generate("  no  ", prefixed_property_name)

    def generate_constraints_facts(self, name, yaml, context_error_message):
        if isinstance(yaml, str):
            return
        constraints = syntax.get_constraints(yaml)
        if constraints:
            for constraint in constraints:
                for constraint_name, constraint_yaml in constraint.items():
                    ctx_error_msg = (
                            context_error_message + ":constraints:" + constraint_name
                    )
                    if constraint_name in ["in_range"]:
                        value = self.stringify_value(
                            constraint_yaml, yaml, ctx_error_msg, ", "
                        )
                    elif constraint_name in ["min_length", "max_length"]:
                        value = self.stringify_value(
                            constraint_yaml, {TYPE: "integer"}, ctx_error_msg, ", "
                        )
                    else:
                        value = self.stringify_value(
                            constraint_yaml, yaml, ctx_error_msg
                        )
                    self.generate_call_predicate(name + "." + constraint_name, value)
        entry_schema_yaml = syntax.get_entry_schema(yaml)
        if entry_schema_yaml:
            # TBR           if yaml.get(TYPE) == 'map':
            # TBR                self.generate('  ', name, '.entry_schema_type[', utils.normalize_name(entry_schema_yaml.get(TYPE)), ']', sep='')
            self.generate_constraints_facts(
                name + ".elems",
                entry_schema_yaml,
                context_error_message + ":entry_schema",
            )

    def generate_parameter_facts(
            self, indentation, prefix, parameter_name, parameter_yaml, context_error_message
    ):
        parameter_type = syntax.get_input_type(parameter_yaml)
        if parameter_type is None:
            parameter_type = "string"
            parameter_yaml[TYPE] = parameter_type
        self.generate(indentation, "// YAML type: ", parameter_type, sep="")
        self.generate(
            indentation,
            prefix,
            parameter_name,
            '.type = "',
            parameter_type,
            '"',
            sep="",
        )
        if parameter_type == "list":
            parameter_type = parameter_yaml.get("entry_schema", {}).get("type")
        elif parameter_type == "map":
            parameter_type = self.get_map_signature(parameter_yaml)
        self.generate(
            indentation,
            prefix,
            parameter_name,
            ".type[",
            self.alloy_sig(parameter_type),
            "]",
            sep="",
        )

        parameter_description = syntax.get_input_description(parameter_yaml)
        self.generate(
            indentation, "// YAML description: ", parameter_description, sep=""
        )
        if parameter_description:
            parameter_description = parameter_description.replace("\n", " ")
            self.generate(
                indentation,
                prefix,
                parameter_name,
                '.description = "',
                parameter_description,
                '"',
                sep="",
            )
        else:
            self.generate(
                indentation, "no ", prefix, parameter_name, ".description", sep=""
            )

        parameter_value = syntax.get_input_value(parameter_yaml)
        if parameter_value:
            self.generate(indentation, "// YAML value: ", parameter_value, sep="")
            self.generate_property(
                indentation[: len(indentation) - 2]
                + prefix
                + parameter_name
                + ".value",
                parameter_value,
                parameter_yaml,
                context_error_message + ":value",
            )

        parameter_required = syntax.is_property_required(parameter_yaml)
        self.generate(
            indentation, "// YAML required: ", str(parameter_required).lower(), sep=""
        )
        self.generate(
            indentation,
            prefix,
            parameter_name,
            ".required[",
            str(parameter_required).lower(),
            "]",
            sep="",
        )

        parameter_default = syntax.get_input_default(parameter_yaml)
        self.generate(indentation, "// YAML  default: ", parameter_default, sep="")
        if parameter_default:
            property_name = (
                    indentation[: len(indentation) - 2]
                    + "("
                    + self.alloy_sig(parameter_type)
                    + "<:"
                    + prefix
                    + parameter_name
                    + ".default)"
            )
            self.generate_property(
                property_name,
                parameter_default,
                parameter_yaml,
                context_error_message + ":default",
            )
        else:
            self.generate(
                indentation, "no ", prefix, parameter_name, ".default", sep=""
            )

        parameter_status = syntax.get_input_status(parameter_yaml)
        self.generate(indentation, "// YAML status: ", parameter_status, sep="")
        self.generate(
            indentation,
            prefix,
            parameter_name,
            '.status = "',
            parameter_status,
            '"',
            sep="",
        )

        self.generate_constraints_facts(
            indentation[: len(indentation) - 2] + prefix + parameter_name + ".value",
            parameter_yaml,
            context_error_message + ":" + parameter_name,
        )

        parameter_external_schema = syntax.get_input_external_schema(parameter_yaml)
        if parameter_external_schema:
            self.generate(
                indentation,
                "// YAML external_schema: ",
                parameter_external_schema,
                sep="",
            )
            self.generate(
                indentation,
                prefix,
                parameter_name,
                '.external_schema = "',
                parameter_external_schema,
                '"',
                sep="",
            )
        else:
            self.generate(
                indentation, "no ", prefix, parameter_name, ".external_schema", sep=""
            )

        parameter_metadata = syntax.get_input_metadata(parameter_yaml)
        if parameter_metadata:
            self.generate(indentation, "// YAML metadata: ", parameter_metadata)
            self.generate(
                indentation,
                "#",
                prefix,
                parameter_name,
                ".metadata = ",
                len(parameter_metadata),
                sep="",
            )
            for metadata_name, metadata_value in parameter_metadata.items():
                self.generate(
                    indentation,
                    prefix,
                    parameter_name,
                    '.metadata["',
                    metadata_name,
                    '"] = "',
                    metadata_value,
                    '"',
                    sep="",
                )
        else:
            self.generate(
                indentation, "no ", prefix, parameter_name, ".metadata", sep=""
            )

    def generate_inputs_facts(self, prefix, yaml, context_error_message):
        inputs = syntax.get_inputs(yaml)
        if inputs:
            self.generate("  // YAML inputs:")
            for (input_name, input_yaml) in inputs.items():
                self.generate("  // YAML   ", input_name, ":", sep="")
                self.generate(
                    "  one",
                    "input_" + input_name,
                    ":",
                    prefix + 'input["' + input_name + '"]',
                    "{",
                )
                self.generate_parameter_facts(
                    "    ",
                    "input_",
                    input_name,
                    input_yaml,
                    context_error_message + ":" + INPUTS + ":" + input_name,
                )
                self.generate("  }")

    def generate_all_sigs(self):
        return

    def generate_sig(self, name, yaml):
        return

    def generate_fields(self, name, yaml):
        return

    def generate_facts(self, name, yaml):
        return

    def generate_commands(self, name, yaml):
        self.generate_command_Show(name, yaml)

    # Commented currently
    # self.generate_command_Check(name, yaml)

    # Generate run Show_...
    def generate_command_Show(self, name, yaml):
        alloy_sig = self.alloy_sig(name)
        self.generate("/** There exists some", name, "*/")
        self.generate(Alloy.RUN, " Show_", alloy_sig, " {", sep="")
        if self.is_command_Show_no_name():
            self.generate("  ", alloy_sig, ".no_name[]", sep="")
        default_scope = self.configuration.get(ALLOY, SCOPE)
        self.generate("}", Alloy.FOR, default_scope["for"], Alloy.BUT)
        self.generate("  ", str(default_scope["Int"]), " ", Alloy.Int, ",", sep="")
        self.generate("  ", str(default_scope["seq"]), " ", Alloy.seq, ",", sep="")
        self.generate(
            "  // NOTE: Setting following scopes strongly reduces the research space."
        )
        for (sig_name, sig_scope) in self.get_command_Show_LG_scopes(
                name, yaml
        ).items():
            self.generate(
                "  ", Alloy.EXACTLY, " ", sig_scope, " ", sig_name, ",", sep=""
            )
        self.generate(" ", Alloy.EXACTLY, 1, alloy_sig)
        self.generate(" ", Alloy.EXPECT, 1)
        self.generate()

    def is_command_Show_no_name(self):
        return False

    def get_command_Show_LG_scopes(self, name, yaml):
        return {LocationGraphs.LocationGraph: 0, LocationGraphs.Location: 0}

    # Generate check Check_...
    def generate_command_Check(self, name, yaml):
        alloy_sig = self.alloy_sig(name)
        self.generate("/** Check all", name, "instances. */")
        self.generate(Alloy.CHECK, " Check_", alloy_sig, " {", sep="")
        self.generate("  all instance :", alloy_sig, " {")
        self.generate_command_Check_predicates(name, yaml)
        self.generate("  }")
        self.generate("}", Alloy.FOR, 10, Alloy.EXPECT, 0)
        self.generate()

    def generate_command_Check_predicates(self, name, yaml):
        return

    def generate_command_Check_predicates_for_naming(self, yaml, keyword, predicate):
        items = yaml.get(keyword)
        if items:
            self.generate_header(keyword.title(), "    ")
            for (item_name, item_yaml) in utils.normalize_dict(items).items():
                prefixed_item_name = self.prefix_name(predicate, item_name)
                self.generate(
                    "    instance.",
                    prefixed_item_name,
                    '.name = "',
                    item_name,
                    '"',
                    sep="",
                )
                self.generate(
                    "    instance.",
                    predicate,
                    '["',
                    item_name,
                    '"] = instance.',
                    prefixed_item_name,
                    sep="",
                )


class AbstractTypeGenerator(AbstractAlloySigGenerator):
    def generate_all_sigs(self):
        kind = self.get_kind()
        types = self.tosca_service_template.get_yaml().get(kind + "_types")
        if types:
            self.generate_header(kind.title() + " Types", "")
            for (type_name, type_yaml) in types.items():
                self.generate_sig(type_name, type_yaml)
        return

    # TODO: can be factorize in AbstractAlloySigGenerator
    def generate_sig(self, type_name, type_yaml):
        self.generate_description(type_yaml)
        if isinstance(type_yaml, dict):
            derived_from = type_yaml.get(DERIVED_FROM)
        else:
            derived_from = None
        if not derived_from or derived_from == "tosca.entity.Root":
            derived_from = self.get_root_sig()
        if self.type_system.is_yaml_type(derived_from):
            self.generate(
                Alloy.LET, self.alloy_sig(type_name), "=", self.alloy_sig(derived_from)
            )
            return
        self.generate(
            Alloy.SIG,
            self.alloy_sig(type_name),
            Alloy.EXTENDS,
            self.alloy_sig(derived_from),
        )
        self.generate("{")
        self.generate_all_properties(type_name, type_yaml)
        self.generate_fields(type_name, type_yaml)
        self.generate("} {")
        self.generate_facts(type_name, type_yaml)
        self.generate("}")
        self.generate()
        self.generate_commands(type_name, type_yaml)

    def generate_all_properties(self, type_name, type_yaml):
        if not isinstance(type_yaml, dict):
            return
        properties = type_yaml.get(PROPERTIES)
        if properties:
            self.generate_header("Properties", "  ")
            for (property_name, property_yaml) in properties.items():
                self.generate("  // YAML ", property_name, ": ", property_yaml, sep="")
                if self.is_property_defined(type_yaml.get(DERIVED_FROM), property_name):
                    self.generate("  // NOTE:", property_name, "overloaded")
                else:
                    self.generate_field("property", None, property_name, property_yaml)
                self.generate()

    def generate_field(self, field_kind, field_prefix, field_name, field_yaml):
        if isinstance(field_yaml, dict):
            self.generate_description(field_yaml, "  ")
            if is_property_required(field_yaml):
                field_cardinality = Alloy.ONE
            else:
                field_cardinality = Alloy.LONE
            field_type = field_yaml.get(TYPE)
            if field_type is None:
                self.error("type required for " + field_kind + " " + field_name, field_yaml)
                return
            field_sig = self.alloy_sig(field_type)
            if field_sig == "list":
                field_cardinality = Alloy.SEQ
                entry_schema_type = get_entry_schema_type(field_yaml)
                if entry_schema_type is None:
                    self.error(
                        " entry schema type required for "
                        + field_kind
                        + " "
                        + field_name,
                        field_yaml
                    )
                    return
                field_sig = self.alloy_sig(entry_schema_type)
            elif field_sig == "map":
                field_sig = self.get_map_signature(field_yaml)
        else:
            field_cardinality = Alloy.LONE
            field_sig = self.alloy_sig(field_yaml)
        self.generate_sig_field(field_prefix, field_name, field_cardinality, field_sig)

    def generate_attributes_fields(self, type_name, type_yaml):
        if type_yaml is None:
            return
        # Generate attributes
        attributes = type_yaml.get(ATTRIBUTES)
        if attributes:
            self.generate_header("Attributes", "  ")
            for (attribute_name, attribute_yaml) in attributes.items():
                self.generate(
                    "  // YAML ", attribute_name, ": ", attribute_yaml, sep=""
                )
                if self.is_attribute_defined(
                        type_yaml.get(DERIVED_FROM), attribute_name
                ):
                    self.generate("  // NOTE:", attribute_name, "overloaded")
                else:
                    self.generate_field(
                        "attribute", "attribute", attribute_name, attribute_yaml
                    )
                self.generate()

    def generate_facts(self, type_name, type_yaml):
        if not isinstance(type_yaml, dict):
            return
        properties = type_yaml.get(PROPERTIES)
        if properties:
            self.generate_header("Properties", "  ")
            for (property_name, property_yaml) in properties.items():
                if isinstance(property_yaml, dict):
                    self.generate_constraints_facts(
                        self.prefix_name(None, property_name),
                        property_yaml,
                        self.get_kind()
                        + "_types:"
                        + type_name
                        + ":properties:"
                        + property_name,
                    )
            self.generate()

    def generate_attributes_facts(self, type_name, type_yaml):
        if type_yaml is None:
            return
        attributes = type_yaml.get(ATTRIBUTES)
        if attributes:
            self.generate_header("Attributes", "  ")
            for (attribute_name, attribute_yaml) in attributes.items():
                self.generate_description(attribute_yaml, "  ")
                if self.is_attribute_defined(
                        type_yaml.get(DERIVED_FROM), attribute_name
                ):
                    self.generate("  // NOTE:", attribute_name, "overloaded")
                if isinstance(attribute_yaml, dict):
                    self.generate_constraints_facts(
                        self.prefix_name("attribute", attribute_name),
                        attribute_yaml,
                        self.get_kind()
                        + "_types:"
                        + type_name
                        + ":attributes:"
                        + attribute_name,
                    )
                self.generate()


class ArtifactTypeGenerator(AbstractTypeGenerator):
    def get_kind(self):
        return "artifact"

    def get_root_sig(self):
        return TOSCA.Artifact

    #    def generate_fields(self, artifact_type_name, artifact_type_yaml):
    # TODO: are other fields to generate?
    #        return

    def generate_facts(self, artifact_type_name, artifact_type_yaml):
        AbstractTypeGenerator.generate_facts(
            self, artifact_type_name, artifact_type_yaml
        )

        mime_type = artifact_type_yaml.get(MIME_TYPE)
        if mime_type:
            self.generate("  // YAML mime_type:", mime_type)
            self.generate_call_predicate(MIME_TYPE, '"' + mime_type + '"')
            self.generate()

        file_ext = artifact_type_yaml.get(FILE_EXT)
        if file_ext:
            self.generate("  // YAML file_ext:", file_ext)
            tmp = ""
            for ext in file_ext:
                if tmp != "":
                    tmp = tmp + " + "
                tmp = tmp + '"' + ext + '"'
            self.generate_call_predicate(FILE_EXT, tmp)

        # TODO: are other facts to generate?
        return

    #    def generate_commands(self, artifact_type_name, artifact_type_yaml):
    # TODO: are other commands to generate?
    #        return

    def is_command_Show_no_name(self):
        return True

    def get_command_Show_LG_scopes(self, artifact_type_name, artifact_type_yaml):
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 0,
            LocationGraphs.Name: 0,
            LocationGraphs.Role: 0,
            LocationGraphs.Process: 0,
            LocationGraphs.Sort: 0,
            TOSCA.Attribute: 0,
            TOSCA.Interface: 0,
            TOSCA.Operation: 0,
        }

    def generate_command_Check(self, artifact_type_name, artifact_type_yaml):
        # Generate nothing.
        return


class DataTypeGenerator(AbstractTypeGenerator):
    def get_kind(self):
        return "data"

    def get_root_sig(self):
        return TOSCA.Data

    #    def generate_fields(self, type_name, type_yaml):
    # TODO: are other fields to generate?
    #        return

    #    def generate_facts(self, type_name, type_yaml):
    # TODO: are other facts to generate?
    #        return

    #    def generate_commands(self, type_name, type_yaml):
    # TODO: are other commands to generate?
    #        return

    def get_command_Show_LG_scopes(self, data_type_name, data_type_yaml):
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 0,
            LocationGraphs.Name: 0,
            LocationGraphs.Role: 0,
            LocationGraphs.Process: 0,
            LocationGraphs.Sort: 0,
            TOSCA.Artifact: 0,
            TOSCA.Attribute: 0,
            TOSCA.Interface: 0,
            TOSCA.Operation: 0,
        }

    def generate_command_Check(self, data_type_name, data_type_yaml):
        # Generate nothing.
        return


class InterfaceTypeGenerator(AbstractTypeGenerator):
    def get_kind(self):
        return "interface"

    def get_root_sig(self):
        return TOSCA.Interface

    def generate_fields(self, interface_type_name, interface_type_yaml):
        # Generate properties
        AbstractTypeGenerator.generate_fields(
            self, interface_type_name, interface_type_yaml
        )

        # TODO: are other fields to generate?

        if interface_type_yaml:

            # compute operations of the derived_from interface type
            derived_from = interface_type_yaml.get(DERIVED_FROM)
            if derived_from is None:
                inherited_operations = {}
            else:
                derived_from_type = self.type_system.merge_type(derived_from)
                inherited_operations = syntax.get_operations(derived_from_type).get(
                    OPERATIONS
                )

            self.generate_header("Operations", "  ")
            for (operation_name, operation_yaml) in (
                    syntax.get_operations(interface_type_yaml).get(OPERATIONS).items()
            ):
                self.generate(
                    "  // YAML ", operation_name, ": ", operation_yaml, sep=""
                )
                if operation_name in inherited_operations:
                    self.generate("  // NOTE:", operation_name, "overloaded")
                else:
                    self.generate_description(operation_yaml, "  ")
                    self.generate_sig_field(
                        "operation", operation_name, Alloy.ONE, TOSCA.Operation
                    )
                self.generate()
        return

    def generate_facts(self, interface_type_name, interface_type_yaml):
        # Generate properties
        AbstractTypeGenerator.generate_facts(
            self, interface_type_name, interface_type_yaml
        )

        # TODO: are other facts to generate?
        if interface_type_yaml:
            self.generate_header("Operations", "  ")
            for (operation_name, operation_yaml) in (
                    syntax.get_operations(interface_type_yaml).get(OPERATIONS).items()
            ):
                self.generate(
                    "  // YAML ", operation_name, ": ", operation_yaml, sep=""
                )
                self.generate_description(operation_yaml, "  ")
                prefixed_operation_name = self.prefix_name("operation", operation_name)
                self.generate_call_predicate(
                    prefixed_operation_name + ".name", '"' + operation_name + '"'
                )
                self.generate_call_predicate("operation", prefixed_operation_name)

                # Translate inputs.
                self.generate_inputs_facts(
                    prefixed_operation_name + ".@",
                    operation_yaml,
                    INTERFACE_TYPES + ":" + interface_type_name + ":" + operation_name,
                )

                self.generate()
        return

    def is_command_Show_no_name(self):
        return True

    def get_command_Show_LG_scopes(self, interface_type_name, interface_type_yaml):
        # TODO fixer TOSCA_OPERATION selon nombre d'opérations de l'interface et des interfaces héritées
        if interface_type_yaml:
            operations = len(interface_type_yaml)
            for key in [DESCRIPTION, DERIVED_FROM, INPUTS]:
                if interface_type_yaml.get(key):
                    operations = operations - 1
        else:
            operations = 0
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 0,
            LocationGraphs.Name: 0,
            LocationGraphs.Role: 0,
            LocationGraphs.Process: 0,
            LocationGraphs.Sort: 0,
            TOSCA.Artifact: 0,
            TOSCA.Attribute: 0,
            TOSCA.Operation: operations,
            TOSCA.Parameter: 8,  # TODO: compute the minimal value exactly
        }

    def generate_command_Check_predicates(
            self, interface_type_name, interface_type_yaml
    ):
        for (operation_name, operation_yaml) in interface_type_yaml.items():
            self.generate(
                "    instance.",
                self.prefix_name("operation", operation_name),
                '.name = "',
                operation_name,
                '"',
                sep="",
            )
            self.generate(
                '    instance.operation["',
                operation_name,
                '"] = instance.',
                self.prefix_name("operation", operation_name),
                sep="",
            )
        # TODO: are other predicates to generate?


class CapabilityTypeGenerator(AbstractTypeGenerator):
    def get_kind(self):
        return "capability"

    def get_root_sig(self):
        return TOSCA.Capability

    def prefix_name(self, prefix, name):
        if prefix is None:
            prefix = "property"
        return AbstractTypeGenerator.prefix_name(self, prefix, name)

    def generate_fields(self, name, yaml):
        AbstractTypeGenerator.generate_fields(self, name, yaml)
        # Generate attributes
        self.generate_attributes_fields(name, yaml)

    def generate_facts(self, name, yaml):
        AbstractTypeGenerator.generate_facts(self, name, yaml)
        # Generate attributes
        self.generate_attributes_facts(name, yaml)

    #    def generate_commands(self, capability_type_name, capability_type_yaml):
    # TODO: are other commands to generate?
    #        return

    def is_command_Show_no_name(self):
        return True

    def get_command_Show_LG_scopes(self, capability_type_name, capability_type_yaml):
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 0,
            LocationGraphs.Name: 0,
            LocationGraphs.Role: 1,
            LocationGraphs.Process: 0,
            LocationGraphs.Sort: 0,
            TOSCA.Artifact: 0,
            TOSCA.Attribute: 0,
            TOSCA.Interface: 0,
            TOSCA.Requirement: 0,
            TOSCA.Operation: 0,
        }

    def generate_command_Check(self, capability_type_name, capability_type_yaml):
        # Generate nothing.
        return


class RequirementTypeGenerator(AbstractTypeGenerator):
    def get_kind(self):
        return "requirement"

    def get_root_sig(self):
        return TOSCA.Requirement

    #    def generate_fields(self, type_name, type_yaml):
    # TODO: are other fields to generate?
    #        return

    #    def generate_facts(self, type_name, type_yaml):
    # TODO: are other facts to generate?
    #        return

    #    def generate_commands(self, type_name, type_yaml):
    # TODO: are other commands to generate?
    #        return

    def is_command_Show_no_name(self):
        return True

    def get_command_Show_LG_scopes(self, requirement_name, requirement_yaml):
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 0,
            LocationGraphs.Name: 0,
            LocationGraphs.Role: 1,
            LocationGraphs.Process: 0,
            LocationGraphs.Sort: 0,
            TOSCA.Artifact: 0,
            TOSCA.Attribute: 0,
            TOSCA.Capability: 0,
            TOSCA.Interface: 0,
            TOSCA.Requirement: 1,
            TOSCA.Operation: 0,
        }


class ToscaComponentTypeGenerator(AbstractTypeGenerator):
    def prefix_name(self, prefix, name):
        if prefix is None:
            prefix = "property"
        return AbstractTypeGenerator.prefix_name(self, prefix, name)

    def generate_fields(self, name, yaml):
        AbstractTypeGenerator.generate_fields(self, name, yaml)

        # Generate attributes
        self.generate_attributes_fields(name, yaml)

        # Generate interfaces
        interfaces = yaml.get(INTERFACES)
        if interfaces:
            self.generate()
            self.generate_header("Interfaces", "  ")
            for (interface_name, interface_yaml) in interfaces.items():
                self.generate(
                    "  // YAML ", interface_name, ": ", interface_yaml, sep=""
                )
                if self.is_interface_defined(yaml.get(DERIVED_FROM), interface_name):
                    self.generate("  // NOTE:", interface_name, "overloaded")
                else:
                    interface_type = interface_yaml.get(TYPE)
                    if interface_type:
                        self.generate_sig_field(
                            "interface",
                            interface_name,
                            Alloy.ONE,
                            self.alloy_sig(interface_type),
                        )
                self.generate()

        # TODO: are other fields (inputs) to generate?

    #        return

    def generate_facts(self, name, yaml):
        AbstractTypeGenerator.generate_facts(self, name, yaml)

        # Generate attributes
        self.generate_attributes_facts(name, yaml)

        # Generate interfaces
        interfaces = yaml.get(INTERFACES)
        if interfaces:
            self.generate_header("Interfaces", "  ")
            for (interface_name, interface_yaml) in interfaces.items():
                self.generate(
                    "  // YAML ", interface_name, ": ", interface_yaml, sep=""
                )
                if self.is_interface_defined(yaml.get(DERIVED_FROM), interface_name):
                    self.generate("  // NOTE:", interface_name, "overloaded")
                else:
                    self.generate("  interface[interface_", interface_name, "]", sep="")
                    self.generate(
                        "  interface_",
                        interface_name,
                        '.name["',
                        interface_name,
                        '"]',
                        sep="",
                    )
                if interface_yaml:
                    for (operation_name, operation_yaml) in (
                            syntax.get_operations(interface_yaml).get("operations").items()
                    ):
                        self.generate("  // YAML   ", operation_name, ":", sep="")
                        if isinstance(operation_yaml, dict):
                            # Translate inputs.
                            self.generate_inputs_facts(
                                self.prefix_name("interface", interface_name)
                                + "."
                                + self.prefix_name("operation", operation_name)
                                + ".",
                                operation_yaml,
                                "???",
                            )

                        # Generate implementation.
                        prefixed_operation = (
                                self.prefix_name("interface", interface_name)
                                + "."
                                + self.prefix_name("operation", operation_name)
                        )
                        implementation = self.get_operation_implementation(
                            operation_yaml
                        )
                        if implementation:

                            def generate_implementation_fact(implementation):
                                artifacts = syntax.get_dict(yaml, ARTIFACTS)
                                if artifacts is not None and artifacts.get(
                                        implementation
                                ):
                                    self.generate(
                                        "  ",
                                        prefixed_operation,
                                        ".implementation = "
                                        + self.prefix_name("artifact", implementation),
                                        sep="",
                                    )
                                else:
                                    artifact_type_sig = self.alloy_sig(
                                        self.get_implementation_artifact_type(
                                            implementation
                                        )
                                    )
                                    self.generate(
                                        "  ",
                                        prefixed_operation,
                                        ".implementation[",
                                        artifact_type_sig,
                                        ', "',
                                        implementation,
                                        '"]',
                                        sep="",
                                    )

                            if isinstance(implementation, str):
                                # Short notation
                                generate_implementation_fact(implementation)
                            else:
                                # Extended notation
                                # some keynames are not supported currently!
                                for unsupported_key in [
                                    "dependencies",
                                    "timeout",
                                    "operation_host",
                                ]:
                                    if implementation.get(unsupported_key) is not None:
                                        self.warning(
                                            " implementation "
                                            + str(implementation)
                                            + " - "
                                            + unsupported_key
                                            + " unsupported by Alloy generator",
                                            unsupported_key
                                        )
                                # only primary is supported currently!
                                primary = implementation.get("primary")
                                if primary is None:
                                    self.error(
                                        " implementation "
                                        + str(implementation)
                                        + " - primary artifact missed",
                                        implementation
                                    )
                                    continue
                                # generate the Alloy fact
                                if isinstance(primary, str):
                                    # Short notation
                                    generate_implementation_fact(primary)
                                else:
                                    # Extended notation
                                    artifact_type_sig = self.alloy_sig(
                                        primary.get("type")
                                    )
                                    artifact_file = primary.get("file")
                                    self.generate(
                                        "  ",
                                        prefixed_operation,
                                        ".implementation[",
                                        artifact_type_sig,
                                        ', "',
                                        artifact_file,
                                        '"]',
                                        sep="",
                                    )

                self.generate()

        # TODO: are other facts to generate?
        return

    #    def generate_commands(self, type_name, type_yaml):
    # TODO: are other commands to generate?
    #        return

    def is_command_Show_no_name(self):
        return True


class RelationshipTypeGenerator(ToscaComponentTypeGenerator):
    def get_kind(self):
        return "relationship"

    def get_root_sig(self):
        return TOSCA.Relationship

    #    def generate_fields(self, relationship_type_name, relationship_type_yaml):
    # TODO: are other fields to generate?
    #        return

    def generate_facts(self, relationship_type_name, relationship_type_yaml):
        ToscaComponentTypeGenerator.generate_facts(
            self, relationship_type_name, relationship_type_yaml
        )

        valid_target_types = relationship_type_yaml.get(VALID_TARGET_TYPES)
        if valid_target_types:
            types = ""
            for valid_target_type in valid_target_types:
                if types != "":
                    types = types + " + "
                types = types + self.alloy_sig(valid_target_type)
            self.generate_call_predicate("valid_target_types", types)

        # TODO: artifacts?

        # TODO: are other facts to generate?
        return

    #    def generate_commands(self, relationship_type_name, relationship_type_yaml):
    # TODO: are other commands to generate?
    #        return

    def get_command_Show_LG_scopes(
            self, relationship_type_name, relationship_type_yaml
    ):
        # TODO calculer TOSCA_OPERATION = somme all interfaces nombre d'opérations et des interfaces héritées
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 3,  # 1 relationship = 1 location + 2 connected nodes
            TOSCA.Group: 0,
            TOSCA.Policy: 0,
        }

    def generate_command_Check(self, relationship_type_name, relationship_type_yaml):
        # Generate nothing.
        return


class NodeTypeGenerator(ToscaComponentTypeGenerator):
    def get_kind(self):
        return "node"

    def get_root_sig(self):
        return TOSCA.Node

    def generate_fields(self, node_type_name, node_type_yaml):
        ToscaComponentTypeGenerator.generate_fields(
            self, node_type_name, node_type_yaml
        )

        # Generate capabilities
        capabilities = node_type_yaml.get(CAPABILITIES)
        if capabilities:
            self.generate_header("Capabilities", "  ")
            for (capability_name, capability_yaml) in capabilities.items():
                self.generate(
                    "  // YAML ", capability_name, ": ", capability_yaml, sep=""
                )
                if self.is_capability_defined(
                        node_type_yaml.get(DERIVED_FROM), capability_name
                ):
                    self.generate(
                        " ", Alloy.SINGLE_LINE_COMMENT, capability_name, "overloaded"
                    )
                else:
                    if isinstance(capability_yaml, str):
                        capability_type = capability_yaml
                        capability_cardinality = self.get_capability_cardinality({})
                    elif isinstance(capability_yaml, dict):
                        self.generate_description(capability_yaml, "  ")
                        capability_type = get_capability_type(capability_yaml)
                        capability_cardinality = self.get_capability_cardinality(
                            capability_yaml
                        )
                    else:
                        self.error(
                            "Invalid capability declaration "
                            + capability_name
                            + ": "
                            + capability_yaml,
                            capability_yaml,
                        )
                        capability_type = TOSCA.Capability
                        capability_cardinality = Alloy.ONE
                    self.generate_sig_field(
                        "capability",
                        capability_name,
                        capability_cardinality,
                        self.alloy_sig(capability_type),
                    )
                self.generate()

        # Generate requirements
        requirements = node_type_yaml.get(REQUIREMENTS)
        if requirements:
            self.generate_header("Requirements", "  ")
            requirements = utils.normalize_dict(requirements)
            for (requirement_name, requirement_yaml) in requirements.items():
                self.generate(
                    "  // YAML ", requirement_name, ": ", requirement_yaml, sep=""
                )
                if self.is_requirement_defined(
                        node_type_yaml.get(DERIVED_FROM), requirement_name
                ):
                    self.generate(
                        " ", Alloy.SINGLE_LINE_COMMENT, requirement_name, "overloaded"
                    )
                else:
                    self.generate_description(requirement_yaml, "  ")
                    requirement_type = (
                        None  # syntax.get_requirement_capability(requirement_yaml)
                    )
                    if not requirement_type:
                        requirement_type = TOSCA.Requirement
                    requirement_cardinality = self.get_requirement_cardinality(
                        requirement_yaml
                    )
                    self.generate_sig_field(
                        "requirement",
                        requirement_name,
                        requirement_cardinality,
                        self.alloy_sig(requirement_type),
                    )
                self.generate()

        # Generate artifacts
        artifacts = syntax.get_dict(node_type_yaml, ARTIFACTS)
        if artifacts:
            self.generate_header("Artifacts", "  ")
            artifacts = utils.normalize_dict(artifacts)
            for (artifact_name, artifact_yaml) in artifacts.items():
                self.generate_description(artifact_yaml, "  ")
                artifact_type = syntax.get_artifact_type(artifact_yaml)
                if artifact_type is None:
                    artifact_type = TOSCA.Artifact
                artifact_cardinality = Alloy.ONE
                self.generate("  // YAML ", artifact_name, ": ", artifact_yaml, sep="")
                if self.is_artifact_defined(
                        node_type_yaml.get(DERIVED_FROM), artifact_name
                ):
                    self.generate("  // NOTE:", artifact_name, "overloaded")
                else:
                    self.generate_sig_field(
                        "artifact",
                        artifact_name,
                        artifact_cardinality,
                        self.alloy_sig(artifact_type),
                    )
                self.generate()

        # TODO: are other fields to generate?
        return

    def generate_facts(self, node_type_name, node_type_yaml):
        # Generate attributes and interfaces
        ToscaComponentTypeGenerator.generate_facts(self, node_type_name, node_type_yaml)

        # Generate capabilities
        capabilities = node_type_yaml.get(CAPABILITIES)
        if capabilities:
            self.generate_header("Capabilities", "  ")
            for (capability_name, capability_yaml) in capabilities.items():

                if isinstance(capability_yaml, dict):
                    self.generate_description(capability_yaml, "  ")
                self.generate(
                    "  // YAML ", capability_name, ": ", capability_yaml, sep=""
                )
                capability_alloy_field_name = self.prefix_name(
                    "capability", capability_name
                )
                if not self.is_capability_defined(
                        node_type_yaml.get(DERIVED_FROM), capability_name
                ):
                    self.generate_call_predicate(
                        capability_alloy_field_name + ".name",
                        '"' + capability_name + '"',
                    )
                    self.generate_call_predicate(
                        "capability", capability_alloy_field_name
                    )
                if isinstance(capability_yaml, dict):
                    valid_source_types = capability_yaml.get(VALID_SOURCE_TYPES)
                    if valid_source_types:
                        tmp = ""
                        for valid_source_type in valid_source_types:
                            if tmp != "":
                                tmp = tmp + " + "
                            tmp = tmp + self.alloy_sig(valid_source_type)
                        self.generate_call_predicate(
                            capability_alloy_field_name + ".valid_source_types", tmp
                        )
                    #                    else:
                    #                        self.error(node_type_name + ':' + capability_name + ': valid_source_types must list one or more node types')
                    self.generate_occurrences_cardinality_constraints(
                        capability_alloy_field_name, capability_yaml, 1
                    )
                self.generate()

        # Generate requirements
        requirements = node_type_yaml.get(REQUIREMENTS)
        if requirements:
            self.generate_header("Requirements", "  ")
            requirements = utils.normalize_dict(requirements)
            for (requirement_name, requirement_yaml) in requirements.items():
                if requirement_yaml is not None:
                    self.generate(
                        "  // YAML ", requirement_name, ": ", requirement_yaml, sep=""
                    )
                    self.generate_description(requirement_yaml, "  ")
                    prefixed_requirement_name = self.prefix_name(
                        "requirement", requirement_name
                    )
                    if not self.is_requirement_defined(
                            node_type_yaml.get(DERIVED_FROM), requirement_name
                    ):
                        self.generate(
                            '  requirement["',
                            requirement_name,
                            '", ',
                            prefixed_requirement_name,
                            "]",
                            sep="",
                        )
                    requirement_capability = syntax.get_requirement_capability(
                        requirement_yaml
                    )
                    if requirement_capability:
                        # TODO generate_call_predicate
                        self.generate(
                            "  ",
                            prefixed_requirement_name,
                            ".capability[",
                            self.alloy_sig(requirement_capability),
                            "]",
                            sep="",
                        )
                    requirement_relationship = syntax.get_requirement_relationship(
                        requirement_yaml
                    )
                    requirement_relationship_type = syntax.get_relationship_type(
                        requirement_relationship
                    )
                    if requirement_relationship_type:
                        # TODO generate_call_predicate
                        self.generate(
                            "  ",
                            prefixed_requirement_name,
                            ".relationship[",
                            self.alloy_sig(requirement_relationship_type),
                            "]",
                            sep="",
                        )
                    requirement_node = get_requirement_node_type(requirement_yaml)
                    if requirement_node:
                        # TODO generate_call_predicate
                        self.generate(
                            "  ",
                            prefixed_requirement_name,
                            ".node[",
                            self.alloy_sig(requirement_node),
                            "]",
                            sep="",
                        )
                    self.generate_occurrences_cardinality_constraints(
                        prefixed_requirement_name, requirement_yaml, 0
                    )
                    self.generate()

        # Generate artifacts
        artifacts = syntax.get_dict(node_type_yaml, ARTIFACTS)
        if artifacts:
            self.generate_header("Artifacts", "  ")
            for (artifact_name, artifact_yaml) in artifacts.items():
                self.generate("  // YAML ", artifact_name, ": ", artifact_yaml, sep="")
                self.generate_description(artifact_yaml, "  ")
                prefixed_artifact_name = self.prefix_name("artifact", artifact_name)
                self.generate_call_predicate(
                    prefixed_artifact_name + ".name", '"' + artifact_name + '"'
                )
                self.generate_call_predicate("artifact", prefixed_artifact_name)
                self.generate()

    #    def generate_commands(self, type_name, type_yaml):
    # TODO: are other commands to generate?
    #        return

    def get_command_Show_LG_scopes(self, node_type_name, node_type_yaml):
        # TODO calculer TOSCA_OPERATION = somme all interfaces nombre d'opérations et des interfaces héritées
        nb_locations = self.get_required_locations(node_type_name)
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: nb_locations,
            LocationGraphs.Value: 35,
            LocationGraphs.Name: nb_locations,
            #                   LocationGraphs.Role: 10, # TODO: compute exact type
            LocationGraphs.Sort: 1,
            LocationGraphs.Process: 1,
            #                   TOSCA.Interface: 2, # TODO: compute exact scope
            #                   TOSCA.Operation: 27, # TODO: compute exact scope
            TOSCA.Group: 0,
            TOSCA.Policy: 0,
        }

    # NOTE: Following is a heuristic to compute the scope of LG locations.
    def get_required_locations(self, node_type_name, default_result=1):
        if not node_type_name:
            return default_result
        node_type_yaml = self.type_system.get_type(node_type_name)
        if not node_type_yaml:
            return default_result
        result = default_result
        # Iterate over requirements
        requirements = node_type_yaml.get(REQUIREMENTS)
        if requirements:
            requirements = utils.normalize_dict(requirements)
            for (requirement_name, requirement_yaml) in requirements.items():
                if requirement_yaml is not None:
                    if self.get_requirement_cardinality(requirement_yaml) == Alloy.ONE:
                        result = result + 1
                        requirement_node = syntax.get_requirement_node_type(
                            requirement_yaml
                        )
                        if requirement_node is not None:
                            result = result + self.get_required_locations(
                                requirement_node
                            )

        # Iterate over derived_from
        derived_from = node_type_yaml.get(DERIVED_FROM)
        if not self.type_system.is_derived_from(derived_from, node_type_name):
            result = result + self.get_required_locations(derived_from, 0)
        return result

    def generate_command_Check_predicates(self, node_type_name, node_type_yaml):
        # Check capabilities
        self.generate_command_Check_predicates_for_naming(
            node_type_yaml, CAPABILITIES, "capability"
        )
        # Check requirements
        self.generate_command_Check_predicates_for_naming(
            node_type_yaml, REQUIREMENTS, "requirement"
        )
        # Check artifacts
        self.generate_command_Check_predicates_for_naming(
            node_type_yaml, ARTIFACTS, "artifact"
        )
        # TODO: are other predicates to generate?
        return


class GroupTypeGenerator(ToscaComponentTypeGenerator):
    def get_kind(self):
        return "group"

    def get_root_sig(self):
        return TOSCA.Group

    def generate_fields(self, group_type_name, group_type_yaml):
        # Generate attributes and interfaces
        ToscaComponentTypeGenerator.generate_fields(
            self, group_type_name, group_type_yaml
        )
        # TODO: are other facts to generate?
        return

    def generate_facts(self, group_type_name, group_type_yaml):
        # Generate attributes and interfaces
        ToscaComponentTypeGenerator.generate_facts(
            self, group_type_name, group_type_yaml
        )

        # Generate members.
        members = group_type_yaml.get(MEMBERS)
        if members:
            types = ""
            for member in members:
                if types != "":
                    types = types + " + "
                types = types + self.alloy_sig(member)
            self.generate_call_predicate("members_type", types)

        # TODO: are other facts to generate?
        return

    #    def generate_commands(self, group_type_name, group_type_yaml):
    # TODO: are other commands to generate?
    #        return

    def get_command_Show_LG_scopes(self, name, yaml):
        # TODO calculer TOSCA_OPERATION = somme all interfaces nombre d'opérations et des interfaces héritées
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 1,
            LocationGraphs.Name: 1,
            LocationGraphs.Process: 1,
            LocationGraphs.Sort: 1,
        }


class PolicyTypeGenerator(ToscaComponentTypeGenerator):
    def get_kind(self):
        return "policy"

    def get_root_sig(self):
        return TOSCA.Policy

    def generate_fields(self, policy_type_name, policy_type_yaml):
        # Generate attributes and interfaces
        ToscaComponentTypeGenerator.generate_fields(
            self, policy_type_name, policy_type_yaml
        )
        # TODO: are other facts to generate?
        return

    def generate_facts(self, policy_type_name, policy_type_yaml):
        # Generate attributes and interfaces
        ToscaComponentTypeGenerator.generate_facts(
            self, policy_type_name, policy_type_yaml
        )

        # Generate targets.
        targets = policy_type_yaml.get(TARGETS)
        if targets is not None:
            self.generate("  // YAML targets:", targets)
            if len(targets) > 0:
                types = ""
                for target in targets:
                    if types != "":
                        types = types + " + "
                    types = types + self.alloy_sig(target)
            else:
                types = "none"
            self.generate_call_predicate("targets_type", types)

        # TODO: are other facts to generate?
        return

    #    def generate_commands(self, type_name, type_yaml):
    # TODO: are other commands to generate?
    #        return

    def get_command_Show_LG_scopes(self, name, yaml):
        # TODO calculer TOSCA_OPERATION = somme all interfaces nombre d'opérations et des interfaces héritées
        return {
            LocationGraphs.LocationGraph: 0,
            LocationGraphs.Location: 1,
            LocationGraphs.Name: 1,
            LocationGraphs.Process: 1,
            LocationGraphs.Sort: 1,
        }


class TopologyTemplateGenerator(AbstractAlloySigGenerator):
    def get_kind(self):
        return "TopologyTemplate"

    def get_root_sig(self):
        return TOSCA.TopologyTemplate

    def generate_all_sigs(self):
        topology_template_yaml = self.tosca_service_template.get_yaml().get(
            "topology_template"
        )
        if not topology_template_yaml:
            return
        # TODO: Can be factorized in AbstractAlloySigGenerator
        self.generate_header("Topology Template", "")
        path = self.tosca_service_template.get_filename()
        topology_template_sig_name = (
                utils.normalize_name(path[: path.rfind(".")]) + "_topology_template"
        )
        self.generate("sig", topology_template_sig_name, "extends", self.get_root_sig())
        self.generate("{")
        self.generate_fields(topology_template_sig_name, topology_template_yaml)
        self.generate("} {")
        self.generate_facts(topology_template_sig_name, topology_template_yaml)
        self.generate("}")
        self.generate()
        self.generate_commands(topology_template_sig_name, topology_template_yaml)
        self.generate()

    def generate_template_field(
            self, template_name, template_yaml, type_keyword, field_prefix, context_message
    ):
        self.generate("  // YAML ", template_name, ": ", template_yaml, sep="")
        template_yaml_type = template_yaml.get(type_keyword)
        if template_yaml_type is None:
            self.error(
                TOPOLOGY_TEMPLATE
                + ":"
                + context_message
                + ":"
                + template_name
                + ": "
                + type_keyword
                + " keyword missed",
                type_keyword
            )
            self.generate("  // ERROR: '", type_keyword, "' keyword missed!", sep="")
            return
        if self.type_system.get_type(template_yaml_type) is None:
            self.error(
                TOPOLOGY_TEMPLATE
                + ":"
                + context_message
                + ":"
                + template_name
                + ":"
                + type_keyword
                + ": "
                + template_yaml_type
                + " undefined",
                template_yaml_type
            )
            self.generate(
                "  // ERROR: ",
                type_keyword,
                " ",
                template_yaml_type,
                " undefined",
                sep="",
            )
            return
        self.generate("  // YAML ", type_keyword, ": ", template_yaml_type, sep="")
        self.generate_sig_field(
            field_prefix, template_name, Alloy.ONE, self.alloy_sig(template_yaml_type)
        )
        self.generate()

    def generate_template_fields(self, keyword, topology_template, field_prefix):
        self.generate_header("YAML " + keyword + ":", "  ")
        templates = topology_template.get(keyword)
        if templates is None:
            templates = {}
        elif isinstance(templates, list):
            templates = utils.normalize_dict(templates)
        for (template_name, template_yaml) in templates.items():
            self.generate_template_field(
                template_name, template_yaml, TYPE, field_prefix, keyword
            )

    def generate_fields(self, sig_name, topology_template_yaml):
        self.generate_template_fields(NODE_TEMPLATES, topology_template_yaml, None)

        self.generate_template_fields(
            RELATIONSHIP_TEMPLATES, topology_template_yaml, "relationship"
        )

        self.generate_template_fields(GROUPS, topology_template_yaml, "group")

        self.generate_template_fields(POLICIES, topology_template_yaml, "policy")

        # Generate outputs
        self.generate_header("YAML " + OUTPUTS + ":", "  ")
        outputs = get_dict(topology_template_yaml, OUTPUTS)
        for (output_name, output_yaml) in outputs.items():
            self.generate_sig_field("output", output_name, Alloy.ONE, TOSCA.Parameter)
            self.generate()

        # Generate substitution_mappings
        substitution_mappings = topology_template_yaml.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            self.generate_header("YAML " + SUBSTITUTION_MAPPINGS + ":", "  ")
            self.generate_template_field(
                SUBSTITUTION_MAPPINGS, substitution_mappings, NODE_TYPE, None, ""
            )

        # TODO: generate workflows

    def generate_interfaces_facts(
            self,
            template_name,
            template_yaml,
            prefixed_template_name,
            merged_template_type,
            context_error_message,
    ):
        self.generate("  // YAML ", INTERFACES, ":", sep="")
        interfaces = get_dict(merged_template_type, INTERFACES)
        self.generate_cardinality_fact(
            prefixed_template_name + "." + INTERFACES, len(interfaces)
        )
        for (interface_name, interface_yaml) in interfaces.items():
            self.generate("  // YAML ", interface_name, ":", sep="")
            nb_operations = 0
            for (operation_name, operation_yaml) in (
                    syntax.get_operations(interface_yaml).get(OPERATIONS).items()
            ):
                self.generate(
                    "  // YAML ", operation_name, ": ", operation_yaml, sep=""
                )
                nb_operations = nb_operations + 1
                if operation_yaml:
                    prefixed_operation = (
                            prefixed_template_name
                            + "."
                            + self.prefix_name("interface", interface_name)
                            + "."
                            + self.prefix_name("operation", operation_name)
                    )
                    implementation = self.get_operation_implementation(operation_yaml)
                    if implementation:

                        def generate_implementation_fact(implementation):
                            if get_dict(template_yaml, ARTIFACTS).get(
                                    implementation
                            ) or merged_template_type.get(ARTIFACTS, {}).get(
                                implementation
                            ):
                                self.generate(
                                    "  ",
                                    prefixed_operation,
                                    ".implementation = ",
                                    utils.normalize_name(template_name),
                                    '.artifact["',
                                    implementation,
                                    '"]',
                                    sep="",
                                )
                            else:
                                artifact_type_sig = self.alloy_sig(
                                    self.get_implementation_artifact_type(
                                        implementation
                                    )
                                )
                                self.generate(
                                    "  ",
                                    prefixed_operation,
                                    ".implementation[",
                                    artifact_type_sig,
                                    ', "',
                                    implementation,
                                    '"]',
                                    sep="",
                                )

                        if isinstance(implementation, str):
                            # Short notation
                            generate_implementation_fact(implementation)
                        else:
                            # Extended notation
                            # some keynames are not supported currently!
                            for unsupported_key in [
                                "dependencies",
                                "timeout",
                                "operation_host",
                            ]:
                                if implementation.get(unsupported_key) is not None:
                                    self.warning(
                                        " implementation "
                                        + str(implementation)
                                        + " - "
                                        + unsupported_key
                                        + " unsupported by Alloy generator",
                                        implementation
                                    )
                            # only primary is supported currently!
                            primary = implementation.get("primary")
                            if primary is None:
                                self.error(
                                    " implementation "
                                    + str(implementation)
                                    + " - primary artifact missed",
                                    implementation
                                )
                                continue
                            # generate the Alloy fact
                            if isinstance(primary, str):
                                # Short notation
                                generate_implementation_fact(primary)
                            else:
                                # Extended notation
                                artifact_type_sig = self.alloy_sig(primary.get("type"))
                                artifact_file = primary.get("file")
                                self.generate(
                                    "  ",
                                    prefixed_operation,
                                    ".implementation[",
                                    artifact_type_sig,
                                    ', "',
                                    artifact_file,
                                    '"]',
                                    sep="",
                                )
                    else:
                        self.generate(
                            "  no ", prefixed_operation, ".implementation", sep=""
                        )
                    mnt = self.type_system.merge_node_type(template_yaml.get(TYPE))
                    inputs = utils.get_path(
                        mnt,
                        INTERFACES,
                        interface_name,
                        operation_name,
                        INPUTS,
                        default={},
                    )
                    template_operation = utils.get_path(
                        template_yaml,
                        INTERFACES,
                        interface_name,
                        operation_name,
                        default={},
                    )
                    if isinstance(template_operation, dict):
                        inputs_values = get_dict(template_operation, INPUTS)
                    else:
                        inputs_values = {}

                    # Add type if not defined.
                    for input_name, input_yaml in inputs_values.items():
                        input_declaration = inputs.get(input_name)
                        if input_declaration is None:
                            self.generate(
                                "  ",
                                prefixed_operation,
                                '.input["',
                                input_name,
                                '"].undefined[]',
                                sep="",
                            )
                            input_declaration = {}
                        if not input_declaration.get(TYPE):
                            input_declaration[TYPE] = "string"
                        inputs[input_name] = input_declaration

                    self.generate_all_properties(
                        inputs,
                        inputs_values,
                        prefixed_operation,
                        context_error_message
                        + ":"
                        + INTERFACES
                        + ":"
                        + interface_name
                        + ":"
                        + operation_name
                        + ":"
                        + INPUTS,
                        property_name_format='input["%s"].value',
                    )

                if isinstance(operation_yaml, dict):
                    nb_inputs = len(get_dict(operation_yaml, INPUTS))
                else:
                    nb_inputs = 0
                self.generate_cardinality_fact(
                    prefixed_operation + "." + INPUTS, nb_inputs
                )
            self.generate_cardinality_fact(
                prefixed_template_name
                + "."
                + self.prefix_name("interface", interface_name)
                + ".operations",
                nb_operations,
            )

    def generate_templates_facts(
            self,
            topology_template,
            keyword,
            relation_name,
            predicate_name,
            field_prefix,
            more_generation,
    ):
        # Translate templates.
        self.generate_header("YAML " + keyword + ":", "  ")
        templates = get_dict(topology_template, keyword)
        self.generate_cardinality_fact(relation_name, len(templates))
        for (template_name, template_yaml) in templates.items():
            # Set the SELF reserved function keyword to the current node template name.
            self.SELF = template_name

            prefixed_template_name = self.prefix_name(field_prefix, template_name)
            merged_template_type = self.merge_node_template_definition(template_yaml)

            # Generate template declaration
            self.generate("  // YAML ", template_name, ": ", template_yaml, sep="")
            self.generate_call_predicate(predicate_name, prefixed_template_name)
            self.generate(
                "  ", prefixed_template_name, '.name["' + template_name + '"]', sep=""
            )
            if predicate_name == "node":
                self.generate(
                    "  ",
                    prefixed_template_name,
                    '.node_type_name = "'
                    + self.type_system.get_type_uri(syntax.get_type(template_yaml))
                    + '"',
                    sep="",
                )

            # Generate node template properties
            self.generate("  // YAML ", PROPERTIES, ":", sep="")
            self.generate_all_properties(
                get_dict(merged_template_type, PROPERTIES),
                get_dict(template_yaml, PROPERTIES),
                prefixed_template_name,
                TOPOLOGY_TEMPLATE
                + ":"
                + keyword
                + ":"
                + template_name
                + ":"
                + PROPERTIES,
            )

            # Constraints the cardinality of interfaces, operations and inputs
            # and set operation implementations
            # and set operation inputs
            self.generate_interfaces_facts(
                template_name,
                template_yaml,
                prefixed_template_name,
                merged_template_type,
                TOPOLOGY_TEMPLATE + ":" + keyword + ":" + template_name,
            )

            if more_generation:
                more_generation(
                    self,
                    template_name,
                    template_yaml,
                    merged_template_type,
                    prefixed_template_name,
                    TOPOLOGY_TEMPLATE + ":" + keyword + ":" + template_name,
                )
            self.generate()

    def generate_facts(self, name, topology_template_yaml):

        # Translate description.
        description = topology_template_yaml.get(DESCRIPTION)
        self.generate("  // YAML description:", description)
        if description:
            self.generate('  description = "', description, '"', sep="")
        else:
            self.generate("  no description")
        self.generate()

        # Translate inputs.
        self.generate_header("YAML " + INPUTS + ":", "  ")
        inputs = get_dict(topology_template_yaml, INPUTS)
        self.generate_cardinality_fact(INPUTS, len(inputs))
        self.generate_inputs_facts("", topology_template_yaml, TOPOLOGY_TEMPLATE)
        self.generate()

        # Translate node templates.

        def generate_artifacts_capabilities_requirements(
                self,
                node_template_name,
                node_template_yaml,
                merged_node_template_type,
                prefixed_node_template_name,
                context_error_message,
        ):

            # Generate template artifacts
            self.generate("  // YAML ", ARTIFACTS, ":", sep="")
            artifacts = utils.merge_dict(
                get_dict(merged_node_template_type, ARTIFACTS),
                get_dict(node_template_yaml, ARTIFACTS),
            )
            self.generate_cardinality_fact(
                prefixed_node_template_name + "." + ARTIFACTS, len(artifacts)
            )
            for artifact_name, artifact_yaml in artifacts.items():
                self.generate(
                    "  // YAML   ", artifact_name, ": ", artifact_yaml, sep=""
                )
                if artifact_yaml is None:
                    artifact_yaml = {}
                artifact_type = syntax.get_artifact_type(artifact_yaml)
                if artifact_type is None:
                    self.warning(
                        context_error_message
                        + ":"
                        + ARTIFACTS
                        + ":"
                        + artifact_name
                        + " must have a type",
                        artifact_name
                    )
                    artifact_type = TOSCA.Artifact
                prefixed_artifact_name = self.prefix_name("artifact", artifact_name)
                self.generate(
                    "  one",
                    prefixed_artifact_name,
                    ":",
                    self.alloy_sig(artifact_type),
                    "{",
                )
                self.generate(
                    "    ",
                    prefixed_node_template_name,
                    ".artifact[",
                    prefixed_artifact_name,
                    "]",
                    sep="",
                )
                self.generate(
                    "    ",
                    prefixed_artifact_name,
                    '.name["',
                    artifact_name,
                    '"]',
                    sep="",
                )
                file = syntax.get_artifact_file(artifact_yaml)
                if file:
                    self.generate(
                        "    ", prefixed_artifact_name, '.file["', file, '"]', sep=""
                    )
                else:
                    self.generate("    no ", prefixed_artifact_name, ".file", sep="")
                # generate artifact properties
                merged_artifact_type = self.type_system.merge_type(artifact_type)
                self.generate_all_properties(
                    get_dict(merged_artifact_type, PROPERTIES),
                    get_dict(artifact_yaml, PROPERTIES),
                    prefixed_artifact_name,
                    context_error_message + ":" + ARTIFACTS + ":" + artifact_name,
                    property_name_format="%s",
                )

                self.generate("  }")

            # Generate node template capabilities

            # Get all capabilities of the node template type.
            all_capabilities = get_dict(merged_node_template_type, CAPABILITIES)

            # Get all capabilities of the node template.
            capabilities = get_dict(node_template_yaml, CAPABILITIES)

            # Check if each capability of the node template is defined in the node template type.
            for capability_name, capability_yaml in capabilities.items():
                if not all_capabilities.get(capability_name):
                    self.error(
                        context_error_message
                        + ":"
                        + CAPABILITIES
                        + ":"
                        + capability_name
                        + ": undefined capability",
                        capability_yaml,
                    )

            self.generate("  // YAML ", CAPABILITIES, ":", sep="")
            for capability_name, capability_yaml in all_capabilities.items():
                capability_value = capabilities.get(capability_name)
                self.generate(
                    "  // YAML   ", capability_name, ": ", capability_value, sep=""
                )
                if capability_yaml:
                    prefixed_capability_name = (
                            prefixed_node_template_name
                            + "."
                            + self.prefix_name("capability", capability_name)
                    )
                    if capability_value is None:
                        capability_value = {}
                    merged_capability_type = self.type_system.merge_type(
                        get_capability_type(capability_yaml)
                    )
                    self.generate_all_properties(
                        get_dict(merged_capability_type, PROPERTIES),
                        get_dict(capability_value, PROPERTIES),
                        prefixed_capability_name,
                        context_error_message
                        + ":"
                        + CAPABILITIES
                        + ":"
                        + capability_name,
                        property_name_format="property_%s",
                    )

            # Generate node template requirements

            # Get all requirements of the node template type.
            all_requirements = get_dict(merged_node_template_type, REQUIREMENTS)

            # Get all requirements of the node template.
            requirements = node_template_yaml.get(REQUIREMENTS, [])
            if requirements is None:
                requirements = []

            # Check if each requirement of the node template is defined in the node template type.
            for requirement in requirements:
                for requirement_name, requirement_yaml in requirement.items():
                    # ACK for Alien4Cloud
                    requirement_name = syntax.get_type_requirement(
                        requirement_yaml, requirement_name
                    )
                    if not all_requirements.get(requirement_name):
                        self.error(
                            context_error_message
                            + ":"
                            + requirement_name
                            + " - requirement undefined",
                            requirement_yaml,
                        )

            # TODO: manage requirements defined in the node type but not filled in the node template.

            node_templates = get_dict(topology_template_yaml, NODE_TEMPLATES)
            relationship_templates = get_dict(
                topology_template_yaml, RELATIONSHIP_TEMPLATES
            )

            for requirement in requirements:
                for (requirement_name, requirement_yaml) in requirement.items():
                    # ACK for Alien4Cloud
                    requirement_name = syntax.get_type_requirement(
                        requirement_yaml, requirement_name
                    )
                    self.generate(
                        "  // YAML ", requirement_name, ": ", requirement_yaml, sep=""
                    )
                    if requirement_yaml is None:
                        self.generate("  // No connection")
                        continue
                    requirement_node = get_requirement_node_template(requirement_yaml)
                    requirement_node_filter = get_requirement_node_filter(
                        requirement_yaml
                    )
                    if requirement_node is None and requirement_node_filter is None:
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + " - node or node_filter expected",
                            requirement_yaml,
                        )
                        continue
                    if (
                            requirement_node is not None
                            and requirement_node_filter is not None
                    ):
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + " - both node and node_filter excluded",
                            requirement_yaml,
                        )
                        continue
                    if requirement_node_filter is not None:
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + ":node_filter unsupported by Alloy generator",
                            requirement_yaml
                        )
                        continue

                    requirement_node_yaml = node_templates.get(requirement_node)
                    if requirement_node_yaml is None:
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + ":node: "
                            + requirement_node
                            + " - undefined node template",
                            requirement_node_yaml,
                        )
                        continue
                    requirement_node_type_name = requirement_node_yaml.get(TYPE)
                    if requirement_node_type_name is None:
                        continue
                    merged_requirement_node_type = self.type_system.merge_node_type(
                        requirement_node_type_name
                    )
                    if merged_requirement_node_type is None:
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + ": node type '"
                            + node_templates.get(requirement_node).get(TYPE)
                            + "' unknown",
                            requirement_node_yaml,
                        )
                        continue
                    requirement = all_requirements.get(requirement_name)
                    requirement_capability = syntax.get_requirement_capability(
                        requirement
                    )
                    capability_found = False
                    for (capability_name, capability_yaml) in get_dict(
                            merged_requirement_node_type, CAPABILITIES
                    ).items():
                        if self.type_system.is_derived_from(
                                get_capability_type(capability_yaml), requirement_capability
                        ):
                            capability_found = True
                            break
                    if capability_found:
                        prefixed_requirement_name = self.prefix_name(
                            "requirement", requirement_name
                        )
                        prefixed_capability_name = self.prefix_name(
                            "capability", capability_name
                        )
                        self.generate(
                            "  connect[",
                            prefixed_node_template_name,
                            ".",
                            prefixed_requirement_name,
                            ", ",
                            utils.normalize_name(requirement_node),
                            ".",
                            prefixed_capability_name,
                            "]",
                            sep="",
                        )
                    else:
                        if requirement_node_type_name is None:
                            requirement_node_type_name = "unknown node type"
                        if requirement_capability is None:
                            requirement_capability = "unknown"
                        self.error(
                            context_error_message
                            + ":"
                            + REQUIREMENTS
                            + ":"
                            + requirement_name
                            + ": capability of type "
                            + requirement_capability
                            + " not found in "
                            + requirement_node_type_name,
                            requirement_node_yaml,
                        )
                        prefixed_requirement_name = "unknown"

                    requirement_relationship_properties = {}
                    merged_requirement_relationship_type = {}
                    requirement_relationship = syntax.get_requirement_relationship(
                        requirement
                    )
                    requirement_relationship_type = syntax.get_relationship_type(
                        requirement_relationship
                    )
                    if requirement_relationship_type is not None:
                        merged_requirement_relationship_type = (
                            self.type_system.merge_node_type(
                                requirement_relationship_type
                            )
                        )
                    prefixed_relationship = (
                            prefixed_node_template_name
                            + "."
                            + prefixed_requirement_name
                            + ".relationship"
                    )

                    if isinstance(requirement_yaml, dict):
                        requirement_relationship = syntax.get_requirement_relationship(
                            requirement_yaml
                        )
                        if isinstance(requirement_relationship, dict):
                            tmp = syntax.get_type(requirement_relationship)
                            if tmp is not None:
                                requirement_relationship_type = tmp
                                merged_requirement_relationship_type = (
                                    self.type_system.merge_node_type(
                                        requirement_relationship_type
                                    )
                                )
                                requirement_relationship_properties = get_dict(
                                    requirement_relationship, PROPERTIES
                                )
                                self.generate(
                                    "  ",
                                    prefixed_relationship,
                                    "[",
                                    self.alloy_sig(requirement_relationship_type),
                                    "]",
                                    sep="",
                                )
                        elif isinstance(requirement_relationship, str):
                            if relationship_templates.get(requirement_relationship):
                                self.generate(
                                    "  ",
                                    prefixed_relationship,
                                    "[",
                                    self.prefix_name(
                                        RELATIONSHIP, requirement_relationship
                                    ),
                                    "]",
                                    sep="",
                                )
                                continue
                            requirement_relationship_type = requirement_relationship
                            merged_requirement_relationship_type = (
                                self.type_system.merge_node_type(
                                    requirement_relationship_type
                                )
                            )
                            requirement_relationship_properties = {}
                            self.generate(
                                "  ",
                                prefixed_relationship,
                                "[",
                                utils.normalize_name(requirement_relationship_type),
                                "]",
                                sep="",
                            )
                    self.generate(
                        "  ", prefixed_relationship, '._name_ = "(anonymous)"', sep=""
                    )
                    # Generate relationship properties.
                    self.generate_all_properties(
                        get_dict(merged_requirement_relationship_type, PROPERTIES),
                        requirement_relationship_properties,
                        prefixed_relationship,
                        context_error_message
                        + ":"
                        + REQUIREMENTS
                        + ":"
                        + requirement_name,
                        property_name_format="property_%s",
                    )

                    self.generate_interfaces_facts(
                        node_template_name,
                        {TYPE: requirement_relationship_type},
                        prefixed_relationship,
                        merged_requirement_relationship_type,
                        context_error_message
                        + ":"
                        + REQUIREMENTS
                        + ":"
                        + requirement_name,
                    )

        self.generate_templates_facts(
            topology_template_yaml,
            NODE_TEMPLATES,
            "nodes",
            "node",
            None,
            generate_artifacts_capabilities_requirements,
        )

        self.generate()

        # Generate facts for relationships
        self.generate_templates_facts(
            topology_template_yaml,
            RELATIONSHIP_TEMPLATES,
            "relationships",
            "relationship",
            "relationship",
            None,
        )

        self.generate()

        # Generate facts for groups

        def generate_members(
                self,
                group_name,
                group_yaml,
                merged_group_type,
                prefixed_group_name,
                context_message,
        ):
            # Generate members.
            members = group_yaml.get(MEMBERS)
            self.generate("  // YAML ", MEMBERS, ": ", members, sep="")
            if members:
                tmp = ""
                for member in members:
                    if tmp != "":
                        tmp = tmp + " + "
                    tmp = tmp + utils.normalize_name(member)
                self.generate_call_predicate(prefixed_group_name + "." + MEMBERS, tmp)
            else:
                self.generate("  no ", prefixed_group_name, "." + MEMBERS, sep="")

        self.generate_templates_facts(
            topology_template_yaml, GROUPS, "groups", "group", "group", generate_members
        )

        self.generate()

        # Generate facts for policies

        def generate_targets(
                self,
                policy_name,
                policy_yaml,
                merged_policy_type,
                prefixed_policy_name,
                context_message,
        ):
            all_node_templates = get_dict(topology_template_yaml, NODE_TEMPLATES)
            all_groups = get_dict(topology_template_yaml, GROUPS)
            # Generate targets.
            targets = policy_yaml.get(TARGETS)
            self.generate("  // YAML ", TARGETS, ": ", targets, sep="")
            if targets:
                tmp = ""
                idx = 0
                for target in targets:
                    if all_node_templates.get(target):
                        prefix_target = None
                    elif all_groups.get(target):
                        prefix_target = "group"
                    else:
                        self.error(
                            context_message
                            + ":targets["
                            + str(idx)
                            + "] - "
                            + target
                            + " node template or group undefined",
                            target,
                        )
                        idx = idx + 1
                        continue
                    if tmp != "":
                        tmp = tmp + " + "
                    tmp = tmp + self.prefix_name(prefix_target, target)
                    idx = idx + 1
                self.generate_call_predicate(prefixed_policy_name + "." + TARGETS, tmp)
            else:
                self.generate("  no ", prefixed_policy_name, "." + TARGETS, sep="")

        self.generate_templates_facts(
            topology_template_yaml,
            POLICIES,
            "policies",
            "policy",
            "policy",
            generate_targets,
        )

        # Translate outputs.
        self.generate_header("YAML outputs:", "  ")
        outputs = get_dict(topology_template_yaml, OUTPUTS)
        self.generate_cardinality_fact(OUTPUTS, len(outputs))
        for (output_name, output_yaml) in outputs.items():
            self.generate("  // YAML   ", output_name, ":", sep="")
            self.generate("  output[output_", output_name, "]", sep="")
            self.generate(
                "  output_", output_name, '.name["', output_name, '"]', sep=""
            )
            self.generate_parameter_facts(
                "  ",
                "output_",
                output_name,
                output_yaml,
                TOPOLOGY_TEMPLATE + ":" + ":" + OUTPUTS + ":" + output_name,
            )
            self.generate()

        # Translate substitution_mappings.
        self.generate()
        self.generate_header("Substitution Mappings", "  ")
        substitution_mappings = topology_template_yaml.get(SUBSTITUTION_MAPPINGS)
        self.generate("  // YAML substitution_mappings:", substitution_mappings)
        if substitution_mappings is None:
            self.generate("  no substitution_mapping")
        else:
            substitution_mappings_node_type = syntax.get_node_type(
                substitution_mappings
            )
            self.generate("  substitution_mappings[substitution_mappings]")
            self.generate(
                '  substitution_mappings.node_type_name = "'
                + self.type_system.get_type_uri(substitution_mappings_node_type)
                + '"',
                sep="",
            )

            # Translate properties.
            self.generate_all_properties(
                get_dict(
                    self.type_system.merge_type(substitution_mappings_node_type),
                    PROPERTIES,
                ),
                get_dict(substitution_mappings, PROPERTIES),
                SUBSTITUTION_MAPPINGS,
                TOPOLOGY_TEMPLATE + ":" + SUBSTITUTION_MAPPINGS + ":" + PROPERTIES,
                generate_no_value=False,
            )

            # Translate capabilities.
            capabilities = substitution_mappings.get(CAPABILITIES)
            if capabilities:
                self.generate("  // YAML   capabilities:")
                for capability_name, capability_yaml in capabilities.items():
                    if not isinstance(capability_yaml, list):
                        self.error(
                            "???:capabilities:"
                            + capability_name
                            + ": "
                            + str(capability_yaml)
                            + " unsupported by Alloy generator",
                            capability_yaml
                        )
                        continue
                    self.generate(
                        "  // YAML     ", capability_name, ": ", capability_yaml, sep=""
                    )
                    self.generate(
                        "  connectCapability[",
                        "substitution_mappings.",
                        self.prefix_name("capability", capability_name),
                        ", ",
                        utils.normalize_name(capability_yaml[0]),
                        ".",
                        self.prefix_name("capability", capability_yaml[1]),
                        "]",
                        sep="",
                    )

            # Generate requirements.
            requirements = syntax.get_substitution_mappings_requirements(
                substitution_mappings
            )
            if len(requirements) > 0:
                self.generate("  // YAML   requirements:")
                for requirement_name, requirement_yaml in requirements.items():
                    self.generate(
                        "  // YAML     ",
                        requirement_name,
                        ": ",
                        requirement_yaml,
                        sep="",
                    )
                    if requirement_yaml:
                        self.generate(
                            "  connectRequirement[",
                            "substitution_mappings.",
                            self.prefix_name("requirement", requirement_name),
                            ", ",
                            utils.normalize_name(requirement_yaml[0]),
                            ".",
                            self.prefix_name("requirement", requirement_yaml[1]),
                            "]",
                            sep="",
                        )

        # TODO: are other facts to generate?
        return

    def merge_node_template_definition(self, node_template_yaml):
        result = self.type_system.merge_node_type(node_template_yaml.get(TYPE))
        node_template_interfaces = node_template_yaml.get(INTERFACES)
        if node_template_interfaces:
            interfaces = result.get(INTERFACES)
            if interfaces:
                result[INTERFACES] = utils.merge_dict(
                    interfaces, node_template_interfaces
                )
            else:
                result[INTERFACES] = copy.deepcopy(node_template_interfaces)
        return result

    def compute_scope_property(self, acs, property_declaration, property_value):
        property_type = syntax.get_property_type(property_declaration)

        if property_type == "integer":
            if isinstance(property_value, int):
                MAX_INT = self.get_max_int()
                if property_value >= MAX_INT:
                    property_value = MAX_INT
                acs.update_Int_scope(property_value)

        elif self.type_system.is_yaml_type(property_type) or property_type == "range":
            NOTHING_TO_DO = True

        elif property_type.startswith("scalar-unit."):
            acs.update_sig_scope("TOSCA/" + utils.normalize_name(property_type))

        elif property_type == "list":
            if property_value:
                acs.update_seq_scope(property_value)
                for elem in property_value:
                    self.compute_scope_property(
                        acs, property_declaration.get(ENTRY_SCHEMA), elem
                    )

        elif property_type == "map":
            if property_value and len(property_value):
                acs.update_sig_scope(self.get_map_signature(property_declaration))
                entry_schema = property_declaration.get(ENTRY_SCHEMA)
                if entry_schema is None:
                    return
                if not isinstance(property_value, dict):
                    return
                for key, value in property_value.items():
                    self.compute_scope_property(acs, entry_schema, value)
            else:
                if is_property_required(property_declaration):
                    acs.update_sig_scope(self.get_map_signature(property_declaration))

        else:
            type_type = self.type_system.merge_type(property_type)
            derived_from = syntax.get_derived_from(type_type)
            if not self.type_system.is_yaml_type(derived_from):
                alloy_sig = self.alloy_sig(property_type)
                acs.update_sig_scope(alloy_sig)
                if type_type and isinstance(property_value, dict):
                    self.compute_scope_properties(
                        acs, get_dict(type_type, PROPERTIES), property_value
                    )

    def compute_scope_properties(
            self, acs, all_declared_properties, template_properties
    ):
        if template_properties is None:
            template_properties = {}

        for (property_name, property_declaration) in all_declared_properties.items():
            property_value = template_properties.get(property_name)
            if property_value is not None:
                self.compute_scope_property(acs, property_declaration, property_value)
            else:
                property_default = syntax.get_property_default(property_declaration)
                if is_property_required(property_declaration):
                    self.compute_scope_property(
                        acs, property_declaration, property_default
                    )
                else:
                    if property_default:
                        self.compute_scope_property(
                            acs, property_declaration, property_default
                        )

    def compute_scope_interfaces(
            self, acs, node_type, node_template_type, node_template
    ):

        if acs.get_signature_scopes().get(self.alloy_sig(node_type)) == 1:
            # This is the first time that this node type is processed.
            interfaces = get_dict(node_template_type, INTERFACES)
        else:
            # This node type was already processed.
            interfaces = get_dict(node_template, INTERFACES)

        # Iterate over all node template interfaces.
        for (interface_name, interface_yaml) in interfaces.items():

            # TODO: add check interface declared

            interface_type = (
                get_dict(node_template_type, INTERFACES).get(interface_name).get(TYPE)
            )
            if interface_type is None:
                interface_sig = TOSCA.Interface
            else:
                interface_sig = self.alloy_sig(interface_type)

            if acs.get_signature_scopes().get(interface_sig, 0) > 0:
                # This interface type was already processed.
                is_new_interface = False
            #                interface_yaml = node_template.get(INTERFACES, {})
            else:
                is_new_interface = True

            interfaces_yaml = get_dict(node_template_type, INTERFACES).get(
                interface_name
            )

            # Iterate over all operations.
            for (operation_name, operation_yaml) in (
                    syntax.get_operations(interface_yaml).get(OPERATIONS).items()
            ):
                # Compute the scope required by each operation.
                is_new_operation = is_new_interface

                implementation = self.get_operation_implementation(operation_yaml)
                if implementation:
                    acs.update_sig_scope(interface_sig)
                    acs.update_sig_scope(TOSCA.Operation)
                    is_new_operation = True

                    def update_sig_scope_implementation_short_notation(implementation):
                        if (
                                get_dict(node_template, ARTIFACTS).get(implementation)
                                is None
                                and get_dict(node_template_type, ARTIFACTS).get(
                            implementation
                        )
                                is None
                        ):
                            artifact_type_sig = self.alloy_sig(
                                self.get_implementation_artifact_type(implementation)
                            )
                            acs.update_sig_scope(artifact_type_sig)

                    if isinstance(implementation, str):
                        # Short notation
                        update_sig_scope_implementation_short_notation(implementation)
                    else:
                        # Extended notation
                        primary = implementation.get("primary")
                        if primary is None:
                            continue
                        if isinstance(primary, str):
                            # Short notation
                            update_sig_scope_implementation_short_notation(primary)
                        else:
                            # Extended notation
                            artifact_type_sig = self.alloy_sig(primary.get("type"))
                            acs.update_sig_scope(artifact_type_sig)
                # Iterate over all inputs.
                for input_name, input_yaml in get_dict(operation_yaml, INPUTS).items():
                    # Compute the scope required by each operation.
                    acs.update_sig_scope(TOSCA.Parameter)
                    is_new_operation = True
                    # Compute the scope of the input value.
                    self.compute_scope_property(
                        acs,
                        input_yaml,
                        node_template.get(INTERFACES, {})
                            .get(operation_name, {})
                            .get(input_name),
                    )

                if is_new_operation:
                    acs.update_sig_scope(TOSCA.Operation)
                    is_new_interface = True

            if is_new_interface:
                # Compute the scope required by each interface.
                acs.update_sig_scope(interface_sig)

    def compute_scope_templates(
            self, acs, topology_template, keyword, more_computation
    ):
        # Iterate over all templates.
        for template_name, template_yaml in get_dict(
                topology_template, keyword
        ).items():
            # Compute the scope required by each template.
            template_type = syntax.get_type(template_yaml)
            acs.update_sig_scope(self.alloy_sig(template_type))
            acs.update_sig_scope(LocationGraphs.Name)

            # Merge the template type with its derived_from parents.
            merged_template_type = self.merge_node_template_definition(template_yaml)

            # Iterate over all properties.
            self.compute_scope_properties(
                acs,
                get_dict(merged_template_type, PROPERTIES),
                get_dict(template_yaml, PROPERTIES),
            )

            # Iterate over all attributes.
            for attribute_name, attribute_yaml in get_dict(
                    merged_template_type, ATTRIBUTES
            ).items():
                # Compute the scope required by the attribute value.
                self.compute_scope_property(acs, attribute_yaml, None)

            # Iterate over all template artifacts.
            artifacts = utils.merge_dict(
                get_dict(merged_template_type, ARTIFACTS),
                get_dict(template_yaml, ARTIFACTS),
            )
            for artifact_name, artifact_yaml in artifacts.items():
                # Compute the scope required by each artifact.
                artifact_type = syntax.get_artifact_type(artifact_yaml)
                if artifact_type is None:
                    artifact_type = TOSCA.Artifact
                acs.update_sig_scope(self.alloy_sig(artifact_type))
                # compute the scope required by artifact properties.
                if not isinstance(artifact_yaml, dict):
                    continue
                merged_artifact_type = self.type_system.merge_type(
                    artifact_yaml.get(TYPE)
                )
                self.compute_scope_properties(
                    acs,
                    get_dict(merged_artifact_type, PROPERTIES),
                    get_dict(artifact_yaml, PROPERTIES),
                )

            # Compute the scope for node template interfaces.
            self.compute_scope_interfaces(
                acs, template_type, merged_template_type, template_yaml
            )

            if more_computation:
                more_computation(
                    self,
                    acs,
                    template_name,
                    template_yaml,
                    merged_template_type,
                    TOPOLOGY_TEMPLATE + ":" + keyword + ":" + template_name,
                )

    def compute_scope_topology_template(
            self, acs, topology_template_name, topology_template_yaml
    ):
        # Required in order to compute the scope required by this topology template.
        Alloy.declare_signature(topology_template_name, TOSCA.TopologyTemplate)

        # Compute the scope for the topology template signature.
        acs.update_sig_scope(topology_template_name)

        # Iterate over all inputs.
        inputs = get_dict(topology_template_yaml, INPUTS)
        for input_name, input_yaml in inputs.items():
            # one TOSCA Input is required.
            acs.update_sig_scope(TOSCA.Parameter)
            # Compute the scope required by each input value.
            if input_yaml.get(TYPE) is None:
                input_yaml[TYPE] = "string"
            self.compute_scope_property(acs, input_yaml, {})

        # Iterate over all node templates.

        def compute_scope_capabilities_requirements(
                self,
                acs,
                node_template_name,
                node_template_yaml,
                merged_node_template_type,
                context_message,
        ):
            all_relationship_templates = get_dict(
                topology_template_yaml, RELATIONSHIP_TEMPLATES
            )

            # Iterate over all node template capabilities.
            for capability_name, capability_yaml in get_dict(
                    merged_node_template_type, CAPABILITIES
            ).items():
                # Compute the scope required by each capability.
                capability_type = get_capability_type(capability_yaml)
                # Add to the scope the lower occurrences of this capability.
                capability_lower_occurrences = get_capability_occurrences(
                    capability_yaml
                )[0]
                if capability_lower_occurrences:
                    acs.update_sig_scope(
                        self.alloy_sig(capability_type), capability_lower_occurrences
                    )

                merged_capability_type = self.type_system.merge_type(capability_type)

                # Iterate over all capability properties.
                capabilities = get_dict(node_template_yaml, CAPABILITIES)
                node_template_capability_yaml = get_dict(capabilities, capability_name)
                self.compute_scope_properties(
                    acs,
                    get_dict(merged_capability_type, PROPERTIES),
                    get_dict(node_template_capability_yaml, PROPERTIES),
                )

                # Iterate over all capability attributes.
                for attribute_name, attribute_yaml in get_dict(
                        merged_capability_type, ATTRIBUTES
                ).items():
                    # Compute the scope required by the attribute value.
                    self.compute_scope_property(acs, attribute_yaml, None)

            node_template_requirements = node_template_yaml.get(REQUIREMENTS, [])
            if node_template_requirements is None:  # TODO: Factorize this code pattern.
                node_template_requirements = []
            # Iterate over all node template requirements.
            for (requirement_name, requirement_yaml) in get_dict(
                    merged_node_template_type, REQUIREMENTS
            ).items():
                requirement_capability = syntax.get_requirement_capability(
                    requirement_yaml
                )
                if requirement_capability is None:
                    self.error(
                        context_message
                        + ":"
                        + REQUIREMENTS
                        + ":"
                        + requirement_name
                        + ": capability type undefined",
                        requirement_yaml,
                    )
                    continue
                requirement_capability_sig = self.alloy_sig(requirement_capability)
                requirement_relationship = syntax.get_requirement_relationship(
                    requirement_yaml
                )
                requirement_relationship_type = syntax.get_relationship_type(
                    requirement_relationship
                )
                if requirement_relationship_type is None:
                    self.error(
                        context_message
                        + ":"
                        + REQUIREMENTS
                        + ":"
                        + requirement_name
                        + ": relationship type undefined",
                        requirement_yaml,
                    )
                    continue
                requirement_relationship_type_sig = self.alloy_sig(
                    requirement_relationship_type
                )
                merged_requirement_relationship_type = self.type_system.merge_node_type(
                    requirement_relationship_type
                )

                nb_requirements = 0
                for node_template_requirement in node_template_requirements:
                    for (
                            node_template_requirement_name,
                            node_template_requirement_yaml,
                    ) in node_template_requirement.items():
                        # TODO : take occurrences into account
                        if node_template_requirement_name == requirement_name:
                            if node_template_requirement_yaml:
                                requirement_relationship_properties = {}
                                if isinstance(node_template_requirement_yaml, dict):
                                    requirement_relationship = (
                                        syntax.get_requirement_relationship(
                                            node_template_requirement_yaml
                                        )
                                    )
                                    if isinstance(requirement_relationship, dict):
                                        relationship_type = (
                                            requirement_relationship.get(TYPE)
                                        )
                                        requirement_relationship_properties = get_dict(
                                            requirement_relationship, PROPERTIES
                                        )
                                    elif isinstance(requirement_relationship, str):
                                        if all_relationship_templates.get(
                                                requirement_relationship
                                        ):
                                            acs.update_sig_scope(TOSCA.Requirement)
                                            acs.update_sig_scope(
                                                requirement_capability_sig
                                            )
                                            continue
                                        relationship_type = requirement_relationship
                                    else:
                                        relationship_type = None
                                    if relationship_type:
                                        requirement_relationship_type = (
                                            relationship_type
                                        )
                                        requirement_relationship_type_sig = (
                                            self.alloy_sig(relationship_type)
                                        )
                                        merged_requirement_relationship_type = (
                                            self.type_system.merge_node_type(
                                                relationship_type
                                            )
                                        )

                                acs.update_sig_scope(TOSCA.Requirement)
                                acs.update_sig_scope(requirement_relationship_type_sig)
                                acs.update_sig_scope(LocationGraphs.Name)
                                acs.update_sig_scope(requirement_capability_sig)

                                # Compute the scope required by relationship properties.
                                self.compute_scope_properties(
                                    acs,
                                    get_dict(
                                        merged_requirement_relationship_type, PROPERTIES
                                    ),
                                    requirement_relationship_properties,
                                )

                                # Iterate over all relationship attributes.
                                for attribute_name, attribute_yaml in get_dict(
                                        merged_requirement_relationship_type, ATTRIBUTES
                                ).items():
                                    # Compute the scope required by the attribute value.
                                    self.compute_scope_property(
                                        acs, attribute_yaml, None
                                    )
                                # Compute the scope for relationship interfaces.
                                self.compute_scope_interfaces(
                                    acs,
                                    requirement_relationship_type,
                                    merged_requirement_relationship_type,
                                    {},
                                )
                                nb_requirements = nb_requirements + 1

                requirement_lower_occurrences = get_requirement_occurrences(
                    requirement_yaml
                )[0]
                unfilled_requirements = requirement_lower_occurrences - nb_requirements
                if unfilled_requirements > 0:
                    acs.update_sig_scope(TOSCA.Requirement, unfilled_requirements)

        self.compute_scope_templates(
            acs,
            topology_template_yaml,
            NODE_TEMPLATES,
            compute_scope_capabilities_requirements,
        )

        # Iterate over all relationships.
        self.compute_scope_templates(
            acs, topology_template_yaml, RELATIONSHIP_TEMPLATES, None
        )

        # Iterate over all groups.
        self.compute_scope_templates(acs, topology_template_yaml, GROUPS, None)

        # Iterate over all policies.
        self.compute_scope_templates(acs, topology_template_yaml, POLICIES, None)

        # Iterate over all outputs.
        outputs = get_dict(topology_template_yaml, OUTPUTS)
        for output_name, output_yaml in outputs.items():
            # one TOSCA Parameter is required.
            acs.update_sig_scope(TOSCA.Parameter)
            # Compute the scope required by each output value.
            if output_yaml.get(TYPE) is None:
                output_yaml[TYPE] = "string"
            self.compute_scope_property(acs, output_yaml, {})

        # Iterate over substitution_mappings.
        substitution_mappings = topology_template_yaml.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            # Compute the scope required by the substitution mapping.
            node_type = substitution_mappings.get(NODE_TYPE)
            acs.update_sig_scope(self.alloy_sig(node_type))

            merged_node_type_declaration = self.type_system.merge_node_type(node_type)

            # Iterate over all node properties.
            self.compute_scope_properties(
                acs,
                get_dict(merged_node_type_declaration, PROPERTIES),
                get_dict(substitution_mappings, PROPERTIES),
            )

            # Iterate over all node capabilities.
            for capability_name, capability_yaml in get_dict(
                    merged_node_type_declaration, CAPABILITIES
            ).items():
                # Compute the scope required by this capability.
                NOTHING_TO_DO = True

            # Iterate over all node requirements.
            for (requirement_name, requirement_yaml) in get_dict(
                    merged_node_type_declaration, REQUIREMENTS
            ).items():
                # Compute the scope required by this requirement.
                nb_filled_requirements = 0
                for (
                        node_template_requirement_name,
                        node_template_requirement_yaml,
                ) in syntax.get_substitution_mappings_requirements(
                    substitution_mappings
                ).items():
                    if node_template_requirement_name == requirement_name:
                        if node_template_requirement_yaml:
                            acs.update_sig_scope(TOSCA.Requirement)
                            nb_filled_requirements = nb_filled_requirements + 1

                requirement_lower_occurrences = get_requirement_occurrences(
                    requirement_yaml
                )[0]
                unfilled_requirements = (
                        requirement_lower_occurrences - nb_filled_requirements
                )
                if unfilled_requirements > 0:
                    acs.update_sig_scope(TOSCA.Requirement, unfilled_requirements)

            # Compute the scope for node template interfaces.
            self.compute_scope_interfaces(
                acs, node_type, merged_node_type_declaration, substitution_mappings
            )

        # TODO: Iterate over all workflows.

    def generate_commands(self, topology_template_name, topology_template_yaml):
        # Create an Alloy command scope.
        acs = AlloyCommandScope(self.type_system)

        # This scope includes exactly 1 LG Sort and 1 LG Process.
        acs.update_sig_scope(LocationGraphs.Sort, 1)
        acs.update_sig_scope(LocationGraphs.Process, 1)

        # Compute the scope required by this topology template.
        self.compute_scope_topology_template(
            acs, topology_template_name, topology_template_yaml
        )

        # Generate the Show command.
        self.generate("/** There exists some", topology_template_name, "*/")
        self.generate(
            Alloy.RUN,
            " Show_",
            utils.normalize_name(topology_template_name),
            " {",
            sep="",
        )
        self.generate("}", Alloy.FOR, 0, Alloy.BUT)
        self.generate(
            "  // NOTE: Setting following scopes strongly reduces the research space."
        )
        for (sig_name, sig_scope) in acs.get_signature_scopes().items():
            self.generate(
                "  ", Alloy.EXACTLY, " ", sig_scope, " ", sig_name, ",", sep=""
            )
        self.generate(
            "  ",
            self.configuration.get(ALLOY, SCOPE, "Int"),
            " ",
            Alloy.Int,
            ",",
            sep="",
        )
        self.generate("  ", acs.get_seq_scope(), " ", Alloy.seq, sep="")
        self.generate(" ", Alloy.EXPECT, 1)
        self.generate()

        # Generate the Substitute command.
        generate_Substitute_command = False
        imports = syntax.get_imports(self.tosca_service_template.get_yaml())
        # Iterate over imported files.
        index = 0
        for import_definition in imports:
            filepath = self.get_import_full_filepath(import_definition)
            try:
                imported_file_yaml = self.tosca_service_template.imports(
                    filepath
                ).get_yaml()
            except Exception as e:
                self.error("imports[" + str(index) + "]: " + filepath + ": " + str(e), import_definition)
                index = index + 1
                continue
            imported_topology_template_yaml = imported_file_yaml.get(TOPOLOGY_TEMPLATE)
            if imported_topology_template_yaml:
                if imported_topology_template_yaml.get(SUBSTITUTION_MAPPINGS):
                    import_file = syntax.get_import_file(import_definition)
                    imported_topology_template_name = (
                            utils.normalize_name(import_file[: import_file.rfind(".")])
                            + "_topology_template"
                    )
                    # Add this imported topology template to the scope.
                    self.compute_scope_topology_template(
                        acs,
                        imported_topology_template_name,
                        imported_topology_template_yaml,
                    )
                    generate_Substitute_command = True
            index = index + 1

        if generate_Substitute_command:
            self.generate("/** Substitute", topology_template_name, "*/")
            self.generate(
                Alloy.RUN,
                " Substitute_",
                utils.normalize_name(topology_template_name),
                " {",
                sep="",
            )
            self.generate(
                "  apply_substitution[",
                utils.normalize_name(topology_template_name),
                "]",
                sep="",
            )
            self.generate("}", Alloy.FOR, 0, Alloy.BUT)
            self.generate(
                "  // NOTE: Setting following scopes strongly reduces the research space."
            )
            for (sig_name, sig_scope) in acs.get_signature_scopes().items():
                self.generate(
                    "  ", Alloy.EXACTLY, " ", sig_scope, " ", sig_name, ",", sep=""
                )
            self.generate(
                "  ",
                self.configuration.get(ALLOY, SCOPE, "Int"),
                " ",
                Alloy.Int,
                ",",
                sep="",
            )
            self.generate("  ", acs.get_seq_scope(), " ", Alloy.seq, sep="")
            self.generate(" ", Alloy.EXPECT, 1)
            self.generate()

        # TODO: Generate the Create command
        # TODO: Generate the Configure command
        # TODO: Generate the Start command
        # TODO: Generate the Install command

        # TODO: are other commands to generate?


#
# Alloy generator.
#
class AlloyGenerator(AbstractAlloySigGenerator):
    def generator_configuration_id(self):
        return ALLOY

    def generation(self):
        self.info("Alloy generation")

        self.open_file(".als", normalize=True)

        # Init Alloy signatures.
        for type_name, type_yaml in self.type_system.types.items():
            derived_from = syntax.get_derived_from(type_yaml)
            # No Alloy signature for TOSCA data types derived from basic YAML types.
            if not self.type_system.is_yaml_type(derived_from):
                # Declare the Alloy signature related to this TOSCA type.
                type_sig = utils.normalize_name(type_name)
                if not Alloy.is_signature_declared(type_sig):
                    if derived_from:
                        derived_from_sig = self.alloy_sig(derived_from)
                    else:
                        derived_from_sig = None
                    Alloy.declare_signature(type_sig, derived_from_sig)

        #
        # Generate metadata
        #
        self.generate_header("TOSCA Topology Metadata", "")

        for metadata_name in [TOSCA_DEFINITIONS_VERSION, DESCRIPTION]:
            metadata_value = self.tosca_service_template.get_yaml().get(metadata_name)
            if metadata_value:
                self.generate(
                    Alloy.SINGLE_LINE_COMMENT + " ",
                    metadata_name,
                    ": ",
                    metadata_value,
                    sep="",
                )
        self.generate()

        # TODO: Generate all other metadata.

        #
        # Generate open cloudnet modules
        #

        tosca_definitions_version = self.get_tosca_definitions_version()
        if tosca_definitions_version:
            if not self.is_tosca_definitions_version_file():
                self.generate(Alloy.OPEN, "cloudnet/LocationGraphs")
                self.generate(Alloy.OPEN, "cloudnet/TOSCA")
                if (
                        self.configuration.get(ALLOY, "open_tosca_definitions_version")
                        is True
                ):
                    if tosca_definitions_version == "tosca_simple_yaml_1_1":
                        # NOTE: This is a temporary workaround, which would be removed later.
                        self.generate(
                            Alloy.OPEN,
                            "cloudnet/tosca_simple_yaml_1_2 // ISSUE: Given value was "
                            + tosca_definitions_version,
                        )
                    else:
                        self.generate(
                            Alloy.OPEN, "cloudnet/" + tosca_definitions_version
                        )

        self.generate()

        #
        # Generate imports
        #
        imports = self.tosca_service_template.get_yaml().get(IMPORTS)
        if imports:
            self.generate_header("Imports", "")
            for import_yaml in imports:
                import_file = syntax.get_import_file(import_yaml)
                # TBR if import_file.startswith('http://') or import_file.startswith('https://'):
                # import_file = import_file[import_file.rfind('/')+1:] # keep only the file name.
                # if import_file.endswith('.yml') or import_file.endswith('.yaml'):
                #    import_file = import_file[:import_file.rfind('.')] # remove YAML extension.
                # open_file = utils.normalize_name(import_file)
                imported_template = self.tosca_service_template.imports(import_file)
                open_file = self.compute_filename(imported_template)
                self.generate(Alloy.OPEN, open_file)
            self.generate()

        #
        # Generate all TOSCA types and Topology Template
        #
        for generator_class in [
            DataTypeGenerator,
            ArtifactTypeGenerator,
            CapabilityTypeGenerator,
            RequirementTypeGenerator,
            RelationshipTypeGenerator,
            InterfaceTypeGenerator,
            NodeTypeGenerator,
            GroupTypeGenerator,
            PolicyTypeGenerator,
            TopologyTemplateGenerator,
        ]:
            generator = generator_class(generator=self)
            generator.generate_all_sigs()

        self.close_file()
