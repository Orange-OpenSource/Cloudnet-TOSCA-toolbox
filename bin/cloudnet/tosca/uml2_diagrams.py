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

import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.configuration import DEFAULT_CONFIGURATION
from cloudnet.tosca.processors import Generator
from cloudnet.tosca.syntax import *  # TODO remove
from cloudnet.tosca.utils import normalize_name, short_type_name

UML2 = "UML2"
DEFAULT_CONFIGURATION[UML2] = {
    # Target directory where UML2 diagrams are generated.
    Generator.TARGET_DIRECTORY: "Results/Uml2Diagrams",
    "kinds": {
        "Compute": "node",  # OASIS TOSCA 1.2
        "tosca.nodes.Compute": "node",  # OASIS TOSCA 1.2
        "tosca.nodes.nfv.Vdu.Compute": "node",  # ETSI NVF SOL 001
        "tosca.nodes.Abstract.Storage": "database",  # OASIS TOSCA 1.2
        "tosca.nodes.nfv.Vdu.VirtualStorage": "database",  # ETSI NVF SOL 001 v0.9
        "tosca.nodes.nfv.Vdu.VirtualBlockStorage": "database",  # ETSI NVF SOL 001 v0.10.0
        "tosca.nodes.nfv.Vdu.VirtualObjectStorage": "database",  # ETSI NVF SOL 001 v0.10.0
        "tosca.nodes.nfv.Vdu.VirtualFileStorage": "database",  # ETSI NVF SOL 001 v0.10.0
        "tosca.nodes.network.Network": "queue",  # OASIS TOSCA 1.2
        "tosca.nodes.nfv.NsVirtualLink": "queue",  # ETSI NVF SOL 001 v2.5.1
        "tosca.nodes.nfv.VnfVirtualLink": "queue",  # ETSI NVF SOL 001
        "tosca.capabilities.nfv.VirtualLinkable": "queue",  # ETSI NVF SOL 001
    },
}
DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}

LOGGER = logging.getLogger(__name__)


class PlantUMLGenerator(Generator):
    def generator_configuration_id(self):
        return UML2

    def generation(self):
        self.info("UML2 diagram generation")

        self.generate_UML2_class_diagram()

        topology_template = syntax.get_topology_template(
            self.tosca_service_template.get_yaml()
        )
        if topology_template:
            self.open_file("-uml2-component-diagram1.plantuml")
            self.generate_UML2_component_diagram(topology_template, False)
            self.close_file()

            self.open_file("-uml2-component-diagram2.plantuml")
            self.generate_UML2_component_diagram(topology_template, True)
            self.close_file()

            self.open_file("-uml2-deployment-diagram.plantuml")
            self.generate_UML2_deployment_diagram(topology_template)
            self.close_file()

    def generate_UML2_class_diagram(self):
        template_yaml = self.tosca_service_template.get_yaml()
        # Get types.
        data_types = syntax.get_data_types(template_yaml)
        artifact_types = syntax.get_artifact_types(template_yaml)
        capability_types = syntax.get_capability_types(template_yaml)
        relationship_types = syntax.get_relationship_types(template_yaml)
        interface_types = syntax.get_interface_types(template_yaml)
        node_types = syntax.get_node_types(template_yaml)
        group_types = syntax.get_group_types(template_yaml)
        policy_types = syntax.get_policy_types(template_yaml)
        # Return if no types is defined.
        if (
            len(data_types) == 0
            and len(artifact_types) == 0
            and len(capability_types) == 0
            and len(relationship_types) == 0
            and len(interface_types) == 0
            and len(node_types) == 0
            and len(group_types) == 0
            and len(policy_types) == 0
        ):
            return

        self.open_file("-uml2-class-diagram.plantuml")
        self.generate("@startuml")
        self.generate("set namespaceSeparator none")

        def generate_class(class_name, class_kind, type_yaml, types):
            def generate_field(field_name, field_yaml):
                declaration = "+"
                if is_property_required(field_yaml):
                    declaration = declaration + "<b>"
                declaration = declaration + field_name
                field_type = syntax.get_type(field_yaml)
                if field_type:
                    declaration = declaration + " : " + field_type
                    if field_type in ["list", "map"]:
                        entry_schema_type = get_entry_schema_type(field_yaml)
                        if entry_schema_type is None:
                            entry_schema_type = "?"
                        declaration = declaration + "<" + entry_schema_type + ">"
                field_default = syntax.get_default(field_yaml)
                if field_default:
                    declaration = declaration + " = " + str(field_default)
                self.generate(declaration)

            def translateToscaOccurrences2UmlMultiplicity(occurrences):
                lower_bound = occurrences[0]
                upper_bound = occurrences[1]
                if lower_bound == upper_bound:
                    return str(lower_bound)
                if upper_bound == syntax.UNBOUNDED:
                    upper_bound = "*"
                return str(lower_bound) + ".." + str(upper_bound)

            derived_from = syntax.get_derived_from(type_yaml)
            if derived_from:
                if types.get(derived_from) is None:
                    self.generate(
                        'class "',
                        derived_from,
                        '" << (',
                        class_kind,
                        ",green) >> #DDDDDD",
                        sep="",
                    )
                self.generate('"', derived_from, '" <|-- "', class_name, '"', sep="")
            self.generate(
                'class "', class_name, '" << (', class_kind, ",green) >> {", sep=""
            )
            mime_type = type_yaml.get(MIME_TYPE)
            if mime_type:
                self.generate("+mime_type:", mime_type)
            file_ext = type_yaml.get(FILE_EXT)
            if file_ext:
                self.generate("+file_ext:", file_ext)
            attributes = get_dict(type_yaml, ATTRIBUTES)
            if len(attributes):
                self.generate(".. attributes ..")
                for attribute_name, attribute_yaml in attributes.items():
                    generate_field(attribute_name, attribute_yaml)
            properties = get_dict(type_yaml, PROPERTIES)
            if len(properties):
                self.generate(".. properties ..")
                for property_name, property_yaml in properties.items():
                    generate_field(property_name, property_yaml)
            capabilities = syntax.get_capabilities(type_yaml)
            if len(capabilities):
                self.generate(".. capabilities ..")
                for capability_name, capability_yaml in capabilities.items():
                    self.generate("+", capability_name, sep="")
                    capability_type = get_capability_type(capability_yaml)
                    if capability_type:
                        capability_occurrence = translateToscaOccurrences2UmlMultiplicity(
                            get_capability_occurrences(capability_yaml)
                        )
                        self.generate(
                            " type : ",
                            capability_type,
                            "[",
                            capability_occurrence,
                            "]",
                            sep="",
                        )
                    if isinstance(capability_yaml, dict):
                        capability_valid_source_types = capability_yaml.get(
                            VALID_SOURCE_TYPES
                        )
                        if capability_valid_source_types:
                            self.generate(
                                " valid_source_types : ",
                                capability_valid_source_types,
                                sep="",
                            )
            requirements = get_dict(type_yaml, REQUIREMENTS)
            if len(requirements):
                self.generate(".. requirements ..")
                for requirement_name, requirement_yaml in requirements.items():
                    requirement_occurrences = syntax.get_requirement_occurrences(
                        requirement_yaml
                    )
                    if requirement_occurrences[0] > 0:
                        bold = "<b>"
                    else:
                        bold = ""
                    self.generate("+", bold, requirement_name, sep="")
                    requirement_capability_type = syntax.get_requirement_capability(
                        requirement_yaml
                    )
                    if requirement_capability_type:
                        uml_multiplicity = translateToscaOccurrences2UmlMultiplicity(
                            requirement_occurrences
                        )
                        self.generate(
                            " capability : ",
                            requirement_capability_type,
                            "[",
                            uml_multiplicity,
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
                        self.generate(" relationship :", requirement_relationship_type)
                    requirement_node = syntax.get_requirement_node_type(
                        requirement_yaml
                    )
                    if requirement_node:
                        self.generate(" node :", requirement_node)
            interfaces = get_dict(type_yaml, INTERFACES)
            if len(interfaces):
                self.generate("--")
                for interface_name, interface_yaml in interfaces.items():
                    self.generate(".. interface", interface_name, "..")
                    for key, value in (
                        syntax.get_operations(interface_yaml).get(OPERATIONS).items()
                    ):
                        self.generate("+", key, "()", sep="")
            if class_kind == "I":
                for key, value in (
                    syntax.get_operations(type_yaml).get(OPERATIONS).items()
                ):
                    self.generate("+", key, "()", sep="")
            self.generate("}")
            for attribute_name, attribute_yaml in attributes.items():
                attribute_type = attribute_yaml.get(TYPE)
                if data_types.get(attribute_type):
                    self.generate(
                        '"',
                        class_name,
                        '" *-- "1" "',
                        attribute_type,
                        '" : ',
                        attribute_name,
                        sep="",
                    )
                if attribute_type in ["list", "map"]:
                    entry_schema_type = get_entry_schema_type(attribute_yaml)
                    if data_types.get(entry_schema_type):
                        self.generate(
                            '"',
                            class_name,
                            '" *-- "*" "',
                            entry_schema_type,
                            '" : ',
                            attribute_name,
                            sep="",
                        )
            for property_name, property_yaml in properties.items():
                property_type = syntax.get_property_type(property_yaml)
                if data_types.get(property_type):
                    self.generate(
                        '"',
                        class_name,
                        '" *-- "1" "',
                        property_type,
                        '" : ',
                        property_name,
                        sep="",
                    )
                if property_type in ["list", "map"]:
                    entry_schema_type = get_entry_schema_type(property_yaml)
                    if data_types.get(entry_schema_type):
                        self.generate(
                            '"',
                            class_name,
                            '" *-- "*" "',
                            entry_schema_type,
                            '" : ',
                            property_name,
                            sep="",
                        )
            for capability_name, capability_yaml in capabilities.items():
                capability_type = get_capability_type(capability_yaml)
                if capability_type:
                    if capability_types.get(capability_type) is None:
                        self.generate(
                            'class "',
                            capability_type,
                            '" << (C,green) >> #DDDDDD',
                            sep="",
                        )
                    self.generate(
                        '"',
                        capability_type,
                        '" "',
                        translateToscaOccurrences2UmlMultiplicity(
                            get_capability_occurrences(capability_yaml)
                        ),
                        '" -* "',
                        class_name,
                        '" : ',
                        capability_name,
                        sep="",
                    )
                if isinstance(capability_yaml, dict):
                    capability_valid_source_types = capability_yaml.get(
                        VALID_SOURCE_TYPES
                    )
                    if capability_valid_source_types:
                        for (
                            capability_valid_source_type
                        ) in capability_valid_source_types:
                            if node_types.get(capability_valid_source_type) is None:
                                self.generate(
                                    'class "',
                                    capability_valid_source_type,
                                    '" << (N,green) >> #DDDDDD',
                                    sep="",
                                )
                            self.generate(
                                '"',
                                capability_valid_source_type,
                                '" <.. "',
                                class_name,
                                '" : ',
                                capability_name,
                                ".valid_source_types",
                                sep="",
                            )
            for requirement_name, requirement_yaml in requirements.items():
                requirement_capability_type = syntax.get_requirement_capability(
                    requirement_yaml
                )
                if requirement_capability_type:
                    if capability_types.get(requirement_capability_type) is None:
                        self.generate(
                            'class "',
                            requirement_capability_type,
                            '" << (C,green) >> #DDDDDD',
                            sep="",
                        )
                    self.generate(
                        '"',
                        class_name,
                        '" *- "',
                        translateToscaOccurrences2UmlMultiplicity(
                            get_requirement_occurrences(requirement_yaml)
                        ),
                        '" "',
                        requirement_capability_type,
                        '" : ',
                        requirement_name,
                        sep="",
                    )
                requirement_relationship = syntax.get_requirement_relationship(
                    requirement_yaml
                )
                requirement_relationship_type = syntax.get_relationship_type(
                    requirement_relationship
                )
                if requirement_relationship_type:
                    if relationship_types.get(requirement_relationship_type) is None:
                        self.generate(
                            'class "',
                            requirement_relationship_type,
                            '" << (R,green) >> #DDDDDD',
                            sep="",
                        )
                    self.generate(
                        '"',
                        class_name,
                        '" ..> "',
                        requirement_relationship_type,
                        '" : ',
                        requirement_name,
                        ".relationship",
                        sep="",
                    )
                requirement_node = syntax.get_requirement_node_type(requirement_yaml)
                if requirement_node:
                    if node_types.get(requirement_node) is None:
                        self.generate(
                            'class "',
                            requirement_node,
                            '" << (N,green) >> #DDDDDD',
                            sep="",
                        )
                    self.generate(
                        '"',
                        class_name,
                        '" ..> "',
                        requirement_node,
                        '" : ',
                        requirement_name,
                        ".node",
                        sep="",
                    )
            for interface_name, interface_yaml in interfaces.items():
                interface_type = interface_yaml.get(TYPE)
                if interface_type:
                    if interface_types.get(interface_type) is None:
                        self.generate(
                            'class "',
                            interface_type,
                            '" << (I,green) >> #DDDDDD',
                            sep="",
                        )
                    self.generate(
                        '"',
                        interface_type,
                        '" <|.. "',
                        class_name,
                        '" : ',
                        interface_name,
                        sep="",
                    )
            valid_target_types = type_yaml.get(VALID_TARGET_TYPES)
            if valid_target_types:
                for valid_target_type in valid_target_types:
                    self.generate(
                        '"',
                        class_name,
                        '" ..> "',
                        valid_target_type,
                        '" : valid_target_types',
                        sep="",
                    )
            members = type_yaml.get(MEMBERS)
            if members:
                for member in members:
                    if node_types.get(member) is None:
                        self.generate(
                            'class "', member, '" << (N,green) >> #DDDDDD', sep=""
                        )
                    self.generate(
                        '"', class_name, '" ..> "*" "', member, '" : members', sep=""
                    )
            targets = type_yaml.get(TARGETS)
            if targets:
                for target in targets:
                    if (
                        node_types.get(target) is None
                        and group_types.get(target) is None
                    ):
                        if "nodes." in target:
                            stereotype = "N"
                        elif "groups." in target:
                            stereotype = "G"
                        else:
                            stereotype = "X"
                        self.generate(
                            'class "',
                            target,
                            '" << (',
                            stereotype,
                            ",green) >> #DDDDDD",
                            sep="",
                        )
                    self.generate(
                        '"', class_name, '" ..> "*" "', target, '" : targets', sep=""
                    )

        def generate_classes(type_kind, class_kind, types):
            #            self.generate('package', type_kind, '{')
            for type_name, type_yaml in types.items():
                generate_class(type_name, class_kind, type_yaml, types)

        #            self.generate('}')

        # Generate the UML class associated to each type.
        generate_classes("data_types", "D", data_types)
        generate_classes("artifact_types", "A", artifact_types)
        generate_classes("capability_types", "C", capability_types)
        generate_classes("relationship_types", "R", relationship_types)
        generate_classes("interface_types", "I", interface_types)
        generate_classes("node_types", "N", node_types)
        generate_classes("group_types", "G", group_types)
        generate_classes("policy_types", "P", policy_types)

        self.generate("@enduml")
        self.close_file()

    def generate_UML2_component_diagram(self, topology_template, with_relationships):
        self.generate("@startuml")
        self.generate("skinparam componentStyle uml2")
        if with_relationships:
            self.generate("skinparam component {")
            self.generate("  backgroundColor<<relationship>> White")
            self.generate("}")
        self.generate()

        substitution_mappings = topology_template.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            substitution_mappings_uml_id = SUBSTITUTION_MAPPINGS
            substitution_mappings_node_type = substitution_mappings.get(NODE_TYPE)
            merged_substitution_mappings_type = self.type_system.merge_node_type(
                substitution_mappings_node_type
            )
            for capability_name, capability_yaml in get_dict(
                merged_substitution_mappings_type, CAPABILITIES
            ).items():
                capability_uml_id = (
                    substitution_mappings_uml_id + "_" + normalize_name(capability_name)
                )
                # Declare an UML interface for the substitution_mappings capability.
                self.generate(
                    'interface "', capability_name, '" as ', capability_uml_id, sep=""
                )
            self.generate(
                'component ": ',
                substitution_mappings_node_type,
                '" <<node>> as ',
                substitution_mappings_uml_id,
                " {",
                sep="",
            )

        relationship_templates = get_dict(topology_template, RELATIONSHIP_TEMPLATES)

        already_generated_interfaces = {}

        # Iterate over all node templates.
        node_templates = get_dict(topology_template, NODE_TEMPLATES)
        for node_template_name, node_template_yaml in node_templates.items():
            node_template_type = node_template_yaml.get(TYPE)
            merged_node_template_type = self.type_system.merge_node_type(
                node_template_type
            )
            node_template_uml_id = "node_" + normalize_name(node_template_name)
            # Declare an UML component for the node template.
            self.generate(
                'component "',
                node_template_name,
                ": ",
                short_type_name(node_template_type),
                '" <<node>> as ',
                node_template_uml_id,
                sep="",
            )
            # Iterate over all capabilities of the node template.
            for capability_name, capability_yaml in get_dict(
                merged_node_template_type, CAPABILITIES
            ).items():
                if isinstance(capability_yaml, dict):
                    capability_occurrences = capability_yaml.get(OCCURRENCES)
                else:
                    capability_occurrences = None
                if with_relationships or (
                    capability_occurrences and capability_occurrences[0] > 0
                ):
                    capability_uml_id = (
                        node_template_uml_id + "_" + normalize_name(capability_name)
                    )
                    # Declare an UML interface for the node template capability.
                    self.generate(
                        'interface "',
                        capability_name,
                        '" as ',
                        capability_uml_id,
                        sep="",
                    )
                    # Connect the capability UML interface to the node template UML component.
                    self.generate(capability_uml_id, "--", node_template_uml_id)
                    already_generated_interfaces[capability_uml_id] = capability_uml_id
            if with_relationships:
                # Iterate over all requirements of the node template.
                index = 0
                for requirement in get_list(node_template_yaml, REQUIREMENTS):
                    for requirement_name, requirement_yaml in requirement.items():
                        requirement_uml_id = (
                            node_template_uml_id
                            + "_"
                            + normalize_name(requirement_name)
                            + "_relationship"
                            + str(index)
                        )
                        index = index + 1

                        requirement_node = get_requirement_node_template(
                            requirement_yaml
                        )
                        if requirement_node is None:
                            continue

                        relationship_component_name = ""  # No name.
                        relationship_component_type = None

                        if isinstance(requirement_yaml, dict):
                            requirement_relationship = syntax.get_requirement_relationship(
                                requirement_yaml
                            )
                            if isinstance(requirement_relationship, dict):
                                relationship_component_type = syntax.get_relationship_type(
                                    requirement_relationship
                                )
                            else:
                                relationship_template = relationship_templates.get(
                                    requirement_relationship
                                )
                                if relationship_template:
                                    relationship_component_name = (
                                        requirement_relationship
                                    )
                                    relationship_component_type = relationship_template.get(
                                        TYPE
                                    )
                                else:
                                    relationship_component_type = (
                                        requirement_relationship
                                    )
                        if relationship_component_type is None:
                            requirement = get_dict(
                                merged_node_template_type, REQUIREMENTS
                            ).get(requirement_name, {})
                            tmp = syntax.get_requirement_relationship(requirement)
                            relationship_component_type = syntax.get_relationship_type(
                                tmp
                            )
                        if relationship_component_type is None:
                            continue
                        # Declare an UML component for the node template requirement relationship.
                        self.generate(
                            'component "',
                            relationship_component_name,
                            ": ",
                            short_type_name(relationship_component_type),
                            '" <<relationship>> as ',
                            requirement_uml_id,
                            sep="",
                        )
                        # Declare an UML interface for the node template requirement relationship.
                        self.generate(
                            'interface " " as ', requirement_uml_id, "_source", sep=""
                        )
                        # Connect the UML interface to the relationship UML component.
                        self.generate(
                            requirement_uml_id,
                            "_source",
                            " -- ",
                            requirement_uml_id,
                            sep="",
                        )
                        # Connect the node template UML component to the relationship UML component.
                        self.generate(
                            node_template_uml_id,
                            " --( ",
                            requirement_uml_id,
                            "_source",
                            " : ",
                            requirement_name,
                            sep="",
                        )
            self.generate()

        # Iterate over all node templates.
        for node_template_name, node_template_yaml in node_templates.items():
            node_template_uml_id = "node_" + normalize_name(node_template_name)
            node_template_type = node_template_yaml.get(TYPE)
            merged_node_template_type = self.type_system.merge_node_type(
                node_template_type
            )
            # Iterate over all requirements of the node template.
            index = 0
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    source_uml_id = node_template_uml_id
                    if with_relationships:
                        source_uml_id = (
                            source_uml_id
                            + "_"
                            + normalize_name(requirement_name)
                            + "_relationship"
                            + str(index)
                        )
                    index = index + 1
                    requirement_node = get_requirement_node_template(requirement_yaml)
                    if requirement_node is None:
                        continue
                    requirement_node_template = node_templates.get(requirement_node)
                    if requirement_node_template is None:
                        continue
                    requirement_node_type_name = requirement_node_template.get(TYPE)
                    if requirement_node_type_name is None:
                        continue

                    requirement_capability = syntax.get_requirement_capability(
                        get_dict(merged_node_template_type, REQUIREMENTS).get(
                            requirement_name
                        )
                    )
                    capability_found = False
                    for (capability_name, capability_yaml) in get_dict(
                        self.type_system.merge_node_type(requirement_node_type_name),
                        CAPABILITIES,
                    ).items():
                        if self.type_system.is_derived_from(
                            syntax.get_capability_type(capability_yaml),
                            requirement_capability,
                        ):
                            capability_found = True
                            break
                    if capability_found:
                        target_node_uml_id = "node_" + normalize_name(requirement_node)
                        target_capability_uml_id = (
                            target_node_uml_id + "_" + normalize_name(capability_name)
                        )
                        if with_relationships:
                            self.generate(
                                source_uml_id, " --( ", target_capability_uml_id, sep=""
                            )
                        else:
                            if (
                                already_generated_interfaces.get(
                                    target_capability_uml_id
                                )
                                is None
                            ):
                                self.generate(
                                    'interface "',
                                    capability_name,
                                    '" as ',
                                    target_capability_uml_id,
                                    sep="",
                                )
                                # Connect the capability UML interface to the node template UML component.
                                self.generate(
                                    target_capability_uml_id, "--", target_node_uml_id
                                )
                                already_generated_interfaces[
                                    target_capability_uml_id
                                ] = target_capability_uml_id
                            self.generate(
                                source_uml_id,
                                " --( ",
                                target_capability_uml_id,
                                " : ",
                                requirement_name,
                                sep="",
                            )

        if substitution_mappings:
            capabilities = get_dict(substitution_mappings, CAPABILITIES)

            for capability_name, capability_yaml in get_dict(
                merged_substitution_mappings_type, CAPABILITIES
            ).items():
                capability = capabilities.get(capability_name)
                if capability is not None:
                    if not isinstance(capability, list):
                        continue  # TODO when capability is not a list
                    target_node_uml_id = "node_" + capability[0]
                    target_uml_id = (
                        target_node_uml_id + "_" + normalize_name(capability[1])
                    )

                    if already_generated_interfaces.get(target_uml_id) is None:
                        self.generate(
                            'interface "',
                            capability_name,
                            '" as ',
                            target_uml_id,
                            sep="",
                        )
                        # Connect the capability UML interface to the node template UML component.
                        self.generate(target_uml_id, "--", target_node_uml_id)
                        already_generated_interfaces[target_uml_id] = target_uml_id

            self.generate("}")

            for capability_name, capability_yaml in get_dict(
                merged_substitution_mappings_type, CAPABILITIES
            ).items():
                capability_uml_id = (
                    substitution_mappings_uml_id + "_" + normalize_name(capability_name)
                )
                # Connect the capability UML interface to the node template UML component.
                capability = capabilities.get(capability_name)
                if capability is not None:
                    if not isinstance(capability, list):
                        continue  # TODO when capability is not a list
                    target_node_uml_id = "node_" + capability[0]
                    target_uml_id = (
                        target_node_uml_id + "_" + normalize_name(capability[1])
                    )
                    self.generate(capability_uml_id, "--(", target_uml_id)
                else:
                    self.generate(capability_uml_id, "--", substitution_mappings_uml_id)

            index = 0
            for (
                requirement_name,
                requirement_yaml,
            ) in syntax.get_substitution_mappings_requirements(
                substitution_mappings
            ).items():
                interface_uml_id = (
                    substitution_mappings_uml_id
                    + "_"
                    + normalize_name(requirement_name)
                    + str(index)
                )
                index = index + 1
                self.generate(
                    'interface "', requirement_name, '" as ', interface_uml_id
                )
                if requirement_yaml:
                    source_uml_id = "node_" + normalize_name(requirement_yaml[0])
                    self.generate(
                        source_uml_id,
                        " --( ",
                        interface_uml_id,
                        " : ",
                        requirement_yaml[1],
                        sep="",
                    )
                else:
                    self.generate(
                        substitution_mappings_uml_id,
                        " -- ",
                        interface_uml_id,
                        " : ",
                        requirement_name,
                    )

        self.generate("@enduml")

    def generate_UML2_deployment_diagram(self, topology_template):
        self.generate("@startuml")
        self.generate("skinparam componentStyle uml2")
        self.generate()

        node_templates = get_dict(topology_template, NODE_TEMPLATES)

        non_containeds = list(node_templates.keys())
        containers = {}
        contained_containers = []

        # Iterate over all node templates to find containers.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(
                node_template_yaml.get(TYPE)
            )
            # Iterate over all capabilities of the node template type.
            for capability_name, capability_yaml in get_dict(
                merged_node_template_type, CAPABILITIES
            ).items():
                capability_type = get_capability_type(capability_yaml)
                if self.type_system.is_derived_from(
                    capability_type, "tosca.capabilities.Container"
                ):
                    containers[node_template_name] = containers.get(
                        node_template_name, dict()
                    )
                    try:
                        non_containeds.remove(node_template_name)
                    except ValueError:
                        pass

        # Iterate over all node templates to find containeds.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(
                node_template_yaml.get(TYPE)
            )
            # Iterate over all requirements of the node template.
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    requirement_definition = get_dict(
                        merged_node_template_type, REQUIREMENTS
                    ).get(requirement_name)
                    requirement_relationship = syntax.get_requirement_relationship(
                        requirement_definition
                    )
                    requirement_relationship_type = syntax.get_relationship_type(
                        requirement_relationship
                    )
                    if self.type_system.is_derived_from(
                        requirement_relationship_type, "tosca.relationships.HostedOn"
                    ):
                        requirement_node = get_requirement_node_template(
                            requirement_yaml
                        )
                        if requirement_node is not None:
                            try:
                                containers[requirement_node][
                                    node_template_name
                                ] = containers.get(node_template_name, dict())
                            except KeyError as e:
                                self.error(e)
                            contained_containers.append(node_template_name)
                            try:
                                non_containeds.remove(node_template_name)
                            except ValueError:
                                pass

        # TODO: Remove containers contained by other containers.
        for contained_container_name in contained_containers:
            if containers.get(contained_container_name) is not None:
                del containers[contained_container_name]

        # Iterate over all containers.

        def get_uml2_kind(tosca_type):
            uml2_kind = "component"
            for tt, kind in self.configuration.get(UML2, "kinds").items():
                if self.type_system.is_derived_from(tosca_type, tt):
                    uml2_kind = kind
                    break
            return uml2_kind

        def generate_container(self, container_name, containeds):
            node_template = node_templates.get(container_name)
            node_template_type = node_template.get(TYPE)
            uml2_kind = get_uml2_kind(node_template_type)
            node_template_artifacts = get_dict(node_template, ARTIFACTS)
            if len(containeds) == 0 and len(node_template_artifacts) == 0:
                self.generate(
                    uml2_kind,
                    ' "',
                    container_name,
                    ": ",
                    short_type_name(node_template_type),
                    '" as node_',
                    normalize_name(container_name),
                    sep="",
                )
            else:
                self.generate(
                    uml2_kind,
                    ' "',
                    container_name,
                    ": ",
                    short_type_name(node_template_type),
                    '" as node_',
                    normalize_name(container_name),
                    " {",
                    sep="",
                )
                for contained_name, contained_dict in containeds.items():
                    generate_container(self, contained_name, contained_dict)
                for artifact_name, artifact_yaml in node_template_artifacts.items():
                    artifact_type = syntax.get_artifact_type(artifact_yaml)
                    if artifact_type is None:
                        artifact_type = "Artifact"
                    self.generate(
                        'artifact "',
                        syntax.get_artifact_file(artifact_yaml),
                        '" <<',
                        artifact_type,
                        ">> as node_",
                        normalize_name(container_name),
                        "_artifact_",
                        normalize_name(artifact_name),
                        sep="",
                    )
                self.generate("}")

        substitution_mappings = topology_template.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            # Create components connected to the capabilities of the substitition mapping.
            for capability_name, capability_yaml in get_dict(
                substitution_mappings, CAPABILITIES
            ).items():
                self.generate(
                    'component "a node" as substitution_mappings_capability_',
                    normalize_name(capability_name),
                    sep="",
                )

            substitution_mappings_node_type = substitution_mappings.get(NODE_TYPE)
            self.generate(
                get_uml2_kind(substitution_mappings_node_type),
                ' ": ',
                substitution_mappings_node_type,
                '" as substitution_mappings {',
                sep="",
            )

        for container_name, containeds in containers.items():
            generate_container(self, container_name, containeds)

        for node_template_name in non_containeds:
            generate_container(self, node_template_name, {})

        relationship_templates = get_dict(topology_template, RELATIONSHIP_TEMPLATES)

        # Iterate over all node templates to draw relationships.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(
                node_template_yaml.get(TYPE)
            )
            # Iterate over all requirements of the node template.
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    requirement_relationship_type = None
                    if isinstance(requirement_yaml, dict):
                        requirement_relationship = syntax.get_requirement_relationship(
                            requirement_yaml
                        )
                        if isinstance(requirement_relationship, dict):
                            requirement_relationship_type = syntax.get_relationship_type(
                                requirement_relationship
                            )
                        else:
                            relationship_template = relationship_templates.get(
                                requirement_relationship
                            )
                            if relationship_template:
                                requirement_relationship_type = relationship_template.get(
                                    TYPE
                                )
                            else:
                                requirement_relationship_type = requirement_relationship
                    if requirement_relationship_type is None:
                        requirement = get_dict(
                            merged_node_template_type, REQUIREMENTS
                        ).get(requirement_name, {})
                        tmp = syntax.get_requirement_relationship(requirement)
                        requirement_relationship_type = syntax.get_relationship_type(
                            tmp
                        )
                    if requirement_relationship_type is None:
                        continue

                    if not self.type_system.is_derived_from(
                        requirement_relationship_type, "tosca.relationships.HostedOn"
                    ):
                        requirement_node = get_requirement_node_template(
                            requirement_yaml
                        )
                        if requirement_node:
                            self.generate(
                                "node_",
                                normalize_name(node_template_name),
                                ' "',
                                requirement_name,
                                '" ..> node_',
                                normalize_name(requirement_node),
                                " : <<",
                                short_type_name(requirement_relationship_type),
                                ">>",
                                sep="",
                            )

        if substitution_mappings:
            self.generate("}")
            # Connect created components to the nodes exported by the capabilities of the substitition mapping.
            for capability_name, capability_yaml in get_dict(
                substitution_mappings, CAPABILITIES
            ).items():
                if not isinstance(capability_yaml, list):
                    continue  # TODO
                target_node_name = capability_yaml[0]
                target_capability_name = capability_yaml[1]
                self.generate(
                    "substitution_mappings_capability_",
                    normalize_name(capability_name),
                    ' "',
                    capability_name,
                    '" ..> node_',
                    normalize_name(target_node_name),
                    sep="",
                )

            merged_substitution_mappings_node_type = self.type_system.merge_node_type(
                substitution_mappings_node_type
            )
            # Get all requirements of the node type of the substitution mapping.
            all_requirement_declarations = get_dict(
                merged_substitution_mappings_node_type, REQUIREMENTS
            )
            req_idx = 0
            # Iterate over all requirements of the substitution mapping.
            for (
                requirement_name,
                requirement_yaml,
            ) in syntax.get_substitution_mappings_requirements(
                substitution_mappings
            ).items():
                requirement_capability = syntax.get_requirement_capability(
                    all_requirement_declarations.get(requirement_name)
                )
                if requirement_capability is None:
                    continue
                self.generate(
                    get_uml2_kind(requirement_capability),
                    ' ": ',
                    short_type_name(requirement_capability),
                    '" as substitution_mappings_requirement_',
                    req_idx,
                    sep="",
                )
                requirement_node = requirement_yaml[0]
                requirement_node_capability = requirement_yaml[1]
                self.generate(
                    "node_",
                    normalize_name(requirement_node),
                    ' "',
                    normalize_name(requirement_node_capability),
                    '" ..> "',
                    requirement_name,
                    '" substitution_mappings_requirement_',
                    req_idx,
                    sep="",
                )
                req_idx = req_idx + 1

        self.generate("@enduml")
