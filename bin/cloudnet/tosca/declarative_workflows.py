######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2021-24 Orange
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
import cloudnet.tosca.utils as utils
import cloudnet.tosca.syntax as syntax
import yaml
import os
import copy

import cloudnet.tosca.configuration as configuration
DECLARATIVE_WORKFLOWS = 'DeclarativeWorkflows'
configuration.DEFAULT_CONFIGURATION[DECLARATIVE_WORKFLOWS] = {
    # Generation activated.
    Generator.GENERATION: True,
    # Target directory where declarative workflows are generated.
    Generator.TARGET_DIRECTORY: "Results/DeclarativeWorkflows",
}

with open(os.path.dirname(__file__) + "/declarative_workflows.yaml", 'r') as stream:
    configuration.DEFAULT_CONFIGURATION[DECLARATIVE_WORKFLOWS]["workflows"] \
        = yaml.safe_load(stream)

configuration.DEFAULT_CONFIGURATION['logging']['loggers'][__name__] = {
    'level': 'INFO',
}

import logging # for logging purposes.
LOGGER = logging.getLogger(__name__)

# TODO: Should be moved into processors.py
class TopologyTemplateGenerator(Generator):
    '''
        This is the base class of TOSCA topology template generators.
    '''

    def generation(self):
        topology_template = \
            syntax.get_topology_template(self.tosca_service_template.get_yaml())
        # Generate only for TOSCA topology template.
        if topology_template != None:
            self.generate_topology_template(topology_template)
        else:
            self.info('no topology template to process')

    def generate_topology_template(self, topology_template):
        raise NotImplementedError

#TBR or move into utils.py
# def format_map(input, args):
#     if isinstance(input, str):
#         return input.format_map(args)
#     elif isinstance(input, list):
#         output = []
#         for i in input:
#             output.append(format_map(i, args))
#         return output
#     elif isinstance(input, dict):
#         output = {}
#         for k, v in input.items():
#             output[format_map(k, args)] = format_map(v, args)
#         return output
#     else:
#         return input

class DeclarativeWorkflowGenerator(TopologyTemplateGenerator):
    '''
        This is the generator of TOSCA declarative workflows.
    '''

    def generator_configuration_id(self):
        return DECLARATIVE_WORKFLOWS

    def generator_title(self):
        return 'TOSCA Declarative Workflow Generator'

    def generate_topology_template(self, topology_template):
        workflows = topology_template.get('workflows')
        if workflows is None:
            # add empty workflows to the topology template
            workflows = {}
            topology_template['workflows'] = workflows

        configuration_workflows = self.configuration.get(DECLARATIVE_WORKFLOWS, "workflows")
        for workflow_name, workflow_generator_configuration \
               in configuration_workflows.items():
            self.debug('- compute workflow %s...' % workflow_name)
            # Flatten extend keyname
            extend = workflow_generator_configuration.get("extend")
            if extend != None:
                self.debug("workflow %s extends %s" % (workflow_name, extend))
                extended_workflow = configuration_workflows[extend]

                def flatten_types(keyname):
                    config = workflow_generator_configuration.get(keyname)
                    if config is None:
                        config = {}
                        workflow_generator_configuration[keyname] = config
                    for key, value in extended_workflow.get(keyname, {}).items():
                        if key not in config:
                            config[key] = value
                        else:
                            subconfig = config[key]
                            for subkey, subvalue in value.items():
                                if subkey not in subconfig:
                                    subconfig[subkey] = subvalue

                flatten_types("node_types")
                flatten_types("relationship_types")
            # Instantiate the workflow generator
            workflow_generator = \
                WorkflowGenerator(self, workflow_generator_configuration)
            # Generate the declarative workflow
            generated_workflow = \
                workflow_generator.generate_workflow(topology_template)
            if generated_workflow != None:
                self.info('- %s workflow generated' % workflow_name)
                workflows[workflow_name] = generated_workflow
            else:
                self.info('- %s workflow not generated' % workflow_name)

        # save the generated workflows
        self.open_file('.yaml')
        yaml.safe_dump(self.tosca_service_template.get_yaml(), self.file)
        self.close_file()

# TODO merge into DeclarativeWorkflowGenerator class

class WorkflowGenerator(object):
    def __init__(self, processor, configuration):
        self.processor = processor
        self.type_system = processor.type_system
        self.configuration = configuration

    def get_config_for_a_type(self, type_kind, type_name, keyname=None):
        config = self.configuration[type_kind]
        while True:
            type_name = self.type_system.get_type_uri(type_name)
            result = config.get(type_name)
            if result != None:
                if keyname is None:
                    return result
                else:
                    value = result.get(keyname)
                    if value != None:
                        return value
            if type_name is None:
                return None
            type_name = self.type_system.types.get(type_name, {}).get('derived_from')

    def generate_workflow(self, topology_template):
        # get the node templates
        node_templates = topology_template.get('node_templates', {})

        # init workflow steps
        steps = {}

        # generate workflow steps for each node template
        for node_name, node_template in node_templates.items():
            self.generate_node_template(steps, node_name, node_template)

        # generate workflow steps for each node template requirement
        relationship_id = 0
        for node_name, node_template in node_templates.items():
            # get the node type
            node_template_type = node_template.get('type')
            node_template_type = self.type_system \
                .merge_type(self.type_system.get_type_uri(node_template_type))
            for requirement in node_template.get('requirements', []):
                for requirement_name, requirement_def in requirement.items():
                    # create a relationship instance
                    relationship = Relationship(topology_template, \
                                                node_name, \
                                                node_template, \
                                                node_template_type, \
                                                requirement_name, \
                                                requirement_def, \
                                                relationship_id)
                    # weave operations of the relationship
                    self.generate_relationship_weave_operations(steps, relationship)
                    # weave steps of both source and target node templates
                    self.generate_relationship_weave_steps(steps, relationship)
                    # increase relationship_id
                    relationship_id += 1

        if len(steps) == 0: # no step generated
            return None     # then no workflow generated

        # return a workflow
        return utils.merge_dict( \
            self.configuration.get("workflow", {}),
            { 'steps': steps }
        )

    def generate_node_template(self,
                               steps,
                               node_name,
                               node_template):
        templated_steps = \
            self.get_config_for_a_type("node_types", node_template.get('type'))
        if templated_steps is None:
            return

        # duplicate templated_steps
        templated_steps = copy.deepcopy(templated_steps.get('steps', {}))

        if isinstance(templated_steps, dict):
            for step_name, step_def in templated_steps.items():
                # the target of steps is the node name
                step_def["target"] = node_name
                # rename on_success steps
                on_success_steps = step_def.get("on_success")
                if on_success_steps != None:
                    for idx in range(0, len(on_success_steps)):
                        on_success_step_name = on_success_steps[idx]
                        if on_success_step_name in templated_steps:
                            on_success_steps[idx] = on_success_step_name + '_' + utils.normalize_name(node_name)

                # add the step to the workflow steps
                steps[step_name + '_' + utils.normalize_name(node_name)] = step_def

        elif isinstance(templated_steps, list):
            previous_step = {}
            for templated_step in templated_steps:
                for step_name, step_def in templated_step.items():
                    # the target of steps is the node name
                    step_def["target"] = node_name
                    # link previous step with this step
                    previous_step["on_success"] = [ step_name + '_' + utils.normalize_name(node_name) ]
                    previous_step = step_def
                    # add the step to the workflow steps
                    steps[step_name + '_' + utils.normalize_name(node_name)] = step_def

    def generate_relationship_weave_operations(self, steps, relationship):
        weave_operations = \
            self.get_config_for_a_type( \
                    "relationship_types", \
                    relationship.relationship_type_name,
                    "weave_operations")

        if weave_operations is None:
            return

        relationship_id = relationship.id
        source_node_name = relationship.source_node_template_name
        requirement_name = relationship.source_requirement_name

        format_args = {
            'SOURCE': relationship.source_node_template_name,
            'TARGET': relationship.target_node_template_name,
        }
        for weave_operation in weave_operations:
            weave_operation = weave_operation.format_map(format_args)
            tmp1 = weave_operation.split(' ')
            tmp2 = tmp1[0].split('.')
            interface_name = tmp2[0]
            operation_name = tmp2[1]
            operator = tmp1[1]
            step_name = tmp1[2]

            if relationship.is_operation_implemented(interface_name, operation_name):
                operation_step_name = operation_name + '_' + str(relationship_id)
                steps[operation_step_name] = {
                    'target': source_node_name,
                    'target_relationship': requirement_name,
                    'activities': [
                        {'call_operation': interface_name + '.' + operation_name }
                    ],
                }
                on_success = steps[step_name].get("on_success")
                if operator == "after":
                    if on_success is None:
                        on_success = []
                        steps[step_name]["on_success"] = on_success
                    on_success.append(operation_step_name)
                elif operator == "follow":
                    steps[operation_step_name]["on_success"] = []
                    if on_success != None:
                        steps[operation_step_name]["on_success"].extend(on_success)
                    steps[step_name]["on_success"] = [ operation_step_name ]
                else:
                    raise Exception(weave_operation)

    def generate_relationship_weave_steps(self, steps, relationship):
        weave_steps = \
            self.get_config_for_a_type( \
                    "relationship_types", \
                    relationship.relationship_type_name)
        if weave_steps is None:
            return

        format_args = {
            'SOURCE': utils.normalize_name(relationship.source_node_template_name),
            'TARGET': utils.normalize_name(relationship.target_node_template_name),
        }
        for weave_step in weave_steps.get("weave_steps", []):
            weave_step = weave_step.format_map(format_args)
            self.processor.debug("  weave " + weave_step)
            tmp = weave_step.split(' ')
            if steps.get(tmp[0]) is None:
                self.processor.debug("- no %r step" % tmp[0])
                continue # next weave_step
            if steps.get(tmp[2]) is None:
                self.processor.debug("- no %r step" % tmp[2])
                continue # next weave_step
            on_success = steps[tmp[0]].get("on_success")
            if on_success is None:
                on_success = []
                steps[tmp[0]]["on_success"] = on_success
            if tmp[1] == "before":
                if tmp[2] not in on_success:
                    on_success.append(tmp[2])
            elif tmp[1] == "follow":
                if steps[tmp[2]].get("on_success") != None:
                    for s in steps[tmp[2]]["on_success"]:
                        if s not in on_success:
                            on_success.append(s)
                steps[tmp[2]]["on_success"] = [] # TODO or [ tmp[0] ] ???
            else:
                raise Exception(weave_step)

class Relationship(object):
    def __init__(self, \
                 topology_template, \
                 node_template_name, \
                 node_template, \
                 node_template_type, \
                 requirement_name, \
                 requirement, \
                 relationship_id):
        # store parameters
        self.source_node_template_name = node_template_name
        self.source_node_template_type = node_template_type
        self.source_requirement_name = requirement_name
        self.id = relationship_id
        # get target node template name
        self.target_node_template_name = \
            syntax.get_requirement_node_template(requirement)
        if(self.target_node_template_name is None):
            # Should not be None so it is unknown node template
            self.target_node_template_name = "UNKNOWN_NODE"

        # compute the relationship type name and interfaces
        node_type_requirements = syntax.get_requirements_dict(node_template_type)
        requirement_def = node_type_requirements.get(requirement_name, {})
        relationship_def = syntax.get_requirement_relationship(requirement_def)
        relationship_type_name = \
            syntax.get_relationship_type(relationship_def)
        self.interfaces = \
            syntax.get_relationship_interfaces(relationship_def) or {}
        # TODO: merge interfaces defined in the relationship type
        interfaces = None
        relationship = syntax.get_requirement_relationship(requirement)
        if isinstance(relationship, str): # short grammar
            relationship_template = \
                topology_template \
                .get(syntax.RELATIONSHIP_TEMPLATES, {}) \
                .get(relationship)
            if relationship_template != None:
                relationship_type_name = relationship_template['type']
                interfaces = relationship_template.get('interfaces')
            else:
                relationship_type_name = relationship
        elif isinstance(relationship, dict): # extended grammar
            tmp = relationship.get('type')
            if tmp != None:
                relationship_type_name = tmp
            interfaces = relationship.get('interfaces')

        self.relationship_type_name = relationship_type_name

        if interfaces != None:
            self.interfaces = utils.merge_dict(self.interfaces, interfaces)

    def is_operation_implemented(self, interface_name, operation_name):
        return syntax.get_operations(self.interfaces.get(interface_name, {})) \
                .get('operations', {}) \
                .get(operation_name) != None
