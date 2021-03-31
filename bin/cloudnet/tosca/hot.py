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

from cloudnet.tosca.processors import Generator
from cloudnet.tosca.syntax import * # TODO remove later
import cloudnet.tosca.syntax as syntax
from cloudnet.tosca.utils import split_scalar_unit

#
# Default configuration of this generator.
#

import cloudnet.tosca.configuration as configuration
HOT = 'HOT'
HEAT_TEMPLATE_VERSION = 'heat_template_version'
configuration.DEFAULT_CONFIGURATION[HOT] = {
    # Target directory where HOT templates are generated.
    Generator.TARGET_DIRECTORY: 'hot',
    # The Heat template version used into generated HOT templates.
    HEAT_TEMPLATE_VERSION: 'queens',
#   HEAT_TEMPLATE_VERSION: 'rocky',
    # Is OpenStack Neutron QoS extension available.
    'OS::Neutron::QoS.available': True,
    # Default OS::Neutron::Subnet CIDRs.
    'OS::Neutron::Subnet.cidr.ipv4': '10.100.%d.0/24',
    'OS::Neutron::Subnet.cidr.ipv6': '2001:db8:%d::0/120',
    # Is OS::Glance::Image can be created.
    'OS::Glance::Image.available': False,
    # Default OS::Nova::Server image.
    'OS::Nova::Server.image.default': 'cirros-0.3.5-x86_64-disk',
    # Maximum OS::Nova::Flavor ram.
    'OS::Nova::Flavor.ram.maximum': 2000,
}
configuration.DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

FLAVOUR_ID = 'flavour_id'

class HOTGenerator(Generator):
    '''
        This is the generator for Heat OpenStack Template (HOT).
    '''

    def generator_configuration_id(self):
        return HOT

    def get_flavour_id(self, node_yaml, node_type):
        flavour_id = get_dict(node_yaml, PROPERTIES).get(FLAVOUR_ID)
        if flavour_id == None:
            node_declaration = self.type_system.get_type(node_type)
            property_flavour_id = get_dict(node_declaration, PROPERTIES).get(FLAVOUR_ID)
            if property_flavour_id:
                flavour_id = property_flavour_id.get(DEFAULT)
        return flavour_id

    def generation(self):
        self.info('HOT generation')

        # TODO: Document next line.
        self.subnet_cidr_idx = 0

        template_yaml = self.tosca_service_template.get_yaml()
        is_etsi_nfv_sol001_template = False
        for an_import in syntax.get_imports(template_yaml):
            if syntax.get_import_file(an_import).startswith('etsi_nfv_sol001_'):
                is_etsi_nfv_sol001_template = True
        topology_template = template_yaml.get(TOPOLOGY_TEMPLATE)
        # Generate HOT only for ETSI NFV SOL 001 NSD/VNFD/PNFD topology template.
        if is_etsi_nfv_sol001_template == False or topology_template == None:
            return

        # Compute the substitution mappings.
        self.substitution_mappings = {}

        # Iterate over imported files.
        for imported_file in get_list(template_yaml, IMPORTS):
            imported_file_yaml = self.tosca_service_template.imports(imported_file).get_yaml()
            substitution_mappings = get_dict(get_dict(imported_file_yaml, TOPOLOGY_TEMPLATE), SUBSTITUTION_MAPPINGS)
            node_type = substitution_mappings.get(NODE_TYPE)
            if node_type:
                flavour_id = self.get_flavour_id(substitution_mappings, node_type)
                mapping_flavour_file = self.substitution_mappings.get(node_type)
                if mapping_flavour_file == None:
                    mapping_flavour_file = {}
                    self.substitution_mappings[node_type] = mapping_flavour_file
                file_of_flavour_id = mapping_flavour_file.get(flavour_id)
                if file_of_flavour_id:
                    self.warning(' HOT - flavour_id ' + flavour_id + ' for type ' + node_type + ' defined in both ' + file_of_flavour_id + ' and ' + imported_file)
                else:
                    mapping_flavour_file[flavour_id] = imported_file

        # Open generated HOT template.
        self.open_file(None)

        # Generate heat_template_version:
        self.generate(HEAT_TEMPLATE_VERSION, ': ', self.configuration.get(HOT, HEAT_TEMPLATE_VERSION), sep='')

        # Generate description:
        description = template_yaml.get(DESCRIPTION)
        if description:
            self.generate()
            self.generate('description:', description)

        INPUT_TYPES_HOT_TYPES = {
             'string':  'string',
             'integer': 'number',
             'boolean':  'boolean',
             'list':    'comma_delimited_list',
             'map':     'json',
        }

        def generate_parameter(input_name, input_yaml, default_value):
            self.generate('  ', input_name, ':', sep='')
            # Generate parameter type.
            input_type = input_yaml.get(TYPE)
            if input_type:
                parameter_type = INPUT_TYPES_HOT_TYPES.get(input_type, 'json')
                self.generate('    type:', parameter_type)
            # Generate parameter label.
            self.generate('    label:', input_name.replace('_', ' ').title())
            # Generate parameter description.
            input_description = input_yaml.get(DESCRIPTION)
            if input_description:
                self.generate('    description:', input_description)
            # Generate parameter default.
            if default_value:
                self.generate('    default:', default_value)
            else:
                input_default = input_yaml.get(DEFAULT)
                if input_default:
                    self.generate('    default:', input_default)
            # Property 'hidden' is set to false by default.
            self.generate('#   hidden: false')
            # Generate parameter constraints.
            input_constraints = get_list(input_yaml, CONSTRAINTS)
            if len(input_constraints) or default_value:
                self.generate('    constraints:')
                if default_value:
                    self.generate("      - allowed_values: [ '", default_value, "' ]", sep='')
                else:
                    for constraint in input_constraints:
                        for constraint_name, constraint_value in constraint.items():
                            if constraint_name == 'valid_values':
                                constraint_name = 'allowed_values'
                            elif constraint_name == 'equal':
                                constraint_name = 'allowed_values'
                                constraint_value = [ constraint_value ]
                            self.generate('      - ', constraint_name, ': ', constraint_value, sep='')
            # Property 'immutable' is set to false by default.
            self.generate('#   immutable: false')
            # Property 'tags' with default value.
            self.generate('#   tags: []')

        # Generate parameters:
        inputs = get_dict(topology_template, INPUTS)
        substitution_mappings = topology_template.get(SUBSTITUTION_MAPPINGS, {})
        substitution_mappings_requirements = syntax.get_substitution_mappings_requirements(substitution_mappings)
        if len(inputs) or len(substitution_mappings_requirements):

            substitution_mappings_node_type = substitution_mappings.get(NODE_TYPE)
            if substitution_mappings_node_type != None:
                substitution_mappings_merged_node_type = self.type_system.merge_type(substitution_mappings_node_type)
            else:
                substitution_mappings_merged_node_type = {}
            substitution_mappings_properties = get_dict(substitution_mappings, PROPERTIES)

            generated_parameters = {}

            self.generate()
            self.generate('parameters:')
            for input_name, input_yaml in inputs.items():
                if generated_parameters.get(input_name) == None:
                    generate_parameter(input_name, input_yaml, None)
                    generated_parameters[input_name] = True

            for property_name, property_yaml in get_dict(substitution_mappings_merged_node_type, PROPERTIES).items():
                if is_property_required(property_yaml):
                    if generated_parameters.get(property_name) == None:
                        generate_parameter(property_name, property_yaml, substitution_mappings_properties.get(property_name))
                        generated_parameters[property_name] = True

            if substitution_mappings_node_type:
                node_type_requirements = substitution_mappings_merged_node_type.get(REQUIREMENTS)
            else:
                node_type_requirements = {}

            for requirement_name, requirement_value in substitution_mappings_requirements.items():
                    if generated_parameters.get(requirement_name) == None:
                        requirement_definition = node_type_requirements.get(requirement_name)
                        self.generate('  ', requirement_name, ':', sep='')
                        # Generate parameter type.
                        self.generate('    type: string')
                        # Generate parameter label.
                        self.generate('    label:', requirement_name.replace('_', ' ').title())
                        # Generate parameter description.
                        description = requirement_definition.get(DESCRIPTION)
                        if description != None:
                            self.generate('    description:', description)
                        # No parameter default value.
                        # Property 'hidden' is set to false by default.
                        self.generate('#   hidden: false')
                        # TODO: add a constraint related to other capability types.
                        capability = requirement_definition.get(CAPABILITY)
                        if capability == 'tosca.capabilities.nfv.VirtualLinkable':
                            custom_constraint = 'neutron.network'
                        else:
                            custom_constraint = None
                        if custom_constraint:
                            self.generate('    constraints:')
                            self.generate('      - custom_constraint:', custom_constraint)
                        # Property 'immutable' is set to false by default.
                        self.generate('#   immutable: false')
                        # Property 'tags' with default value.
                        self.generate('#   tags: []')
                        generated_parameters[requirement_name] = True

        # Generate resources:
        node_templates = get_dict(topology_template, NODE_TEMPLATES)
        groups = get_dict(topology_template, GROUPS)
        policies = topology_template.get(POLICIES, [])
        if len(node_templates) or len(groups) or len(policies):
            self.generate()
            self.generate('resources:')

            def call_generate(self, entity_name, entity_type, entity_yaml):
                for tosca_type, generate_function in HOTGenerator.GENERATE_NODES.items():
                    if self.type_system.is_derived_from(entity_type, tosca_type):
                        generate_function(self, entity_name, entity_yaml)
                        return
                # If no generate_function found call generate_undefined_node
                HOTGenerator.generate_undefined_node(self, entity_name, entity_yaml)

            for node_name, node_yaml in node_templates.items():
                node_type = node_yaml.get(TYPE)
                self.generate('  #')
                self.generate("  # Node '", node_name, "' of type '", node_type, "' translated into the following resource(s):", sep='')
                self.generate('  #')
                call_generate(self, node_name, node_type, node_yaml)
                self.generate()
            for group_name, group_yaml in groups.items():
                group_type = group_yaml.get(TYPE)
                self.generate('  #')
                self.generate("  # Group '", group_name, "' of type '", group_type, "' translated into the following resource(s):", sep='')
                self.generate('  #')
                call_generate(self, group_name, group_type, group_yaml)
                self.generate()
            for policy in policies:
                for policy_name, policy_yaml in policy.items():
                    policy_type = policy_yaml.get(TYPE)
                    self.generate('  #')
                    self.generate("  # Policy '",  policy_name, "' of type '", policy_type, "' translated into the following resource(s):", sep='')
                    self.generate('  #')
                    call_generate(self, policy_name, policy_type, policy_yaml)
                    self.generate()

        self.close_file()

    def generate_resource(self, resource_name, resource_type):
        self.generate()
        self.generate('  ', resource_name, ':', sep='')
        self.generate('    type:', resource_type)

    def generate_OS_Heat_None(self, entity_name, entity_yaml):
        #
        # Generate an OS::Heat::None resource.
        #
        self.generate_resource(entity_name, 'OS::Heat::None')
        #
        # Generate properties of this resource.
        #
        entity_properties = get_dict(entity_yaml, PROPERTIES)
        if len(entity_properties) > 0:
            self.generate('    properties:')
        for property_name, property_value in entity_properties.items():
            self.generate('      ', property_name, ': ', property_value, sep='')
        #
        # Generate metadata of this resource.
        #
        self.generate('    metadata:')
        entity_type = entity_yaml.get(TYPE)
        self.generate('      tosca.type:', entity_type)
        #
        # Generate dependencies of this resource.
        #
        requirements = entity_yaml.get(REQUIREMENTS)
        if requirements:
            self.generate('    depends_on:')
            for requirement in requirements:
                for requirement_name, requirement_value in requirement.items():
                    if requirement_value != None:
                        self.generate('      -', requirement_value)

    def generate_hot_template_ressource(self, entity_name, entity_yaml):
        entity_type = entity_yaml.get(TYPE)
        flavour_id = self.get_flavour_id(entity_yaml, entity_type)
        if type(flavour_id) == str:
            template_file = self.substitution_mappings.get(entity_type, {}).get(flavour_id)
            if template_file != None:
                #
                # Generate a templated resource.
                #
                self.generate_resource(entity_name, template_file)
                #
                # Generate properties of this resource.
                #
                entity_type_properties = get_dict(self.type_system.merge_type(entity_type), PROPERTIES)
                if len(entity_type_properties) > 0:
                    self.generate('    properties:')
                for property_name, property_value in get_dict(entity_yaml, PROPERTIES).items():
                    property_type = entity_type_properties.get(property_name).get(TYPE)
                    property_value_type = type(property_value)
                    if property_type == 'string' and property_value_type == float:
                        # Quote the float value to be sure that Heat will be seen it as a string (not a float).
                        self.generate('      ', property_name, ": '", property_value, "'", sep='')
                    else:
                        self.generate('      ', property_name, ': ', property_value, sep='')
                #
                # Generate dependencies of this resource.
                #
                for requirement in get_list(entity_yaml, REQUIREMENTS):
                    for requirement_name, requirement_value in requirement.items():
                        if requirement_value != None:
                            self.generate('      ', requirement_name, ': { get_resource: ', requirement_value, ' }', sep='')
                #
                # Generate metadata of this resource.
                #
                self.generate('    metadata:')
                entity_type = entity_yaml.get(TYPE)
                self.generate('      tosca.type:', entity_type)
                return
        # else
        self.generate_OS_Heat_None(entity_name, entity_yaml)

    def generate_todo_translate(self, properties, property_name):
        if type(properties) != dict:
            return
        property_value = properties.get(property_name)
        if property_value:
            self.generate('      # TODO: Translate ', property_name, ': ', property_value, sep='')

    def sizeInMB(self, scalar_size):
        size, unit = split_scalar_unit(scalar_size)

        if unit == 'MB':
           return size
        if unit == 'MiB':
           return int(size/1.024)
        if unit == 'GB':
            return size*1000
        else:
            self.error('Do not know how to convert ' + scalar_size + ' to MB')
            return '1 # TODO: ' + scalar_size

    def sizeInGB(self, scalar_size):
        size, unit = split_scalar_unit(scalar_size)
        if unit == 'GB':
           return size
        else:
            self.error('Do not know how to convert ' + scalar_size + ' to GB')
            return '1 # TODO: ' + scalar_size

    def generate_NS(self, ns_name, ns_yaml):
        self.generate_hot_template_ressource(ns_name, ns_yaml)

    def generate_OS_Neutron_Port(self, port_id, virtual_link_name, layer_protocol, port_role):
        #
        # Generate an OS::Neutron::Port resource for the virtual link.
        #
        self.generate_resource(port_id, 'OS::Neutron::Port')
        #
        # Generate properties of the OS::Neutron::Port resource.
        #
        self.generate('    properties:')
        # Set required property 'network'.
        self.generate('      network: { get_resource: ', virtual_link_name, ' }', sep='')
        # Nothing to do for property 'admin_state_up' as set to true by default.
        self.generate('#     admin_state_up: true  # default value')
        # TODO: Could property 'allowed_address_pairs' be set?
        self.generate('#     allowed_address_pairs: []  # default value')
        # TODO: Could property 'binding:vnic_type' be set?
        self.generate('#     binding:vnic_type: normal # TODO')
        # TODO: Could property 'device_id' be set?
        self.generate('#     device_id: "" # default value')
        # TODO: Could property 'device_owner' be set?
        self.generate('#     device_owner: "" # default value')
        # TODO: Could property 'dns_name' be set?
        self.generate('#     dns_name: "" # TODO')
        # Set property 'fixed_ips' with the layer_protocol subnet of the virtual link.
        self.generate('      fixed_ips:')
        self.generate('        - subnet: { get_resource: ', virtual_link_name, '_subnet_' + layer_protocol, ' }', sep='')
        # TODO: Could property 'mac_address' be set?
        self.generate('#     mac_address: MAC_ADDRESS')
        # Property 'name' is not set as it sets by Heat engine.
        self.generate('#     name: # set by Heat Engine')
        # TODO: Could property 'port_security_enabled' be set?
        self.generate('#     port_security_enabled: true # default value')
        # Set property 'qos_policy' according to role.
        if port_role in [ 'root', 'leaf' ]:
            self.generate('      qos_policy: { get_resource: ', virtual_link_name, '_' + port_role + '_qos_policy }', sep='')
        else:
            self.generate('#     qos_policy: QOS_POLICY_ID_OR_NAME')
        # TODO: Could property 'security_groups' be set?
        self.generate('#     security_groups: [ SECURITY_GROUP ]')
        # TODO: Could property 'tags' be set?
        self.generate('#     tags: [] # default value')
        # TODO: Could property 'value_specs' be set?
        self.generate('#     value_specs: {} # default value')

    def generate_router(self, router_name, router_yaml):
        router_type = router_yaml.get(TYPE)
        router_properties = get_dict(router_yaml, PROPERTIES)

        dependencies = []
        internal_virtual_link = None
        external_virtual_link = None
        external_virtual_link_as_param = False
        for requirement in router_yaml.get(REQUIREMENTS, []):
            for requirement_name, requirement_value in requirement.items():
                if requirement_name == 'internal_virtual_link':
                    if requirement_value:
                        internal_virtual_link = requirement_value
                elif requirement_name == 'external_virtual_link':
                    if requirement_value:
                        external_virtual_link = requirement_value
                elif requirement_name == 'dependency':
                    dependency.append(requirement_value)
                else:
                    self.error(' HOT - requirement "', requirement_name, '" not supported')

        if external_virtual_link == None:
            for requirement_name, requirement_value in syntax.get_substitution_mappings_requirements(self.tosca_service_template.get_yaml().get(TOPOLOGY_TEMPLATE).get(SUBSTITUTION_MAPPINGS, {})).items():
                if type(requirement_value) == list and len(requirement_value) == 2 and requirement_value[0] != None and requirement_value[0] == router_name and requirement_value[1] == 'external_virtual_link':
                    external_virtual_link =  requirement_name
                    external_virtual_link_as_param = True

        #
        # Generate an OS::Neutron::Router resource.
        #
        self.generate_resource(router_name, 'OS::Neutron::Router')
        #
        # Generate properties of the OS::Neutron::Router resource.
        #
        self.generate('#   properties:')
        # Nothing to do for property 'admin_state_up' as set to true by default.
        self.generate('#     admin_state_up: true # default value')
        # TODO: Could property 'distributed' be set?
        self.generate('#     distributed: false # default value?')
        # No need to deal with property 'external_gateway_info'
        # TODO: Could property 'ha' be set?
        self.generate('#     ha: false# default value?')
        # TODO: Could property 'l3_agent_ids' be set?
        self.generate('#     l3_agent_ids: [] # default value')
        # Property 'name' is not set as it sets by Heat engine.
        self.generate('#     name:', router_name, ' # set by Heat engine')
        # TODO: Could property 'tags' be set?
        self.generate('#     tags: [] # default value')
        # TODO: Could property 'value_specs' be set?
        self.generate('#     value_specs: {} # default value')
        #
        # Generate metadata of the OS::Neutron::Router resource.
        #
        self.generate('    metadata:')
        # Store the TOSCA type as a metadata of the resource.
        self.generate('      tosca.type:', router_type)
        # Store property 'layer_protocols' as metadata of the resource.
        router_layer_protocols = router_properties.get('layer_protocols')
        self.generate('      layer_protocols: ', router_layer_protocols, sep='')
        # Store property 'role' as metadata of the resource.
        router_role = router_properties.get('role')
        if router_role != None:
            self.generate('      role: ', router_role, sep='')
        # Store property 'description' as metadata of the resource.
        router_description = router_properties.get('description')
        if router_description != None:
            self.generate('      description: ', router_description, sep='')
        # Store property 'protocol' as metadata of the resource.
        router_protocol = router_properties.get('protocol')
        if router_protocol != None:
            self.generate('      protocol: ', router_protocol, sep='')
        # Store property 'trunk_mode' as metadata of the resource.
        router_trunk_mode = router_properties.get('trunk_mode')
        if router_trunk_mode != None:
            self.generate('      trunk_mode: ', str(router_trunk_mode).lower(), sep='')

        # Generate dependencies to other resources.
        if dependencies:
            self.generate('    depends_on:')
            for dependency in dependencies:
                self.generate('      -', dependency)

        def generate_router_interface(layer_protocol, virtual_link_label, virtual_link_name):
            self.generate_OS_Neutron_Port(router_name + '_' + virtual_link_label + '_' + layer_protocol + '_port', virtual_link_name, layer_protocol, router_role)

            #
            # Generate an OS::Neutron::RouterInterface resource for the virtual link.
            #
            self.generate_resource(router_name + '_' + virtual_link_label + '_' + layer_protocol, 'OS::Neutron::RouterInterface')
            #
            # Generate properties of the OS::Neutron::RouterInterface resource.
            #
            self.generate('    properties:')
            self.generate('      router: { get_resource: ', router_name, ' }', sep='')
            self.generate('      port: { get_resource: ', router_name + '_', virtual_link_label, '_', layer_protocol, '_port', ' }', sep='')

        if router_layer_protocols != None:
            for layer_protocol in router_layer_protocols:
                if not layer_protocol in ['ipv4', 'ipv6' ]:
                    self.error(" HOT - layer protocol '" + layer_protocol + "' is not supported")
                    continue
                generate_router_interface(layer_protocol, 'internal_virtual_link', internal_virtual_link)

                if not external_virtual_link_as_param:
                        generate_router_interface(layer_protocol, 'external_virtual_link', external_virtual_link)

        if external_virtual_link_as_param:
            #
            # Generate an OS::Neutron::Port resource for the external virtual link.
            #
            self.generate_resource(router_name + '_external_virtual_link_port', 'OS::Neutron::Port')
            #
            # Generate properties of the OS::Neutron::Port resource.
            #
            self.generate('    properties:')
            self.generate('      network: { get_param: ', external_virtual_link, ' }', sep='')

            #
            # Generate an OS::Neutron::RouterInterface resource for the virtual link.
            #
            self.generate_resource(router_name + '_external_virtual_link', 'OS::Neutron::RouterInterface')
            #
            # Generate properties of the OS::Neutron::RouterInterface resource.
            #
            self.generate('    properties:')
            self.generate('      router: { get_resource: ', router_name, ' }', sep='')
            self.generate('      port: { get_resource: ', router_name + '_external_virtual_link_port', ' }', sep='')

    def generate_Sap(self, sap_name, sap_yaml):
        self.generate_router(sap_name, sap_yaml)

    def generate_network(self, network_name, network_yaml):
        network_type = network_yaml.get(TYPE)
        network_properties = get_dict(network_yaml, PROPERTIES)

        #
        # Generate an OS::Neutron::Net resource.
        #
        self.generate_resource(network_name, 'OS::Neutron::Net')
        #
        # Generate properties of the OS::Neutron::Net resource.
        #
        self.generate('    properties:')
        # Nothing to do for property 'admin_state_up' as set to true by default.
        self.generate('#     admin_state_up: true # default value')
        # TODO: Could property 'dhcp_agent_ids' be set?
        self.generate('#     dhcp_agent_ids: [] # default value')
        # Set property 'dns_domain' if needed.
        dns_domain_not_set = True
        for protocol_data in network_properties.get('vl_profile', {}).get('virtual_link_protocol_data', []):
            dns_domain = protocol_data.get('l3_protocol_data', {}).get('name')
            if dns_domain != None:
                self.generate('      dns_domain:', dns_domain)
                dns_domain_not_set = False
                break
        if dns_domain_not_set:
                self.generate('#     dns_domain: DNS_DOMAIN')
        # Property 'name' is not set as it sets by Heat engine.
        self.generate('#     name:', network_name, '# set by Heat engine')
        # TODO: Could property 'port_security_enabled' be set?
        self.generate('#     port_security_enabled: true # default value')
        # TODO: Could property 'qos_policy' be set?
        self.generate('#     qos_policy: QOS_POLICY_ID_OR_NAME')
        # Nothing to do for property 'shared' as set to false by default.
        self.generate('      shared: false # default value')
        # TODO: Could property 'tags' be set?
        self.generate('#     tags: [] # default value')
        # TODO: Could property 'value_specs' be set?
        self.generate('#     value_specs: {} # default value')
        #
        # Generate metadata of the OS::Neutron::Net resource.
        #
        self.generate('    metadata:')
        # Store the TOSCA type as a metadata of the resource.
        self.generate('      tosca.type:', network_type)
        # Store property 'connectivity_type' as metadata of the resource.
        network_connectivity_type = network_properties.get('connectivity_type')
        network_connectivity_type_layer_protocols = network_connectivity_type.get('layer_protocols')
        self.generate('      connectivity_type.layer_protocols: ', network_connectivity_type_layer_protocols, sep='')
        network_connectivity_type_flow_pattern = network_connectivity_type.get('flow_pattern')
        if network_connectivity_type_flow_pattern != None:
            self.generate('      connectivity_type.flow_pattern: ', network_connectivity_type_flow_pattern, sep='')
        # Store property 'vl_profile' as metadata of the resource.
        network_vl_profile = network_properties.get('vl_profile')
        network_vl_profile_max_bitrate_requirements = network_vl_profile.get('max_bitrate_requirements')
        if network_vl_profile_max_bitrate_requirements:
            network_vl_profile_max_bitrate_requirements_root = network_vl_profile_max_bitrate_requirements.get('root')
            self.generate('      vl_profile.max_bitrate_requirements.root:', network_vl_profile_max_bitrate_requirements_root)
            network_vl_profile_max_bitrate_requirements_leaf = network_vl_profile_max_bitrate_requirements.get('leaf')
            if network_vl_profile_max_bitrate_requirements_leaf != None:
                self.generate('      vl_profile.max_bitrate_requirements.leaf:', network_vl_profile_max_bitrate_requirements_leaf)
        else:
            network_vl_profile_max_bitrate_requirements_root = None
            network_vl_profile_max_bitrate_requirements_leaf = None
        network_vl_profile_min_bitrate_requirements = network_vl_profile.get('min_bitrate_requirements')
        if network_vl_profile_min_bitrate_requirements:
            network_vl_profile_min_bitrate_requirements_root = network_vl_profile_min_bitrate_requirements.get('root')
            self.generate('      vl_profile.min_bitrate_requirements.root:', network_vl_profile_min_bitrate_requirements_root)
            network_vl_profile_min_bitrate_requirements_leaf = network_vl_profile_min_bitrate_requirements.get('leaf')
            if network_vl_profile_min_bitrate_requirements_leaf != None:
                self.generate('      vl_profile.min_bitrate_requirements.leaf:', network_vl_profile_min_bitrate_requirements_leaf)
        network_vl_profile_virtual_link_protocol_data = network_vl_profile.get('virtual_link_protocol_data')
        if network_vl_profile_virtual_link_protocol_data != None:
             self.generate('      vl_profile.virtual_link_protocol_data:', network_vl_profile_virtual_link_protocol_data)
        network_vl_profile_qos = network_vl_profile.get('qos')
        if network_vl_profile_qos != None:
            network_vl_profile_qos_latency = network_vl_profile_qos.get('latency')
            self.generate('      vl_profile.qos.latency:', network_vl_profile_qos_latency)
            network_vl_profile_qos_packet_delay_variation = network_vl_profile_qos.get('packet_delay_variation')
            self.generate('      vl_profile.qos.packet_delay_variation:', network_vl_profile_qos_packet_delay_variation)
            network_vl_profile_qos_packet_loss_ratio = network_vl_profile_qos.get('packet_loss_ratio')
            if network_vl_profile_qos_packet_loss_ratio != None:
                self.generate('      vl_profile.qos.packet_loss_ratio:', network_vl_profile_qos_packet_loss_ratio)
            network_vl_profile_qos_priority = network_vl_profile_qos.get('priority')
            if network_vl_profile_qos_priority != None:
                self.generate('      vl_profile.qos.priority:', network_vl_profile_qos_priority)
        network_vl_profile_service_availability = network_vl_profile.get('service_availability')
        if network_vl_profile_service_availability != None:
            network_vl_profile_service_availability_level = network_vl_profile_service_availability.get('level')
            if network_vl_profile_service_availability_level != None:
                self.generate('      vl_profile.service_availability.level:', network_vl_profile_service_availability_level)
        # Store property 'description' as metadata of the resource.
        network_description = network_properties.get('description')
        if network_description != None:
            self.generate('      description:', network_description)
        # Store property 'test_access' as metadata of the resource.
        network_test_access = network_properties.get('test_access')
        if network_test_access != None:
            self.generate('      test_access: ', network_test_access, sep='')

        if self.configuration.get(HOT, 'OS::Neutron::QoS.available'):
            def generate_qos(role, max_bitrate_requirements):
                #
                # Generate an OS::Neutron::QoSPolicy resource.
                #
                self.generate_resource(network_name + '_' + role + '_qos_policy', 'OS::Neutron::QoSPolicy')
                #
                # Generate properties of the OS::Neutron::QoSPolicy resource.
                #
                self.generate('    properties:')
                # Property 'description' is set even if this is not required.
                self.generate('      description: QoS policy for ', role, ' ports of network ', network_name, sep='')
                # Property 'name' is not set as it sets by Heat engine.
                self.generate('#     name: ', network_name, ' root QoS Policy # set by Heat engine', sep='')
                # Nothing to do for property 'shared' as set to false by default.
                self.generate('#     shared: false # default value')

                if max_bitrate_requirements != None:
                    #
                    # Generate an OS::Neutron::QoSBandwidthLimitRule resource.
                    #
                    self.generate_resource(network_name + '_' + role + '_qos_bandwidth_limit_rule', 'OS::Neutron::QoSBandwidthLimitRule')
                    #
                    # Generate properties of the OS::Neutron::QoSBandwidthLimitRule resource.
                    #
                    self.generate('    properties:')
                    self.generate('      policy: { get_resource: ', network_name, '_', role, '_qos_policy }', sep='')
                    # Property 'max_kbps' is required.
                    max_kbps =int(max_bitrate_requirements/1000)
                    self.generate('      max_kbps: ', max_kbps, sep='')
                    # TODO: Could property 'max_burst_kbps' be set?
                    self.generate('#     max_burst_kbps:',  max_kbps)

            generate_qos('root', network_vl_profile_max_bitrate_requirements_root)
            generate_qos('leaf', network_vl_profile_max_bitrate_requirements_leaf)

        network_vl_profile_virtual_link_protocol_data = {}
        for virtual_link_protocol_data in network_vl_profile.get('virtual_link_protocol_data', []):
            network_vl_profile_virtual_link_protocol_data[virtual_link_protocol_data.get('associated_layer_protocol')] = virtual_link_protocol_data

        if type(network_connectivity_type_layer_protocols) == list:
            layer_protocols = network_connectivity_type_layer_protocols
        elif type(network_connectivity_type_layer_protocols) == str:
            layer_protocols = [ network_connectivity_type_layer_protocols ]
        for layer_protocol in layer_protocols:
            # Generate only ip subnets
            if layer_protocol not in ['ipv4', 'ipv6']:
                continue
            # Get the protocol data associated to the current layer_protocol.
            l3_protocol_data = network_vl_profile_virtual_link_protocol_data.get(layer_protocol, {}).get('l3_protocol_data', {})
            #
            # Generate an OS::Neutron::Subnet resource.
            #
            self.generate_resource(network_name + '_subnet_' + layer_protocol, 'OS::Neutron::Subnet')
            #
            # Generate properties of the OS::Neutron::Subnet resource.
            #
            self.generate('    properties:')
            # Set required property 'network'.
            self.generate('      network: { get_resource: ', network_name, ' }', sep='')
            # Set property 'allocation_pools' if needed.
            ip_allocation_pools = l3_protocol_data.get('ip_allocation_pools')
            if ip_allocation_pools:
                self.generate('      allocation_pools:')
                for ip_allocation_pool in ip_allocation_pools:
                    self.generate('        - start:', ip_allocation_pool.get('start_ip_address'))
                    self.generate('          end:', ip_allocation_pool.get('end_ip_address'))
            else:
                self.generate('#     allocation_pools: [] # default value')
            # Set property 'cidr' as required.
            cidr = l3_protocol_data.get('cidr')
            if cidr == None:
                # self.generate('      subnetpool: { get_resource: subnetpool_', layer_protocol, ' }', sep='')
                cidr = self.configuration.get(HOT, 'OS::Neutron::Subnet.cidr.' + layer_protocol) % self.subnet_cidr_idx
                self.subnet_cidr_idx = self.subnet_cidr_idx +1
                self.warning(' HOT - CIDR "' + cidr + '" generated')
                self.generate('      cidr:', cidr, ' # generated')
            else:
                self.generate('      cidr:', cidr)
            # Set property 'enable_dhcp' if needed.
            dhcp_enabled = l3_protocol_data.get('dhcp_enabled')
            if dhcp_enabled != None:
                self.generate('      enable_dhcp:', str(dhcp_enabled).lower())
            else:
                self.generate('#     enable_dhcp: true # default value')
            # Set property 'gateway_ip' if needed.
            gateway_ip = l3_protocol_data.get('gateway_ip')
            if gateway_ip != None:
                self.generate('      gateway_ip:', gateway_ip)
            else:
                self.generate('#     gateway_ip: GATEWAY_IP')
            # TODO: Could property 'host_routes' be set?
            self.generate('#     host_routes: {} # default value')
            # Set property 'ip_version'.
            if layer_protocol == 'ipv4':
                ip_version = 4
            elif layer_protocol == 'ipv6':
                ip_version = 6
            self.generate('      ip_version:', ip_version)
            # TODO: Could property 'ipv6_address_mode' be set?
            self.generate('#     ipv6_address_mode: ""')
            # TODO: Could property 'ipv6_ra_mode' be set?
            self.generate('#     ipv6_ra_mode: ""')
            # Property 'name' is not set as it sets by Heat engine.
            self.generate('#     name: ', network_name, '-subnet-', layer_protocol, ' # set by Heat engine', sep='')
            # TODO: Could property 'prefixlen' be set?
            self.generate('#     prefixlen: integer')
            # TODO: Could property 'segment' be set?
            self.generate('#     segment: segment_id')
            # TODO: Could property 'subnetpool' be set?
            self.generate('#     subnetpool: subnetpool_id')
            # TODO: Could property 'tags' be set?
            self.generate('#     tags: [] # default value')
            # TODO: Could property 'value_specs' be set?
            self.generate('#     value_specs: {} # default value')

    def generate_NsVirtualLink(self, ns_virtual_link_name, ns_virtual_link_yaml):
        self.generate_network(ns_virtual_link_name, ns_virtual_link_yaml)

    def generate_VNF(self, vnf_name, vnf_yaml):
        self.generate_hot_template_ressource(vnf_name, vnf_yaml)

    def generate_OS_Glance_Image(self, node_name, node_yaml):

        if not self.configuration.get(HOT, 'OS::Glance::Image.available'):
            return False

        # Generate OS::Glance::Image

        # Search a tosca.artifacts.nfv.SwImage artifact.
        sw_image_artifact_location = None
        for artifact_name, artifact_yaml in node_yaml.get(ARTIFACTS, {}).items():
            if artifact_yaml.get(TYPE) == 'tosca.artifacts.nfv.SwImage':
                sw_image_artifact_location = artifact_yaml.get(FILE)
                break

        sw_image_data = node_yaml.get(PROPERTIES, {}).get('sw_image_data')
        if sw_image_data:
            self.generate_resource(node_name +  '_image', 'OS::Glance::Image')
            self.generate('    properties:')
            self.generate('#     name:', sw_image_data.get('name'), ' # set by Heat engine')
            if sw_image_artifact_location:
                self.generate('      location:', sw_image_artifact_location)
            else:
                self.error(TOPOLOGY_TEMPLATE + ':' + NODE_TEMPLATES + ':' + node_name + ": Artifact of type 'tosca.artifacts.nfv.SwImage' required")
                self.generate('      location: # ERROR: Location not set because tosca.artifacts.nfv.SwImage artifact missed!')
            self.generate('      container_format:', sw_image_data.get('container_format')) # TODO: Is 'docker' value supported by OpenStack?
            self.generate('      disk_format:', sw_image_data.get('disk_format')) # TODO: is 'vhdx' value supported by OpenStack?
            self.generate('      min_disk:', self.sizeInGB(sw_image_data.get('min_disk')))
            min_ram = sw_image_data.get('min_ram')
            if min_ram:
                self.generate('      min_ram:', self.sizeInMB(min_ram))
            operating_system = sw_image_data.get('operating_system')
            if operating_system:
                self.generate('      os_distro:', operating_system.lower())
            else:
                self.generate('#     os_distro: ')
            self.generate('      extra_properties:')
            self.generate('        version:', sw_image_data.get('version'))
            self.generate('        checksum:', sw_image_data.get('checksum'))
            self.generate('        size:', sw_image_data.get('size'))
            self.generate_todo_translate(sw_image_data, 'supported_virtualisation_environments')
            return True
        elif sw_image_artifact_location:
            self.error(TOPOLOGY_TEMPLATE + ':' + NODE_TEMPLATES + ':' + node_name + ": Property 'sw_image_data' required")
        return False

    def generate_Vdu_Compute(self, vdu_compute_name, vdu_compute_node):
        vdu_compute_properties = vdu_compute_node.get(PROPERTIES)

        #
        # Generate a OS::Nova::Flavor resource.
        #
        virtual_compute_properties = vdu_compute_node.get(CAPABILITIES, {}).get('virtual_compute', {}).get(PROPERTIES, {})
        self.generate_resource(vdu_compute_name +  '_flavor', 'OS::Nova::Flavor')
        #
        # Generate properties.
        #
        self.generate('    properties:')
        self.generate('      is_public: false')
        virtual_memory = virtual_compute_properties.get('virtual_memory')
        if type(virtual_memory) == dict:
            ram = self.sizeInMB(virtual_memory.get('virtual_mem_size'))
        else:
            ram = 0
        maximum_ram = self.configuration.get(HOT, 'OS::Nova::Flavor.ram.maximum')
        if ram > maximum_ram:
            self.generate('      ram:', maximum_ram, '# WARNING: Initial value was', ram, '!')
            self.warning(' HOT - ram of ' + str(ram) + 'MB narrowed to '+ str(maximum_ram) + 'MB')
        else:
            self.generate('      ram:', ram)
        self.generate_todo_translate(virtual_memory, 'virtual_mem_oversubscription_policy')
        self.generate_todo_translate(virtual_memory, 'vdu_mem_requirements')
        self.generate_todo_translate(virtual_memory, 'numa_enabled')
        virtual_cpu = virtual_compute_properties.get('virtual_cpu')
        if type(virtual_cpu) == dict:
            self.generate('      vcpus:', virtual_cpu.get('num_virtual_cpu'))
        self.generate_todo_translate(virtual_cpu, 'cpu_architecture')
        self.generate_todo_translate(virtual_cpu, 'virtual_cpu_clock')
        self.generate_todo_translate(virtual_cpu, 'virtual_cpu_oversubscription_policy')
        self.generate_todo_translate(virtual_cpu, 'vdu_cpu_requirements')
        self.generate_todo_translate(virtual_cpu, 'virtual_cpu_pinning')
        self.generate_todo_translate(virtual_compute_properties, 'logical_node')
        self.generate_todo_translate(virtual_compute_properties, 'requested_additional_capabilities')
        self.generate_todo_translate(virtual_compute_properties, 'compute_requirements')
        self.generate_todo_translate(virtual_compute_properties, 'virtual_local_storage')

        # Generate image.
        image_generated = self.generate_OS_Glance_Image(vdu_compute_name, vdu_compute_node)

        #
        # Generate OS::Nova::Server
        #
        vdu_profile = vdu_compute_properties.get('vdu_profile')
        if type(vdu_profile) == dict:
            min_number_of_instances = vdu_profile.get('min_number_of_instances')
            if min_number_of_instances > 1:
                self.generate()
                self.generate_todo_translate(vdu_profile, 'min_number_of_instances')
            max_number_of_instances = vdu_profile.get('max_number_of_instances')
            if max_number_of_instances > 1:
                self.generate()
                self.generate_todo_translate(vdu_profile, 'max_number_of_instances')

        # TODO: Should use AutoScalingGroup

        min_number_of_instances = 1

        for resource_idx in range(0, min_number_of_instances):
            resource_name = vdu_compute_name
            if min_number_of_instances > 1:
                resource_name = resource_name + '_' + str(resource_idx)
            self.generate_resource(resource_name, 'OS::Nova::Server')
            self.generate('    properties:')
            # Property 'name' is not not as it sets by Heat engine.
            name = vdu_compute_properties.get('name')
            self.generate('#     name: ', name, ' # set by Heat engine', sep='')
            description = vdu_compute_properties.get('description')
            self.generate('      metadata:')
            self.generate('        description:', description)
            self.generate('      flavor: { get_resource: ', vdu_compute_name, '_flavor }', sep='')
            if image_generated:
                self.generate('      image: { get_resource: ', vdu_compute_name, '_image }', sep='')
            else:
                self.generate('      image:', self.configuration.get(HOT, 'OS::Nova::Server.image.default'), '# default value generated')

            self.generate_todo_translate(vdu_compute_properties, 'boot_order')
            self.generate_todo_translate(vdu_compute_properties, 'nfvi_constraints')
            self.generate_todo_translate(vdu_compute_properties, 'monitoring_parameters')
            self.generate_todo_translate(vdu_compute_properties, 'boot_data')

            # Generate networks:
            self.generate('      networks:')
            for node_name, node_yaml in self.tosca_service_template.get_yaml().get(TOPOLOGY_TEMPLATE).get(NODE_TEMPLATES).items():
                if node_yaml.get(TYPE) == 'tosca.nodes.nfv.VduCp':
                    for requirement in node_yaml.get(REQUIREMENTS, []):
                        for requirement_name, requirement_value in requirement.items():
                            if requirement_name == 'virtual_binding' and requirement_value == vdu_compute_name:
                                self.generate('        - port: { get_resource:', node_name, '}')
            # Following dependency is required to avoid to remove the flavor before to remove the compute.
            self.generate('    depends_on: ', vdu_compute_name, '_flavor # Required else error when delete the stack. Should it be a bug into Heat engine?', sep='')

            # Generate OS::Cinder::VolumeAttachment resources
            requirements = vdu_compute_node.get('requirements', [])
            vol_idx = 0
            for requirement in requirements:
                for requirement_name, requirement_value in requirement.items():
                    if requirement_name == 'virtual_storage':
                        self.generate_resource(resource_name + '_volume_attachment_' + str(vol_idx), 'OS::Cinder::VolumeAttachment')
                        vol_idx = vol_idx + 1
                        self.generate('    properties:')
                        self.generate('     volume_id: { get_resource:', requirement_value, '}')
                        self.generate('     instance_uuid: { get_resource:', resource_name, '}')
                        self.generate('    depends_on:', requirement_value, '# WARNING: Else error. Should it be a bug into Heat engine?')

    def generate_VduCp(self, vdu_cp_name, vdu_cp_yaml):
        vdu_cp_properties = vdu_cp_yaml.get(PROPERTIES)

        virtual_link = None
        virtual_link_as_param = None
        for requirement in vdu_cp_yaml.get(REQUIREMENTS, []):
            for requirement_name, requirement_value in requirement.items():
                if requirement_name == 'virtual_link':
                    if requirement_value != None:
                        virtual_link = requirement_value
                        virtual_link_as_param = False
                elif requirement_name == 'virtual_binding':
                    # Already done in Vdu.Compute
                    pass
                elif requirement_name == 'trunk_binding':
                    pass # TODO
                # TODO: deal with requirement 'dependency'
                else:
                    self.error(' HOT - Invalid requirement ' + requirement_name + ': ' + str(requirement_value))

        if virtual_link_as_param == None:
            for requirement_name, requirement_value in syntax.get_substitution_mappings_requirements(self.tosca_service_template.get_yaml().get(TOPOLOGY_TEMPLATE).get(SUBSTITUTION_MAPPINGS, {})).items():
                if type(requirement_value) == list and len(requirement_value) == 2 and requirement_value[0] == vdu_cp_name and requirement_value[1] == 'virtual_link':
                    virtual_link = requirement_name
                    virtual_link_as_param = True

        if virtual_link_as_param == True:
            self.generate_resource(vdu_cp_name, 'OS::Neutron::Port')
            self.generate('    properties:')
            self.generate('      network: { get_param: ', virtual_link, ' }', sep='')

            self.generate_todo_translate(vdu_cp_properties, 'layer_protocols')
            self.generate_todo_translate(vdu_cp_properties, 'role')
        else:
            if vdu_cp_properties != None:
                vdu_cp_role = vdu_cp_properties.get('role')
                layer_protocols = vdu_cp_properties.get('layer_protocols')
                if len(layer_protocols) > 1:
                    for layer_protocol in layer_protocols:
                        self.generate_OS_Neutron_Port(vdu_cp_name + '_' + layer_protocol + '_port', virtual_link, layer_protocol, vdu_cp_role)
                    self.generate_resource(vdu_cp_name, 'OS::Heat::None')
                    self.generate('    depends_on:')
                    for layer_protocol in layer_protocols:
                        self.generate('      - ', vdu_cp_name, '_', layer_protocol, '_port', sep='')
                elif len(layer_protocols) == 1:
                            self.generate_OS_Neutron_Port(vdu_cp_name, virtual_link, layer_protocols[0], vdu_cp_role)
                else:
                    self.error(' HOT - layer_protocols can not be empty')

        self.generate_todo_translate(vdu_cp_properties, 'description')
        self.generate_todo_translate(vdu_cp_properties, 'trunk_mode')
        self.generate_todo_translate(vdu_cp_properties, 'bitrate_requirement')
        self.generate_todo_translate(vdu_cp_properties, 'virtual_network_interface_requirements')
        self.generate_todo_translate(vdu_cp_properties, 'order')
        self.generate_todo_translate(vdu_cp_properties, 'vnic_type')

    def generate_Vdu_VirtualBlockStorage(self, vdu_virtual_block_storage_name, vdu_virtual_block_storage_node):
        image_generated = self.generate_OS_Glance_Image(vdu_virtual_block_storage_name, vdu_virtual_block_storage_node)

        self.generate_resource(vdu_virtual_block_storage_name, 'OS::Cinder::Volume')
        self.generate('    properties:')
        vdu_virtual_block_storage_properties = vdu_virtual_block_storage_node.get(PROPERTIES)
        virtual_block_storage_data = vdu_virtual_block_storage_properties.get('virtual_block_storage_data')
        size_of_storage = virtual_block_storage_data.get('size_of_storage')
        self.generate('      size:',  self.sizeInGB(size_of_storage))
        if image_generated:
                 self.generate('      image: { get_resource: ', vdu_virtual_block_storage_name, '_image }', sep='')

        self.generate_todo_translate(virtual_block_storage_data, 'vdu_storage_requirements')
        self.generate_todo_translate(virtual_block_storage_data, 'rdma_enabled')

    def generate_Vdu_VirtualObjectStorage(self, vdu_virtual_object_name, vdu_virtual_object_node):
        self.generate_resource(vdu_virtual_object_name, 'TODO')

    def generate_Vdu_VirtualFileStorage(self, vdu_virtual_file_name, vdu_virtual_file_node):
        self.generate_resource(vdu_virtual_file_name, 'TODO')

    def generate_VnfVirtualLink(self, vnf_virtual_link_name, vnf_virtual_link_yaml):
        self.generate_network(vnf_virtual_link_name, vnf_virtual_link_yaml)

        self.generate()
        vnf_virtual_link_properties = vnf_virtual_link_yaml.get(PROPERTIES)
        self.generate_todo_translate(vnf_virtual_link_properties, 'test_access')
        self.generate_todo_translate(vnf_virtual_link_properties, 'monitoring_parameters')

    def generate_VnfExtCp(self, vnf_ext_cp_name, vnf_ext_cp_yaml):
        self.generate_router(vnf_ext_cp_name, vnf_ext_cp_yaml)

    def generate_PNF(self, pnf_name, pnf_yaml):
        self.generate_hot_template_ressource(pnf_name, pnf_yaml)

    def generate_PnfExtCp(self, pnf_ext_cp_name, pnf_ext_cp_yaml):
        self.generate()
        self.generate("  # TODO", sep='')

    def generate_undefined_node(self, node_name, node):
        self.generate("  # TODO: Undefined translation for node '", node_name, "' of type '", node.get(TYPE), "'!", sep='')

    GENERATE_NODES = {
        # For ETSI NFV Network Service Descriptor (NSD).
        'tosca.nodes.nfv.NS':                       generate_NS,
        'tosca.nodes.nfv.Sap':                      generate_Sap,
        'tosca.nodes.nfv.NsVirtualLink':            generate_NsVirtualLink,
        # For ETSI NFV Virtual Network Function Descriptor (VNFD).
        'tosca.nodes.nfv.VNF':                      generate_VNF,
        'tosca.nodes.nfv.Vdu.Compute':              generate_Vdu_Compute,
        'tosca.nodes.nfv.VduCp':                    generate_VduCp,
        'tosca.nodes.nfv.Vdu.VirtualBlockStorage':  generate_Vdu_VirtualBlockStorage,
        'tosca.nodes.nfv.Vdu.VirtualObjectStorage': generate_Vdu_VirtualObjectStorage,
        'tosca.nodes.nfv.Vdu.VirtualFileStorage':   generate_Vdu_VirtualFileStorage,
        'tosca.nodes.nfv.VnfVirtualLink':           generate_VnfVirtualLink,
        'tosca.nodes.nfv.VnfExtCp':                 generate_VnfExtCp,
        # For ETSI NFV Virtual Physical Network Function Descriptor (PNFD).
        'tosca.nodes.nfv.PNF':                      generate_PNF,
        'tosca.nodes.nfv.PnfExtCp':                 generate_PnfExtCp,
    }
