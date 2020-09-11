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

from cloudnet.tosca.processors import Generator
import cloudnet.tosca.syntax as syntax

from cloudnet.tosca.configuration import DEFAULT_CONFIGURATION
NWDIAG = 'nwdiag'
DEFAULT_CONFIGURATION[NWDIAG] = {
    # Target directory where network diagrams are generated.
    Generator.TARGET_DIRECTORY: 'nwdiag'
}
DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

class NwdiagGenerator(Generator):
    '''
        This is the generator of network diagrams.
    '''

    def generator_configuration_id(self):
        return NWDIAG

    def generation(self):
        self.info('Network diagram generation')

        # TODO: Following could be shared with HOTGenerator

        template_yaml = self.tosca_service_template.get_yaml()
        is_etsi_nfv_sol001_template = False
        for an_import in syntax.get_imports(template_yaml):
            import_file = syntax.get_import_file(an_import)
            if import_file.startswith('etsi_nfv_sol001_'): # or import_file == 'onap_dm.yaml': # TODO
                is_etsi_nfv_sol001_template = True
                break
        topology_template = syntax.get_topology_template(template_yaml)
        # Generate HOT only for ETSI NFV SOL 001 NSD/VNFD/PNFD topology template.
        if is_etsi_nfv_sol001_template == False or topology_template == None:
            return

        node_type_requirements = {}
        substitution_mappings = syntax.get_substitution_mappings(topology_template)
        if substitution_mappings != None:
            substitution_mappings_node_type = syntax.get_node_type(substitution_mappings)
            if substitution_mappings_node_type:
                node_type_requirements = syntax.get_requirements_dict(self.type_system.merge_type(substitution_mappings_node_type))

        networks = {}
        def get_network(network_name):
            network = networks.get(network_name)
            if network == None:
                network = {}
                networks[network_name] = network
            return network
        network_of_nodes = {}

        if substitution_mappings:
            for requirement_name, requirement_value in syntax.get_substitution_mappings_requirements(substitution_mappings).items():
                requirement_definition = node_type_requirements.get(requirement_name)
                capability = syntax.get_requirement_capability(requirement_definition)
                if capability == 'tosca.capabilities.nfv.VirtualLinkable':
                    network_of_nodes[requirement_value[0]] = get_network(requirement_name)

        for node_name, node_yaml in syntax.get_node_templates(topology_template).items():
            node_type = syntax.get_type(node_yaml)
            if node_type in [ 'tosca.nodes.nfv.VnfVirtualLink', 'tosca.nodes.nfv.NsVirtualLink' ]:
                network = get_network(node_name)
            elif node_type in [ 'tosca.nodes.nfv.VduCp' ]:
                virtual_binding = None
                virtual_link = None
                for requirement in syntax.get_requirements_list(node_yaml):
                    for requirement_name, requirement_yaml in requirement.items():
                        if requirement_name == 'virtual_binding':
                            virtual_binding = requirement_yaml
                        elif requirement_name == 'virtual_link':
                            virtual_link = requirement_yaml
                if virtual_binding:
                    if virtual_link:
                        get_network(virtual_link)[virtual_binding] = 'compute'
                    else:
                        network_of_nodes[node_name][virtual_binding] = 'compute'
            elif node_type in [ 'tosca.nodes.nfv.VnfExtCp', 'tosca.nodes.nfv.Sap',  'tosca.nodes.nfv.PnfExtCp' ]:
                internal_virtual_link = None
                external_virtual_link = None
                for requirement in syntax.get_requirements_list(node_yaml):
                    for requirement_name, requirement_yaml in requirement.items():
                        if requirement_name == 'internal_virtual_link':
                            internal_virtual_link = requirement_yaml
                        elif requirement_name == 'external_virtual_link':
                            external_virtual_link = requirement_yaml
                if internal_virtual_link:
                    get_network(internal_virtual_link)[node_name] = 'router'
                if external_virtual_link:
                    get_network(external_virtual_link)[node_name] = 'router'
                else:
                    try:
                        network_of_nodes[node_name][node_name] = 'router'
                    except KeyError:
                        LOGGER.error(node_name + ' unknown!')
            else:
                node_type_requirements = syntax.get_requirements_dict(self.type_system.merge_type(node_type))
                for requirement in syntax.get_requirements_list(node_yaml):
                    for requirement_name, requirement_yaml in requirement.items():
                        requirement_definition = node_type_requirements.get(requirement_name)
                        capability = syntax.get_requirement_capability(requirement_definition)
                        if capability == 'tosca.capabilities.nfv.VirtualLinkable':
                            virtual_link = requirement_yaml
                            if virtual_link:
                                get_network(virtual_link)[node_name] = node_type
                            else:
                                network_of_nodes.get(node_name, {})[node_name] = node_type

        if len(networks):
            # Generate the network diagram.
            self.open_file('.nwdiag')
            self.generate('{')
            for network_name, network_content in networks.items():
                self.generate('  network ', network_name, ' {', sep='')
                for name, key in network_content.items():
                    self.generate('    "', name, '";', sep='')
                self.generate('  }')
            self.generate('}')
            self.close_file()
