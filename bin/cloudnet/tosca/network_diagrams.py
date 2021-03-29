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
import os
import shutil

import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.configuration import DEFAULT_CONFIGURATION
from cloudnet.tosca.processors import Generator

NWDIAG = "nwdiag"
DEFAULT_CONFIGURATION[NWDIAG] = {
    # Target directory where network diagrams are generated.
    Generator.TARGET_DIRECTORY: "Results/NetworkDiagrams",
    # Network capability types.
    "linkable_capability_types": ["tosca.capabilities.network.Linkable"],
    # Port capability types.
    "bindable_capability_types": ["tosca.capabilities.network.Bindable"],
    # Representation of node templates.
    "node_types": {
        "tosca.nodes.network.Network": {
            "label": [
                "properties.network_name",
            ],
            "address": [
                "properties.cidr",
                #                'properties.start_ip',
                #                'properties.end_ip',
            ],
            # graphical attributes
            "color": "lightblue",
            "textcolor": "black",
            # no shape as it is a network
        },
        "tosca.nodes.network.Port": {
            "address": [
                "properties.ip_address",
            ],
            # no graphical attributes as it is a port
        },
    },
}
DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}
from cloudnet.tosca.diagnostics import diagnostic

LOGGER = logging.getLogger(__name__)


class Network(object):
    def __init__(self):
        self.network_node = None
        self.nodes = {}


class NwdiagGenerator(Generator):
    """
    This is the generator of network diagrams.
    """

    def generator_configuration_id(self):
        return NWDIAG

    def generation(self):
        self.info("Network diagram generation...")
        topology_template = self.tosca_service_template.get_yaml().get(
            syntax.TOPOLOGY_TEMPLATE
        )
        self.topology_template = topology_template
        if topology_template is None:
            self.info("No network diagram generated.")
        else:
            # generate network diagrams for TOSCA topology templates only
            self.generate_network_diagram(topology_template)
        self.info("Network diagram generation done.")

    def generate_network_diagram(self, topology_template):
        # network ports
        # dict<port node name, array of bindable node templates>
        ports = {}

        def add_port_binding(port_name, node_name):
            port_bindings = ports.get(port_name)
            if port_bindings is None:
                port_bindings = []
                ports[port_name] = port_bindings
            port_bindings.append(node_name)

        # Networks
        # dict<network name, Network>
        networks = {}

        def get_network(network_name):
            network = networks.get(network_name)
            if network is None:
                network = Network()
                networks[network_name] = network
            return network

        # iterates over all the requirements of the substitution mapping
        # in order to create external networks
        substitution_mapping = topology_template.get(syntax.SUBSTITUTION_MAPPINGS)
        if substitution_mapping is not None:
            substitution_mapping_node_type = syntax.get_node_type(substitution_mapping)
            if substitution_mapping_node_type is not None:
                node_type = self.type_system.merge_type(substitution_mapping_node_type)
                node_type_requirements = syntax.get_requirements_dict(node_type)
                for (
                    requirement_name,
                    requirement_value,
                ) in syntax.get_substitution_mappings_requirements(
                    substitution_mapping
                ).items():
                    requirement_definition = node_type_requirements.get(
                        requirement_name
                    )
                    capability = syntax.get_requirement_capability(
                        requirement_definition
                    )
                    if capability in self.configuration.get(
                        NWDIAG, "linkable_capability_types"
                    ):
                        # is a requirement with capability in linkable capability types
                        # create the Network associated to this external network requirement
                        network = get_network(requirement_name)
                        # the requirement node is in the external node
                        network.nodes[requirement_value[0]] = requirement_value[0]

        # iterates over all the node templates
        node_templates = topology_template.get(syntax.NODE_TEMPLATES, {})
        for node_name, node_yaml in node_templates.items():
            # get the node type
            node_type = node_yaml.get(syntax.TYPE)
            node_type_type = self.type_system.merge_type(node_type)

            # TODO: special case for Forwarding node which are both a port and a network
            if node_type == "tosca.nodes.nfv.Forwarding":
                # a Forwarding node is a node of its associated Forwarding network
                get_network(node_name).nodes[node_name] = node_name

            # iterate over all the node capabilities
            # in order to identify node templates which are networks
            for cap_name, cap_def in node_type_type.get(
                syntax.CAPABILITIES, {}
            ).items():
                cap_def_type = (
                    cap_def.get(syntax.TYPE) if isinstance(cap_def, dict) else cap_def
                )
                if cap_def_type in self.configuration.get(
                    NWDIAG, "linkable_capability_types"
                ):
                    # this node template is a network node,
                    # i.e. a node template with a linkable capability
                    get_network(node_name).network_node = node_yaml

            # iterate over all the requirements of the current node
            node_type_requirements = syntax.get_requirements_dict(node_type_type)
            for requirement in syntax.get_requirements_list(node_yaml):
                for requirement_name, requirement_yaml in requirement.items():
                    requirement_definition = node_type_requirements.get(
                        requirement_name
                    )
                    capability = syntax.get_requirement_capability(
                        requirement_definition
                    )
                    if capability in self.configuration.get(
                        NWDIAG, "linkable_capability_types"
                    ):
                        network_node = syntax.get_requirement_node_template(
                            requirement_yaml
                        )
                        # current node template is a node of the network node
                        get_network(network_node).nodes[node_name] = node_name
                    elif capability in self.configuration.get(
                        NWDIAG, "bindable_capability_types"
                    ):
                        binding_node = syntax.get_requirement_node_template(
                            requirement_yaml
                        )
                        add_port_binding(node_name, binding_node)

        # network diagram generation
        if len(networks) == 0:  # no network node template found
            self.info("No network diagram generated.")
        else:
            # network node templates found then
            # generate the network diagram file
            self.open_file(".nwdiag")
            self.generate("{")
            # iterate over all found networks
            for network_name, network in networks.items():
                self.generate("  network %s {" % network_name)
                network_node = network.network_node
                if network_node is None:
                    # this is an external network associated to a network requirement of the substitution mapping
                    network_repr = {}  # use default graphical attributes
                    network_label = network_name
                    network_address = ""  # no network address
                else:
                    # this a network node template
                    network_repr = self.get_representation(network_node)
                    network_label = self.resolve_attribute(
                        network_node, network_repr, "label", "\n"
                    )
                    network_label = (
                        network_label if network_label != "" else network_name
                    )
                    network_address = self.resolve_attribute(
                        network_node, network_repr, "address", "\n"
                    )  # '', ')
                # generate the graphical attributes of the network
                # TODO: add other graphical attributes font, etc.
                self.generate('    label = "%s"' % network_label)
                self.generate('    address = "%s"' % network_address)
                self.generate(
                    '    color = "%s"' % network_repr.get("color", "lightblue")
                )
                self.generate(
                    '    textcolor = "%s"' % network_repr.get("textcolor", "black")
                )

                # generate all the ports connected to the network
                if len(network.nodes) == 0:  # no node found
                    # nwdiag tool requires that a network has nodes else an error is produced!
                    # so generate a graphical note
                    self.generate(
                        '    empty_network_%s[label="This network\nis empty!", shape=note];'
                        % network_name
                    )
                else:
                    # iterates over of the nodes of the network
                    for port_name, node_name in network.nodes.items():
                        port_node = node_templates.get(port_name)
                        port_repr = self.get_representation(port_node)
                        port_address = self.resolve_attribute(
                            port_node, port_repr, "address", ", "
                        )
                        bindings = ports.get(node_name, [node_name])
                        for binding in bindings:
                            bindings = ports.get(binding, [binding])
                            for binding in bindings:
                                binding_node = node_templates.get(binding)
                                binding_repr = self.get_representation(binding_node)
                                binding_label = self.resolve_attribute(
                                    binding_node, binding_repr, "label", "\n"
                                )
                                binding_label = (
                                    binding_label if binding_label != "" else binding
                                )
                                # generate the graphical node
                                # TODO: add other graphical attributes font, etc.
                                self.generate(
                                    '    "%s"[label="%s", address="%s", shape="%s", color="%s", textcolor="%s", style="%s"%s];'
                                    % (
                                        binding,
                                        binding_label,
                                        port_address,
                                        binding_repr.get("shape", "box"),
                                        binding_repr.get("color", "white"),
                                        binding_repr.get("textcolor", "black"),
                                        binding_repr.get("style", "solid"),
                                        self.get_icon_attribute(
                                            binding_node, binding_repr
                                        ),
                                    )
                                )
                self.generate("  }")
            self.generate("}")
            self.close_file()
            # network diagram generated :-)

    def get_representation(self, node_template):
        node_type_name = node_template.get(syntax.TYPE)
        while True:
            # search the graphical representation for the current node type name
            representation = self.configuration.get(NWDIAG, "node_types").get(
                node_type_name
            )
            if representation is not None:  # representation found
                return representation  # so return it
            # else try with the derived_from type
            node_type = self.type_system.get_type(node_type_name)
            if node_type is None:
                # TODO: log error?
                break  # node type not found
            node_type_name = node_type.get(syntax.DERIVED_FROM)
            if node_type_name is None:
                break  # reach a root node type
        # node representation not found!
        # so use default graphical representation
        return {}

    def resolve_attribute(self, node, representation, attribute_name, separator):
        address = ""
        sep1 = ""
        for item in representation.get(attribute_name, []):
            value = node
            for key in item.split("."):
                value = value.get(key)
                if value is None:
                    return ""
            if isinstance(value, dict):
                input_name = value.get("get_input")
                if input_name is not None:
                    value = (
                        self.topology_template.get(syntax.INPUTS, {})
                        .get(input_name, {})
                        .get(syntax.DEFAULT, "")
                    )
            if isinstance(value, list):
                tmp = ""
                sep2 = sep1
                for item in value:
                    tmp += sep2 + str(item)
                    sep2 = " "
                value = tmp
            value = str(value)
            if len(value) > 0:
                address += sep1 + value
                sep1 = separator
        return address

    def get_icon_attribute(self, node, representation):
        icon_file = representation.get("icon")
        if icon_file is None:
            return ""
        # get target directory
        target_directory = self.configuration.get(
            self.generator_configuration_id(), Generator.TARGET_DIRECTORY
        )
        if not os.path.exists(target_directory + "/" + icon_file):
            icon_path = icon_file[: icon_file.rfind("/") + 1]
            # create target directory
            if not os.path.exists(target_directory + "/" + icon_path):
                os.makedirs(target_directory + "/" + icon_path)
            # copy icon_file into target directory
            shutil.copy2(icon_file, target_directory + "/" + icon_file)
        return ', icon="' + icon_file + '"'
