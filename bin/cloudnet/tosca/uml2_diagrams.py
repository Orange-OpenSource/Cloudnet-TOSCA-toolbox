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

from cloudnet.tosca.utils import normalize_name, short_type_name
from cloudnet.tosca.processors import Generator
import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.syntax import * # TODO remove

from cloudnet.tosca.configuration import DEFAULT_CONFIGURATION
UML2 = 'UML2'
DEFAULT_CONFIGURATION[UML2] = {
    # Target directory where UML2 diagrams are generated.
    Generator.TARGET_DIRECTORY: 'uml2',
    'kinds': {
        'Compute': 'node', # OASIS TOSCA 1.2
        'tosca.nodes.Compute': 'node', # OASIS TOSCA 1.2
        'tosca.nodes.nfv.Vdu.Compute': 'node', # ETSI NVF SOL 001
        'tosca.nodes.Abstract.Storage': 'database', # OASIS TOSCA 1.2
        'tosca.nodes.nfv.Vdu.VirtualStorage': 'database', # ETSI NVF SOL 001 v0.9
        'tosca.nodes.nfv.Vdu.VirtualBlockStorage': 'database', # ETSI NVF SOL 001 v0.10.0
        'tosca.nodes.nfv.Vdu.VirtualObjectStorage': 'database', # ETSI NVF SOL 001 v0.10.0
        'tosca.nodes.nfv.Vdu.VirtualFileStorage': 'database', # ETSI NVF SOL 001 v0.10.0
        'tosca.nodes.network.Network': 'queue', # OASIS TOSCA 1.2
        'tosca.nodes.nfv.NsVirtualLink': 'queue', # ETSI NVF SOL 001 v2.5.1
        'tosca.nodes.nfv.VnfVirtualLink': 'queue', # ETSI NVF SOL 001
        'tosca.capabilities.nfv.VirtualLinkable': 'queue', # ETSI NVF SOL 001
    },
    'direction': {
        'tosca.relationships.network.BindsTo': 'up', # OASIS TOSCA
    },
    'node_types': {
    }
}
DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

class PlantUMLGenerator(Generator):

    def generator_configuration_id(self):
        return UML2

    def generation(self):
        self.info('UML2 diagram generation')

        self.generate_UML2_class_diagram()

        topology_template = syntax.get_topology_template(self.tosca_service_template.get_yaml())
        if topology_template:
            self.open_file('-uml2-component-diagram1.plantuml')
            self.generate_UML2_component_diagram(topology_template, False)
            self.close_file()

            self.open_file('-uml2-component-diagram2.plantuml')
            self.generate_UML2_component_diagram(topology_template, True)
            self.close_file()

            self.open_file('-uml2-deployment-diagram.plantuml')
            self.generate_UML2_deployment_diagram(topology_template)
            self.close_file()

            self.generate_UML2_workflow_diagrams(topology_template)

            self.generate_UML2_sequence_diagrams(topology_template)

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
        if len(data_types) == 0 and len(artifact_types) == 0 and len(capability_types) == 0 and len(relationship_types) == 0 and len(interface_types) == 0 and len(node_types) == 0 and len(group_types) == 0 and len(policy_types) == 0:
            return

        self.open_file('-uml2-class-diagram.plantuml')
        self.generate('@startuml')
        self.generate('set namespaceSeparator none')

        def generate_class(class_name, class_kind, type_yaml, types):

            def generate_field(field_name, field_yaml):
                declaration = '+'
                if is_property_required(field_yaml):
                    declaration = declaration + '<b>'
                declaration = declaration + field_name
                field_type = syntax.get_type(field_yaml)
                if field_type:
                    declaration = declaration + ' : ' + field_type
                    if field_type in ['list', 'map']:
                        entry_schema_type = get_entry_schema_type(field_yaml)
                        if entry_schema_type == None:
                            entry_schema_type = '?'
                        declaration = declaration + '<' + entry_schema_type + '>'
                field_default = syntax.get_default(field_yaml)
                if field_default:
                    declaration = declaration + ' = ' + str(field_default)
                self.generate(declaration)

            def translateToscaOccurrences2UmlMultiplicity(occurrences):
                lower_bound = occurrences[0]
                upper_bound = occurrences[1]
                if lower_bound == upper_bound:
                    return str(lower_bound)
                if upper_bound == syntax.UNBOUNDED:
                    upper_bound = '*'
                return str(lower_bound) + '..' + str(upper_bound)

            derived_from = syntax.get_derived_from(type_yaml)
            if derived_from:
                if types.get(derived_from) == None:
                    self.generate('class "', derived_from, '" << (', class_kind, ',green) >> #DDDDDD', sep='')
                self.generate('"', derived_from, '" <|-- "', class_name, '"', sep='')
            self.generate('class "', class_name, '" << (', class_kind, ',green) >> {', sep='')
            mime_type = type_yaml.get(MIME_TYPE)
            if mime_type:
                self.generate('+mime_type:', mime_type)
            file_ext = type_yaml.get(FILE_EXT)
            if file_ext:
                self.generate('+file_ext:', file_ext)
            attributes = get_dict(type_yaml, ATTRIBUTES)
            if len(attributes):
                self.generate('.. attributes ..')
                for attribute_name, attribute_yaml in attributes.items():
                    generate_field(attribute_name, attribute_yaml)
            properties = get_dict(type_yaml, PROPERTIES)
            if len(properties):
                self.generate('.. properties ..')
                for property_name, property_yaml in properties.items():
                    generate_field(property_name, property_yaml)
            capabilities = syntax.get_capabilities(type_yaml)
            if len(capabilities):
                self.generate('.. capabilities ..')
                for capability_name, capability_yaml in capabilities.items():
                    self.generate('+', capability_name, sep='')
                    capability_type = get_capability_type(capability_yaml)
                    if capability_type:
                      capability_occurrence = translateToscaOccurrences2UmlMultiplicity(get_capability_occurrences(capability_yaml))
                      self.generate(' type : ', capability_type, '[', capability_occurrence, ']', sep='')
                    if type(capability_yaml) == dict:
                        capability_valid_source_types = capability_yaml.get(VALID_SOURCE_TYPES)
                        if capability_valid_source_types:
                          self.generate(' valid_source_types : ', capability_valid_source_types, sep='')
            requirements = get_dict(type_yaml, REQUIREMENTS)
            if len(requirements):
                self.generate('.. requirements ..')
                for requirement_name, requirement_yaml in requirements.items():
                    requirement_occurrences = syntax.get_requirement_occurrences(requirement_yaml)
                    if requirement_occurrences[0] > 0:
                        bold = '<b>'
                    else:
                        bold = ''
                    self.generate('+', bold, requirement_name, sep='')
                    requirement_capability_type = syntax.get_requirement_capability(requirement_yaml)
                    if requirement_capability_type:
                        uml_multiplicity = translateToscaOccurrences2UmlMultiplicity(requirement_occurrences)
                        self.generate(' capability : ', requirement_capability_type, '[', uml_multiplicity, ']', sep='')
                    requirement_relationship = syntax.get_requirement_relationship(requirement_yaml)
                    requirement_relationship_type = syntax.get_relationship_type(requirement_relationship)
                    if requirement_relationship_type:
                        self.generate(' relationship :',  requirement_relationship_type)
                    requirement_node = syntax.get_requirement_node_type(requirement_yaml)
                    if requirement_node:
                        self.generate(' node :',  requirement_node)
            interfaces = get_dict(type_yaml, INTERFACES)
            if len(interfaces):
                self.generate('--')
                for interface_name, interface_yaml in interfaces.items():
                    self.generate('.. interface', interface_name, '..')
                    for key, value in syntax.get_operations(interface_yaml).get(OPERATIONS).items():
                        self.generate('+', key, '()', sep='')
            if class_kind == 'I':
                for key, value in syntax.get_operations(type_yaml).get(OPERATIONS).items():
                    self.generate('+', key, '()', sep='')
            self.generate('}')
            for attribute_name, attribute_yaml in attributes.items():
                attribute_type = attribute_yaml.get(TYPE)
                if data_types.get(attribute_type):
                    self.generate('"', class_name, '" *-- "1" "', attribute_type, '" : ', attribute_name, sep='')
                if attribute_type in ['list', 'map']:
                    entry_schema_type = get_entry_schema_type(attribute_yaml)
                    if data_types.get(entry_schema_type):
                        self.generate('"', class_name, '" *-- "*" "', entry_schema_type, '" : ', attribute_name, sep='')
            for property_name, property_yaml in properties.items():
                property_type = syntax.get_property_type(property_yaml)
                if data_types.get(property_type):
                    self.generate('"', class_name, '" *-- "1" "', property_type, '" : ', property_name, sep='')
                if property_type in ['list', 'map']:
                    entry_schema_type = get_entry_schema_type(property_yaml)
                    if data_types.get(entry_schema_type):
                        self.generate('"', class_name, '" *-- "*" "', entry_schema_type, '" : ', property_name, sep='')
            for capability_name, capability_yaml in capabilities.items():
                capability_type = get_capability_type(capability_yaml)
                if capability_type:
                    if capability_types.get(capability_type) == None:
                        self.generate('class "', capability_type, '" << (C,green) >> #DDDDDD', sep='')
                    self.generate('"', capability_type, '" "', translateToscaOccurrences2UmlMultiplicity(get_capability_occurrences(capability_yaml)), '" -* "', class_name, '" : ', capability_name, sep='')
                if type(capability_yaml) == dict:
                    capability_valid_source_types = capability_yaml.get(VALID_SOURCE_TYPES)
                    if capability_valid_source_types:
                        for capability_valid_source_type in capability_valid_source_types:
                            if node_types.get(capability_valid_source_type) == None:
                                self.generate('class "', capability_valid_source_type, '" << (N,green) >> #DDDDDD', sep='')
                            self.generate('"', capability_valid_source_type, '" <.. "', class_name, '" : ', capability_name, '.valid_source_types', sep='')
            for requirement_name, requirement_yaml in requirements.items():
                requirement_capability_type = syntax.get_requirement_capability(requirement_yaml)
                if requirement_capability_type:
                    if capability_types.get(requirement_capability_type) == None:
                        self.generate('class "', requirement_capability_type, '" << (C,green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" *- "', translateToscaOccurrences2UmlMultiplicity(get_requirement_occurrences(requirement_yaml)), '" "', requirement_capability_type, '" : ', requirement_name, sep='')
                requirement_relationship = syntax.get_requirement_relationship(requirement_yaml)
                requirement_relationship_type = syntax.get_relationship_type(requirement_relationship)
                if requirement_relationship_type:
                    if relationship_types.get(requirement_relationship_type) == None:
                        self.generate('class "', requirement_relationship_type, '" << (R,green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" ..> "', requirement_relationship_type, '" : ', requirement_name, '.relationship', sep='')
                requirement_node = syntax.get_requirement_node_type(requirement_yaml)
                if requirement_node:
                    if node_types.get(requirement_node) == None:
                        self.generate('class "', requirement_node, '" << (N,green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" ..> "', requirement_node, '" : ', requirement_name, '.node', sep='')
            for interface_name, interface_yaml in interfaces.items():
                    interface_type = interface_yaml.get(TYPE)
                    if interface_type:
                        if interface_types.get(interface_type) == None:
                            self.generate('class "', interface_type, '" << (I,green) >> #DDDDDD', sep='')
                        self.generate('"', interface_type, '" <|.. "', class_name, '" : ', interface_name, sep='')
            valid_target_types = type_yaml.get(VALID_TARGET_TYPES)
            if valid_target_types:
                for valid_target_type in valid_target_types:
                    if capability_types.get(valid_target_type) == None:
                        self.generate('class "', valid_target_type, '" << (C,green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" ..> "', valid_target_type, '" : valid_target_types', sep='')
            members = type_yaml.get(MEMBERS)
            if members:
                for member in members:
                    if node_types.get(member) == None:
                        self.generate('class "', member, '" << (N,green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" ..> "*" "', member, '" : members', sep='')
            targets = type_yaml.get(TARGETS)
            if targets:
                for target in targets:
                    if node_types.get(target) == None and group_types.get(target) == None:
                        if 'nodes.' in target:
                            stereotype = 'N'
                        elif 'groups.' in target:
                            stereotype = 'G'
                        else:
                            stereotype = 'X'
                        self.generate('class "', target, '" << (', stereotype, ',green) >> #DDDDDD', sep='')
                    self.generate('"', class_name, '" ..> "*" "', target, '" : targets', sep='')

        def generate_classes(type_kind, class_kind, types):
#            self.generate('package', type_kind, '{')
            for type_name, type_yaml in types.items():
                generate_class(type_name, class_kind, type_yaml, types)
#            self.generate('}')

        # Generate the UML class associated to each type.
        generate_classes('data_types', 'D', data_types)
        generate_classes('artifact_types', 'A', artifact_types)
        generate_classes('capability_types', 'C', capability_types)
        generate_classes('relationship_types', 'R', relationship_types)
        generate_classes('interface_types', 'I', interface_types)
        generate_classes('node_types', 'N', node_types)
        generate_classes('group_types', 'G', group_types)
        generate_classes('policy_types', 'P', policy_types)

        self.generate('@enduml')
        self.close_file()

    def get_representation(self, node_type_name):
        representations = self.configuration.get(UML2, 'node_types')
        while True:
            node_type_name = self.type_system.get_type_uri(node_type_name)
            # search the graphical representation for the current node type name
            representation = representations.get(node_type_name)
            if representation != None: # representation found
                return representation # so return it
            # else try with the derived_from type
            node_type = self.type_system.get_type(node_type_name)
            if node_type is None:
                # TODO: log error?
                break # node type not found
            node_type_name = node_type.get(syntax.DERIVED_FROM)
            if node_type_name is None:
                break # reach a root node type
        # node representation not found!
        # so use default graphical representation
        return {}

    def get_color(self, node_type_name):
        color = self.get_representation(node_type_name).get('color')
        if color != None:
            return ' #%s' % color
        else:
            return ''

    def generate_UML2_component_diagram(self, topology_template, with_relationships):
        self.generate('@startuml')
        self.generate('skinparam componentStyle uml2')
        if with_relationships:
            self.generate('skinparam component {')
            self.generate('  backgroundColor<<relationship>> White')
            self.generate('}')
        self.generate()

        substitution_mappings = topology_template.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            substitution_mappings_uml_id = SUBSTITUTION_MAPPINGS
            substitution_mappings_node_type = substitution_mappings.get(NODE_TYPE)
            merged_substitution_mappings_type = self.type_system.merge_node_type(substitution_mappings_node_type)
            for capability_name, capability_yaml in get_dict(merged_substitution_mappings_type, CAPABILITIES).items():
                capability_uml_id = substitution_mappings_uml_id + '_' + normalize_name(capability_name)
                # Declare an UML interface for the substitution_mappings capability.
                self.generate('interface "', capability_name, '" as ', capability_uml_id, sep='')
            self.generate('component ": ', substitution_mappings_node_type, '" <<node>> as ', substitution_mappings_uml_id,
                self.get_color(substitution_mappings_node_type), ' {', sep='')

        relationship_templates = get_dict(topology_template, RELATIONSHIP_TEMPLATES)

        already_generated_interfaces = {}

        # Iterate over all node templates.
        node_templates = get_dict(topology_template, NODE_TEMPLATES)
        for node_template_name, node_template_yaml in node_templates.items():
            node_template_type = node_template_yaml.get(TYPE)
            merged_node_template_type = self.type_system.merge_node_type(node_template_type)
            node_template_uml_id = 'node_' + normalize_name(node_template_name)
            # Declare an UML component for the node template.
            self.generate('component "', node_template_name, ': ', short_type_name(node_template_type), '" <<node>> as ', node_template_uml_id, self.get_color(node_template_type), sep='')
            # Iterate over all capabilities of the node template.
            for capability_name, capability_yaml in get_dict(merged_node_template_type, CAPABILITIES).items():
                if type(capability_yaml) == dict:
                    capability_occurrences = capability_yaml.get(OCCURRENCES)
                else:
                    capability_occurrences = None
                if with_relationships or (capability_occurrences and capability_occurrences[0] > 0):
                    capability_uml_id = node_template_uml_id + '_' + normalize_name(capability_name)
                    # Declare an UML interface for the node template capability.
                    self.generate('interface "', capability_name, '" as ', capability_uml_id, sep='')
                    # Connect the capability UML interface to the node template UML component.
                    self.generate(capability_uml_id, '--', node_template_uml_id)
                    already_generated_interfaces[capability_uml_id] = capability_uml_id
            if with_relationships:
                # Iterate over all requirements of the node template.
                index = 0
                for requirement in get_list(node_template_yaml, REQUIREMENTS):
                    for requirement_name, requirement_yaml in requirement.items():
                        requirement_uml_id = node_template_uml_id + '_' + normalize_name(requirement_name) + '_relationship' + str(index)
                        index = index + 1

                        requirement_node = get_requirement_node_template(requirement_yaml)
                        if requirement_node == None:
                            continue

                        relationship_component_name = '' # No name.
                        relationship_component_type = None

                        if type(requirement_yaml) == dict:
                            requirement_relationship = syntax.get_requirement_relationship(requirement_yaml)
                            if type(requirement_relationship) == dict:
                                relationship_component_type = syntax.get_relationship_type(requirement_relationship)
                            else:
                                relationship_template = relationship_templates.get(requirement_relationship)
                                if relationship_template:
                                    relationship_component_name = requirement_relationship
                                    relationship_component_type = relationship_template.get(TYPE)
                                else:
                                    relationship_component_type = requirement_relationship
                        if relationship_component_type == None:
                            requirement = get_dict(merged_node_template_type, REQUIREMENTS).get(requirement_name, {})
                            tmp = syntax.get_requirement_relationship(requirement)
                            relationship_component_type = syntax.get_relationship_type(tmp)
                        if relationship_component_type == None:
                            continue
                        # Declare an UML component for the node template requirement relationship.
                        self.generate('component "', relationship_component_name, ': ', short_type_name(relationship_component_type), '" <<relationship>> as ', requirement_uml_id, sep='')
                        # Declare an UML interface for the node template requirement relationship.
                        self.generate('interface " " as ', requirement_uml_id, '_source', sep='')
                        # Connect the UML interface to the relationship UML component.
                        self.generate(requirement_uml_id, '_source', ' -- ', requirement_uml_id, sep='')
                        # Connect the node template UML component to the relationship UML component.
                        self.generate(node_template_uml_id, ' --( ', requirement_uml_id, '_source', ' : ', requirement_name, sep='')
            self.generate()

        # Iterate over all node templates.
        for node_template_name, node_template_yaml in node_templates.items():
            node_template_uml_id = 'node_' + normalize_name(node_template_name)
            node_template_type = node_template_yaml.get(TYPE)
            merged_node_template_type = self.type_system.merge_node_type(node_template_type)
            # Iterate over all requirements of the node template.
            index = 0
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    source_uml_id = node_template_uml_id
                    if with_relationships:
                        source_uml_id = source_uml_id + '_' + normalize_name(requirement_name) + '_relationship' + str(index)
                    index = index + 1
                    requirement_node = get_requirement_node_template(requirement_yaml)
                    if requirement_node == None:
                        continue
                    requirement_node_template = node_templates.get(requirement_node)
                    if requirement_node_template == None:
                        continue
                    requirement_node_type_name = requirement_node_template.get(TYPE)
                    if requirement_node_type_name == None:
                        continue

                    requirement_capability = syntax.get_requirement_capability(get_dict(merged_node_template_type, REQUIREMENTS).get(requirement_name))
                    capability_found = False
                    for ( capability_name, capability_yaml ) in get_dict(self.type_system.merge_node_type(requirement_node_type_name), CAPABILITIES).items():
                        if self.type_system.is_derived_from(syntax.get_capability_type(capability_yaml), requirement_capability):
                            capability_found = True
                            break
                    if capability_found:
                        target_node_uml_id = 'node_' + normalize_name(requirement_node)
                        target_capability_uml_id = target_node_uml_id + '_' + normalize_name(capability_name)
                        if with_relationships:
                            self.generate(source_uml_id, ' --( ', target_capability_uml_id, sep='')
                        else:
                            if already_generated_interfaces.get(target_capability_uml_id) == None:
                                self.generate('interface "', capability_name, '" as ', target_capability_uml_id, sep='')
                                # Connect the capability UML interface to the node template UML component.
                                self.generate(target_capability_uml_id, '--', target_node_uml_id)
                                already_generated_interfaces[target_capability_uml_id] = target_capability_uml_id
                            self.generate(source_uml_id, ' "' + requirement_name + '" --( ', target_capability_uml_id, sep='')


        # generate UML representation for TOSCA policies
        for policy in topology_template.get(POLICIES, []):
            for policy_name, policy_yaml in policy.items():
                policy_type = policy_yaml.get(TYPE)
                policy_uml_id = 'policy_' + normalize_name(policy_name)
                self.generate('agent %s <<policy>> #AliceBlue [' % policy_uml_id)
                if policy_type in [ 'tosca.policies.nfv.VnfIndicator' ]:
                    self.generate(policy_name, ': ', short_type_name(policy_type), sep='')
                else:
                    self.generate(short_type_name(policy_type), sep='')
                self.generate('---')
                properties = policy_yaml.get('properties', {})
                if len(properties) > 0:
                    self.generate('.. properties ..')
                    for prop_name, prop_value in properties.items():
                        self.generate(prop_name, '=', self.stringify_value(prop_value))
                triggers = policy_yaml.get('triggers', {})
                if len(triggers) > 0:
                    self.generate('.. triggers ..')
                    for trigger_name, trigger in triggers.items():
                        filename = self.get_filename(self.tosca_service_template)
                        filename = filename[:filename.rfind('.')] + '-' + policy_name + '-' + trigger_name + '-sequence-diagram.svg'
                        self.generate('[[%s %s]]' % (filename, trigger_name))
                self.generate(']')
                for target in policy_yaml.get(TARGETS, []):
                    if node_templates.get(target) != None:
                        target_uml_id = 'node_' + normalize_name(target)
                        self.generate(policy_uml_id, ' -up-> ', target_uml_id, sep='')
                    else:
                        target_group = topology_template.get(GROUPS, {}).get(target)
                        if target_group is None:
                            self.error(target + " - undefined node template or group")
                            continue
                        for member in target_group.get(MEMBERS, []):
                            member_uml_id = 'node_' + normalize_name(member)
                            self.generate(policy_uml_id, ' -up-> ', member_uml_id, sep='')

        if substitution_mappings:
            capabilities = get_dict(substitution_mappings, CAPABILITIES)

            for capability_name, capability_yaml in get_dict(merged_substitution_mappings_type, CAPABILITIES).items():
                capability = capabilities.get(capability_name)
                if capability != None:
                    if type(capability) != list:
                        continue # TODO when capability is not a list
                    target_node_uml_id = 'node_' + normalize_name(capability[0])
                    target_uml_id = target_node_uml_id + '_' + normalize_name(capability[1])

                    if already_generated_interfaces.get(target_uml_id) == None:
                        self.generate('interface "', normalize_name(capability[1]), '" as ', target_uml_id, sep='')
                        # Connect the capability UML interface to the node template UML component.
                        self.generate(target_uml_id, '--', target_node_uml_id)
                        already_generated_interfaces[target_uml_id] = target_uml_id

            self.generate('}')

            for capability_name, capability_yaml in get_dict(merged_substitution_mappings_type, CAPABILITIES).items():
                capability_uml_id = substitution_mappings_uml_id + '_' + normalize_name(capability_name)
                # Connect the capability UML interface to the node template UML component.
                capability = capabilities.get(capability_name)
                if capability != None:
                    if type(capability) != list:
                        continue # TODO when capability is not a list
                    target_node_uml_id = 'node_' + normalize_name(capability[0])
                    target_uml_id = target_node_uml_id + '_' + normalize_name(capability[1])
                    self.generate(capability_uml_id, '--(', target_uml_id)
                else:
                    self.generate(capability_uml_id, '--', substitution_mappings_uml_id)

            index = 0
            requirements = syntax.get_substitution_mappings_requirements(substitution_mappings)
            for requirement_name, requirement_def in merged_substitution_mappings_type.get(REQUIREMENTS, {}).items():
                interface_uml_id = substitution_mappings_uml_id + '_' + normalize_name(requirement_name) + str(index)
                index = index + 1
                self.generate('interface "', requirement_name, '" as ', interface_uml_id)
                requirement_yaml = requirements.get(requirement_name)
                if requirement_yaml:
                    source_uml_id = 'node_' + normalize_name(requirement_yaml[0])
                    self.generate(source_uml_id, ' "' + requirement_yaml[1] + '" --( ', interface_uml_id, sep='')
                else:
                    self.generate(substitution_mappings_uml_id, ' --( ', interface_uml_id)

        self.generate('@enduml')

    def generate_UML2_deployment_diagram(self, topology_template):
        self.generate('@startuml')
        self.generate('skinparam componentStyle uml2')
        self.generate()

        node_templates = get_dict(topology_template, NODE_TEMPLATES)

        non_containeds = list(node_templates.keys())
        containers = {}
        contained_containers = []

        # Iterate over all node templates to find containers.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(node_template_yaml.get(TYPE))
            # Iterate over all capabilities of the node template type.
            for capability_name, capability_yaml in get_dict(merged_node_template_type, CAPABILITIES).items():
                capability_type = get_capability_type(capability_yaml)
                if self.type_system.is_derived_from(capability_type, 'tosca.capabilities.Container'):
                    containers[node_template_name] = containers.get(node_template_name, dict())
                    try:
                        non_containeds.remove(node_template_name)
                    except ValueError:
                        pass

        # Iterate over all node templates to find containeds.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(node_template_yaml.get(TYPE))
            # Iterate over all requirements of the node template.
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    requirement_definition = get_dict(merged_node_template_type, REQUIREMENTS).get(requirement_name)
                    requirement_relationship = syntax.get_requirement_relationship(requirement_definition)
                    requirement_relationship_type = syntax.get_relationship_type(requirement_relationship)
                    if self.type_system.is_derived_from(requirement_relationship_type, 'tosca.relationships.HostedOn'):
                        requirement_node = get_requirement_node_template(requirement_yaml)
                        if requirement_node != None:
                            try:
                                containers[requirement_node][node_template_name] = containers.get(node_template_name, dict())
                            except KeyError as e:
                                self.error(e)
                            contained_containers.append(node_template_name)
                            try:
                                non_containeds.remove(node_template_name)
                            except ValueError:
                                pass

        # TODO: Remove containers contained by other containers.
        for contained_container_name in contained_containers:
            if containers.get(contained_container_name) != None:
                del containers[contained_container_name]

        # Iterate over all containers.

        def get_uml2_kind(tosca_type):
            uml2_kind = 'component'
            for tt, kind in self.configuration.get(UML2, 'kinds').items():
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
                self.generate(uml2_kind, ' "', container_name, ': ', short_type_name(node_template_type), '" as node_', normalize_name(container_name), self.get_color(node_template_type), sep='')
            else:
                self.generate(uml2_kind, ' "', container_name, ': ', short_type_name(node_template_type), '" as node_', normalize_name(container_name), ' ', self.get_color(node_template_type), '{', sep='')
                for contained_name, contained_dict in containeds.items():
                    generate_container(self, contained_name, contained_dict)
                for artifact_name, artifact_yaml in node_template_artifacts.items():
                    artifact_type = syntax.get_artifact_type(artifact_yaml)
                    if artifact_type == None:
                        artifact_type = 'Artifact'
                    self.generate('artifact "', syntax.get_artifact_file(artifact_yaml), '" <<', artifact_type, '>> as node_', normalize_name(container_name), '_artifact_',  normalize_name(artifact_name) , sep='')
                self.generate('}')

        substitution_mappings = topology_template.get(SUBSTITUTION_MAPPINGS)
        if substitution_mappings:
            # Create components connected to the capabilities of the substitition mapping.
            for capability_name, capability_yaml in get_dict(substitution_mappings, CAPABILITIES).items():
                self.generate('component "a node" as substitution_mappings_capability_', normalize_name(capability_name), sep='')

            substitution_mappings_node_type = substitution_mappings.get(NODE_TYPE)
            self.generate(get_uml2_kind(substitution_mappings_node_type), ' ": ', substitution_mappings_node_type, '" as substitution_mappings', self.get_color(substitution_mappings_node_type), ' {', sep='')

        for container_name, containeds in containers.items():
            generate_container(self, container_name, containeds)

        for node_template_name in non_containeds:
            generate_container(self, node_template_name, {})

        relationship_templates = get_dict(topology_template, RELATIONSHIP_TEMPLATES)

        # Iterate over all node templates to draw relationships.
        for node_template_name, node_template_yaml in node_templates.items():
            merged_node_template_type = self.type_system.merge_node_type(node_template_yaml.get(TYPE))
            # Iterate over all requirements of the node template.
            for requirement in get_list(node_template_yaml, REQUIREMENTS):
                for requirement_name, requirement_yaml in requirement.items():
                    requirement_relationship_type = None
                    if type(requirement_yaml) == dict:
                        requirement_relationship = syntax.get_requirement_relationship(requirement_yaml)
                        if type(requirement_relationship) == dict:
                            requirement_relationship_type = syntax.get_relationship_type(requirement_relationship)
                        else:
                            relationship_template = relationship_templates.get(requirement_relationship)
                            if relationship_template:
                                requirement_relationship_type = relationship_template.get(TYPE)
                            else:
                                requirement_relationship_type = requirement_relationship
                    if requirement_relationship_type == None:
                        requirement = get_dict(merged_node_template_type, REQUIREMENTS).get(requirement_name, {})
                        tmp = syntax.get_requirement_relationship(requirement)
                        requirement_relationship_type = syntax.get_relationship_type(tmp)
                    if requirement_relationship_type == None:
                        continue

                    if not self.type_system.is_derived_from(requirement_relationship_type, 'tosca.relationships.HostedOn'):
                        requirement_node = get_requirement_node_template(requirement_yaml)
                        if requirement_node:
                            direction = self.configuration.get(UML2, 'direction').get(requirement_relationship_type, '')
                            self.generate('node_', normalize_name(node_template_name), ' "', requirement_name, '" .' + direction + '.> node_', normalize_name(requirement_node), ' : <<', short_type_name(requirement_relationship_type), '>>', sep='')

        if substitution_mappings:
            self.generate('}')
            # Connect created components to the nodes exported by the capabilities of the substitition mapping.
            for capability_name, capability_yaml in get_dict(substitution_mappings, CAPABILITIES).items():
                if type(capability_yaml) != list:
                    continue # TODO
                target_node_name = capability_yaml[0]
                target_capability_name = capability_yaml[1]
                self.generate('substitution_mappings_capability_', normalize_name(capability_name), ' "', capability_name, '" ..> node_', normalize_name(target_node_name), sep='')

            merged_substitution_mappings_node_type = self.type_system.merge_node_type(substitution_mappings_node_type)
            # Get all requirements of the node type of the substitution mapping.
            all_requirement_declarations = get_dict(merged_substitution_mappings_node_type, REQUIREMENTS)
            req_idx = 0
            # Iterate over all requirements of the substitution mapping.
            for requirement_name, requirement_yaml in syntax.get_substitution_mappings_requirements(substitution_mappings).items():
                requirement_capability = syntax.get_requirement_capability(all_requirement_declarations.get(requirement_name))
                if requirement_capability == None:
                    continue
                self.generate(get_uml2_kind(requirement_capability), ' ": ', short_type_name(requirement_capability),'" as substitution_mappings_requirement_', req_idx, sep='')
                requirement_node = requirement_yaml[0]
                requirement_node_capability = requirement_yaml[1]
                self.generate('node_', normalize_name(requirement_node), ' "', normalize_name(requirement_node_capability), '" ..> "', requirement_name, '" substitution_mappings_requirement_', req_idx, sep='')
                req_idx = req_idx + 1

        self.generate('@enduml')

    def generate_UML2_workflow_diagrams(self, topology_template):

        # get the workflows
        workflows = topology_template.get('workflows', {})

        def generate_workflow_diagram(workflow_name, workflow_definition):

            def step_id(step_name):
                return 'step_%s_%s' \
                    % (normalize_name(workflow_name), \
                       normalize_name(step_name))

            # generate all steps of the current workflow
            steps = workflow_definition.get('steps', {})
            for step_name, step_definition in steps.items():
                # generate a PlantUML state for each step
                self.generate('state "%s" as %s << step >> {' % (step_name, step_id(step_name)))
                # get the target of the current step
                target = step_definition['target']
                step_activity_id = step_id(step_name) + '_' + normalize_name(target)
                target_relationship = step_definition.get('target_relationship')
                if target_relationship is None:
                    target_label = target
                else:
                    step_activity_id += '_' + normalize_name(target_relationship)
                    target_label = target + ' ' + normalize_name(target_relationship)
                # store ids of all activities of the current step
                activity_ids = []
                # generate all activities of the current step
                for activity in step_definition['activities']:
                    for key, value in activity.items():
                        # generate an id of the current activity
                        activity_id = '%s_%s' % (step_activity_id, value)
                        activity_ids.append(activity_id)
                        if key == 'inline':
                            # generate a step encapsulating the inlined workflow
                            self.generate('  state "%s" as %s << %s >> {' % (value, activity_id, key))
                            generate_workflow_diagram(value, workflows.get(value))
                            self.generate('  }')
                        else:
                            # generate a PlantUML state for each activity
                            self.generate('  state "%s %s" as %s << %s >>' % (target_label, value, activity_id, key))
                if len(activity_ids) > 0:
                    # links consecutive activities
                    previous_activity_id = activity_ids[0]
                    for next_activity_id in activity_ids[1:]:
                        self.generate('  %s --> %s' % (previous_activity_id, next_activity_id))
                        previous_activity_id = next_activity_id
                # close the step
                self.generate('}')

            # compute the number of predecessors of each step
            nb_predecessors = { step_name: 0 for step_name in steps.keys() }
            for step_name, step_definition in steps.items():
                for next_step in step_definition.get('on_success', []):
                    nb_predecessors[next_step] += 1

            # generate a join for each step having multiple predecessors
            for step_name in steps.keys():
                if nb_predecessors[step_name] > 1:
                    sid = step_id(step_name)
                    self.generate('  state %s_join <<join>>' % sid)
                    self.generate('  %s_join --> %s' % (sid, sid))

            # links the steps
            initial_step_names = list(steps.keys())
            final_step_names = []
            for step_name, step_definition in steps.items():
                on_success = step_definition.get('on_success')
                if on_success is None or len(on_success) == 0:
                    # the current step is a final step
                    final_step_names.append(step_name)
                else:
                    # link the current step to each on_success step
                    nb_successors = len(on_success)
                    if nb_successors == 1:
                        state_source_id = step_id(step_name)
                    elif nb_successors > 1:
                        # generate a fork
                        state_source_id = '%s_fork' % step_id(step_name)
                        self.generate('state %s <<fork>>' % state_source_id)
                        self.generate('%s --> %s' % (step_id(step_name), state_source_id))
                    for next_step in on_success:
                        target_step_id = step_id(next_step)
                        if nb_predecessors[next_step] > 1:
                            target_step_id += '_join'
                        self.generate('%s --> %s' % (state_source_id, target_step_id))
                        # next_step is not an initial step
                        try:
                            initial_step_names.remove(next_step)
                        except ValueError:
                            pass # next_step was already removed from initial_step_names
                # link the current step to each on_failure step
                for next_step in step_definition.get('on_failure', []):
                    self.generate('%s -right[#red]-> %s : <color:red>on_failure</color>' % (step_id(step_name), step_id(next_step)))
                    # next_step is not an initial step
                    try:
                        initial_step_names.remove(next_step)
                    except ValueError:
                        pass # next_step was already removed from initial_step_names

            # link all initial steps
            nb_initial_steps = len(initial_step_names)
            if nb_initial_steps == 0:
                self.error('topology_template:workflows:%s - no initial state' % workflow_name)
            elif nb_initial_steps == 1:
                initial_state = '[*]'
            else: # > 1
                # generate a fork
                initial_state = '%s_fork' % workflow_name
                self.generate('state %s <<fork>>' % initial_state)
                self.generate('[*] --> %s' % initial_state)
            for step_name in initial_step_names:
                self.generate('%s --> %s' % (initial_state, step_id(step_name)))

            # link all final steps
            nb_final_steps = len(final_step_names)
            if nb_final_steps == 0:
                self.error('topology_template:workflows:%s - no final state' % workflow_name)
            elif nb_final_steps == 1:
                final_state = '[*]'
            else: # > 1
                # generate a join
                final_state = '%s_join' % workflow_name
                self.generate('state %s <<join>>' % final_state)
                self.generate('%s --> [*]' % final_state)
            for step_name in final_step_names:
                self.generate('%s --> %s' % (step_id(step_name), final_state))

        # iterate over all workflows
        for workflow_name, workflow_definition in workflows.items():
            # open a file for each workflow
            self.open_file('-%s-workflow-diagram.plantuml' % workflow_name)
            self.generate('@startuml')
            # generate PlantUML configuration
            self.generate('hide empty description')
            self.generate('skinparam shadowing false')
            self.generate('skinparam state {')
            self.generate('  ArrowColor blue')
            self.generate('  BorderColor blue')
            self.generate('  EndColor black')
            self.generate('  StartColor green')
            self.generate('  BackGroundColor<< step >> white')
            self.generate('  BorderColor<< step >> black')
            self.generate('  BackGroundColor<< delegate >> lightgrey')
            self.generate('  BackGroundColor<< set_state >> white')
            self.generate('  BackGroundColor<< call_operation >> lightblue')
            self.generate('  BackGroundColor<< inline >> white')
            self.generate('}')
            self.generate()

            generate_workflow_diagram(workflow_name, workflow_definition)

            # close the current workflow diagram
            self.generate('@enduml')
            self.close_file()

    def generate_UML2_sequence_diagrams(self, topology_template):

        def generate_sequence_diagram(policy_name, policy, trigger_name, trigger):
            # open a file for each policy trigger
            self.open_file('-%s-%s-sequence-diagram.plantuml' % (policy_name, trigger_name))
            self.generate('@startuml')

            self.generate('participant "%s\\n%s" as policy_trigger <<policy>>' % (policy_name, trigger_name))
            for target in policy.get('targets', []):
                if topology_template.get('node_templates', {}).get(target) != None:
                    stereotype = ' <<node>>'
                elif topology_template.get('groups', {}).get(target) != None:
                    stereotype = ' <<group>>'
                else:
                    stereotype = ''
#TODO                self.generate('participant "%s" as target_%s' % (target, normalize_name(target)))
                self.generate('participant "%s" as target%s' % (target, stereotype))

            self.generate('?-> policy_trigger : %s' % trigger.get('event'))
            self.generate('activate policy_trigger')
            condition = trigger.get('condition')
            if condition != None:
                self.generate('note over policy_trigger, target : **condition**:\\n%s'
                    % self.yamlify_value(condition, '   ', '   ')
                )

            for action in trigger.get('action', []):
                for activity_name, parameters in action.items():
                    if activity_name == 'call_operation':
                        target_participant = 'target'
                        if isinstance(parameters, dict):
                            message = parameters.get('operation')
                            message += '('
                            sep = ''
                            for input_name, input_value in parameters.get('inputs', {}).items():
                                message += sep
                                message += input_name
                                message += '='
                                if isinstance(input_value, dict):
                                    value = input_value.get('value')
                                    if value != None:
                                        input_value = value
                                message += self.stringify_value(input_value)
                                sep = ', '
                            message += ')'
                        else:
                            message = '%s()' % parameters
                    elif activity_name == 'set_state':
                        target_participant = 'target'
                        message = 'set_state: %s' % parameters
                    elif activity_name == 'delegate':
                        target_participant = 'target'
                        message = 'delegate: %s' % parameters
                    elif activity_name == 'inline':
                        target_participant = 'orchestrator'
                        message = 'inline: %s' % parameters
                    else:
                        target_participant = 'UNKNOWN'
                        message = 'UNKNOWN ACTIVITY'
                    self.generate('policy_trigger -> %s : %s' % (target_participant, message))
                    self.generate('activate %s' % target_participant)
                    self.generate('%s --> policy_trigger' % target_participant)
                    self.generate('deactivate %s' % target_participant)

            self.generate('deactivate policy_trigger')

            # close the current sequence diagram
            self.generate('@enduml')
            self.close_file()

        # iterate over all policies
        for policy in topology_template.get('policies', []):
            for policy_name, policy in policy.items():
                for trigger_name, trigger in policy.get('triggers', {}).items():
                    if trigger.get('action') != None:
                        generate_sequence_diagram(policy_name, policy, trigger_name, trigger)

    def stringify_value(self, value):
        if not isinstance(value, (str, int, float)):
            return '[[{' + self.yamlify_value(value) + '} ...]]'
        else:
            return repr(value)

    def yamlify_value(self, value, header='', ident=''):
        result = ''
        if isinstance(value, dict):
            tmp = header
            for k, v in value.items():
                result += tmp + str(k) + ': ' + self.yamlify_value(v, '\\n' + ident + '  ', ident + '  ')
                tmp = '\\n' + ident
        elif isinstance(value, list):
            tmp = header
            for v in value:
                result += tmp + '- ' + self.yamlify_value(v, '', ident + '  ')
                tmp = '\\n' + ident
        else:
            result = repr(value)
        return result
