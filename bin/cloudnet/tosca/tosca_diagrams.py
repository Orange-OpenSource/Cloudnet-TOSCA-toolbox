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

import cloudnet.tosca.configuration as configuration
import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.processors import Generator
from cloudnet.tosca.utils import normalize_name, short_type_name

TOSCA_DIAGRAMS = "tosca_diagrams"
configuration.DEFAULT_CONFIGURATION[TOSCA_DIAGRAMS] = {
    # Target directory where network diagrams are generated.
    Generator.TARGET_DIRECTORY: "tosca_diagrams"
}
configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}

LOGGER = logging.getLogger(__name__)


class ToscaDiagramGenerator(Generator):
    """
    This is the generator of TOSCA diagrams.
    """

    def generator_configuration_id(self):
        return TOSCA_DIAGRAMS

    def get_node_name_id(self, node_name):
        node_name_id = normalize_name(node_name)
        if node_name_id == "node":  # 'node' is a dot keyword
            node_name_id = "node_node"  # rename to 'node_node' to avoid dot error.
        return node_name_id

    def generation(self):
        self.info("TOSCA diagram generation")

        topology_template = syntax.get_topology_template(
            self.tosca_service_template.get_yaml()
        )
        # Generate only for TOSCA topology template.
        if topology_template is None:
            return

        # Generate the TOSCA diagram.
        self.open_file(".dot")

        self.generate("graph ToscaDiagram {")
        self.generate('  rankdir="LR"')

        substitution_mappings = syntax.get_substitution_mappings(topology_template)
        if substitution_mappings is not None:
            for capability_name, capability_yaml in syntax.get_capabilities(
                substitution_mappings
            ).items():
                if capability_yaml:
                    if type(capability_yaml) != list:
                        continue  # TODO something when capability_yaml is not a list
                    capability_name_id = normalize_name(capability_name)
                    self.generate(
                        "  ",
                        capability_name_id,
                        '[label="',
                        capability_name,
                        '" shape=cds style=filled fillcolor=orange]',
                        sep="",
                    )
                    self.generate(
                        "  ",
                        capability_name_id,
                        " -- ",
                        normalize_name(capability_yaml[0]),
                        "_capability_",
                        normalize_name(capability_yaml[1]),
                        "[style=dotted]",
                        sep="",
                    )
            substitution_mappings_node_type = syntax.get_node_type(
                substitution_mappings
            )
            self.generate("  subgraph clusterSubstitutionMappings {")
            self.generate('    label="', substitution_mappings_node_type, '"', sep="")

        node_templates = syntax.get_node_templates(topology_template)

        target_capability_ids = {}  # map<requirement_assignment_id,capability_id>
        show_feature_capabilities = set()  # set<node_name>
        show_dependency_requirements = set()  # set<node_name>

        for node_name, node_yaml in node_templates.items():
            node_type_requirements = syntax.get_requirements_dict(
                self.type_system.merge_type(syntax.get_type(node_yaml))
            )
            for requirement in syntax.get_requirements_list(node_yaml):
                for requirement_name, requirement_yaml in requirement.items():
                    # ACK for Alien4Cloud
                    requirement_name = syntax.get_type_requirement(
                        requirement_yaml, requirement_name
                    )
                    if requirement_yaml:
                        requirement_capability = syntax.get_requirement_capability(
                            node_type_requirements.get(requirement_name)
                        )
                        if requirement_capability is None:
                            self.error(requirement_name + ": capability undefined")
                            continue
                        requirement_node = syntax.get_requirement_node_template(
                            requirement_yaml
                        )
                        if requirement_node is None:
                            continue
                        capability_found = False
                        requirement_node_template = node_templates.get(requirement_node)
                        if requirement_node_template is None:
                            self.error(requirement_node + " node template undefined")
                            continue
                        for capability_name, capability_yaml in syntax.get_capabilities(
                            self.type_system.merge_node_type(
                                syntax.get_type(requirement_node_template)
                            )
                        ).items():
                            if self.type_system.is_derived_from(
                                syntax.get_capability_type(capability_yaml),
                                requirement_capability,
                            ):
                                capability_found = True
                                break
                        if capability_found:
                            target_capability_ids[id(requirement)] = (
                                self.get_node_name_id(requirement_node)
                                + "_capability_"
                                + normalize_name(capability_name)
                            )
                            if capability_name == "feature":
                                show_feature_capabilities.add(requirement_node)
                            if requirement_name == "dependency":
                                show_dependency_requirements.add(node_name)
                        else:
                            self.error(
                                ' capability of type "'
                                + requirement_capability
                                + '" not found'
                            )

        for node_name, node_yaml in node_templates.items():
            node_name_id = self.get_node_name_id(node_name)
            node_type = syntax.get_type(node_yaml)
            merged_node_type = self.type_system.merge_type(node_type)
            self.generate("    subgraph cluster", node_name_id, " {", sep="")
            self.generate("      color=white")
            self.generate('      label=""')
            self.generate(
                "      ",
                node_name_id,
                '[label="',
                node_name,
                ": ",
                short_type_name(node_type),
                '|\l\l\l\l" shape=record style=rounded]',
                sep="",
            )
            for capability_name, capability_yaml in syntax.get_capabilities(
                merged_node_type
            ).items():
                if (
                    capability_name != "feature"
                    or node_name in show_feature_capabilities
                ):
                    self.generate(
                        "      ",
                        node_name_id,
                        "_capability_",
                        normalize_name(capability_name),
                        '[label="',
                        capability_name,
                        '" shape=cds style=filled fillcolor=orange]',
                        sep="",
                    )
                    self.generate(
                        "      ",
                        node_name_id,
                        "_capability_",
                        normalize_name(capability_name),
                        " -- ",
                        node_name_id,
                        sep="",
                    )
            for requirement_name, requirement_yaml in syntax.get_requirements_dict(
                merged_node_type
            ).items():
                if (
                    requirement_name != "dependency"
                    or node_name in show_dependency_requirements
                ):
                    self.generate(
                        "      ",
                        node_name_id,
                        "_requirement_",
                        normalize_name(requirement_name),
                        '[label="',
                        requirement_name,
                        '" shape=cds style=filled fillcolor=turquoise]',
                        sep="",
                    )
                    self.generate(
                        "      ",
                        node_name_id,
                        " -- ",
                        node_name_id,
                        "_requirement_",
                        normalize_name(requirement_name),
                        sep="",
                    )
            self.generate("    }")

        for node_name, node_yaml in node_templates.items():
            node_name_id = self.get_node_name_id(node_name)
            for requirement in syntax.get_requirements_list(node_yaml):
                for requirement_name, requirement_yaml in requirement.items():
                    # ACK for Alien4Cloud
                    requirement_name = syntax.get_type_requirement(
                        requirement_yaml, requirement_name
                    )
                    capability_id = target_capability_ids.get(id(requirement))
                    if capability_id is not None:
                        self.generate(
                            "    ",
                            node_name_id,
                            "_requirement_",
                            normalize_name(requirement_name),
                            " -- ",
                            capability_id,
                            "[style=dotted]",
                            sep="",
                        )

        if substitution_mappings is not None:
            self.generate("  }")
            for (
                requirement_name,
                requirement_yaml,
            ) in syntax.get_substitution_mappings_requirements(
                substitution_mappings
            ).items():
                if requirement_yaml:
                    requirement_name_id = normalize_name(requirement_name)
                    self.generate(
                        "  ",
                        requirement_name_id,
                        '[label="',
                        requirement_name,
                        '" shape=cds style=filled fillcolor=turquoise]',
                        sep="",
                    )
                    self.generate(
                        "  ",
                        normalize_name(requirement_yaml[0]),
                        "_requirement_",
                        normalize_name(requirement_yaml[1]),
                        " -- ",
                        requirement_name_id,
                        "[style=dotted]",
                        sep="",
                    )

        self.generate("}")
        self.close_file()
