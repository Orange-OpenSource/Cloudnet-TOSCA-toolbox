/******************************************************************************
 *
 * Software Name : Cloudnet TOSCA toolbox
 * Version: 1.0
 * SPDX-FileCopyrightText: Copyright (c) 2020-21 Orange
 * SPDX-License-Identifier: Apache-2.0
 *
 * This software is distributed under the Apache License 2.0
 * the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
 * or see the "LICENSE-2.0.txt" file for more details.
 *
 * Author: Philippe Merle (INRIA) <philippe.merle@inria.fr>
 *
 * A formal specification of TOSCA in Alloy with Location Graphs.
 *
*******************************************************************************/

module tosca_simple_yaml_1_0

open LocationGraphs
open TOSCA
// --------------------------------------------------
// TOSCA Topology Metadata
// --------------------------------------------------

// tosca_definitions_version: tosca_simple_yaml_1_0
// description: OASIS TOSCA 1.0 os01 normative types


// --------------------------------------------------
// Data Types
// --------------------------------------------------

//
// The TOSCA root Data Type all other TOSCA base Data Types derive from
//
sig tosca_datatypes_Root extends TOSCA/Data
{
} {
}

/** There exists some tosca.datatypes.Root */
run Show_tosca_datatypes_Root {
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_datatypes_Root
  expect 1

//
// The TOSCA data Type used when describing authorization credentials used to access network accessible resources
//
sig tosca_datatypes_Credential extends tosca_datatypes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML protocol: {'description': 'The optional protocol name', 'type': 'string', 'required': False}
  //
  // The optional protocol name
  //
  protocol: lone string,

  // YAML token_type: {'description': 'The required token type', 'type': 'string', 'default': 'password'}
  //
  // The required token type
  //
  token_type: one string,

  // YAML token: {'description': 'The required token used as a credential for authorization or access to a networked resource', 'type': 'string'}
  //
  // The required token used as a credential for authorization or access to a networked resource
  //
  token: one string,

  // YAML keys: {'description': 'The optional list of protocol-specific keys or assertions', 'type': 'map', 'required': False, 'entry_schema': {'type': 'string'}}
  //
  // The optional list of protocol-specific keys or assertions
  //
  keys: lone TOSCA/map_string/Map,

  // YAML user: {'description': 'The optional user (name or ID) used for non-token based credentials', 'type': 'string', 'required': False}
  //
  // The optional user (name or ID) used for non-token based credentials
  //
  user: lone string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.datatypes.Credential */
run Show_tosca_datatypes_Credential {
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_datatypes_Credential
  expect 1

sig tosca_datatypes_network_NetworkInfo extends tosca_datatypes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML network_name: {'type': 'string'}
  network_name: one string,

  // YAML network_id: {'type': 'string'}
  network_id: one string,

  // YAML addresses: {'type': 'list', 'entry_schema': {'type': 'string'}}
  addresses: seq string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.datatypes.network.NetworkInfo */
run Show_tosca_datatypes_network_NetworkInfo {
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_datatypes_network_NetworkInfo
  expect 1

sig tosca_datatypes_network_PortInfo extends tosca_datatypes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML port_name: {'type': 'string'}
  port_name: one string,

  // YAML port_id: {'type': 'string'}
  port_id: one string,

  // YAML network_id: {'type': 'string'}
  network_id: one string,

  // YAML mac_address: {'type': 'string'}
  mac_address: one string,

  // YAML addresses: {'type': 'list', 'entry_schema': {'type': 'string'}}
  addresses: seq string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.datatypes.network.PortInfo */
run Show_tosca_datatypes_network_PortInfo {
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_datatypes_network_PortInfo
  expect 1

let tosca_datatypes_network_PortDef = integer
sig tosca_datatypes_network_PortSpec extends tosca_datatypes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML protocol: {'type': 'string', 'required': True, 'default': 'tcp', 'constraints': [{'valid_values': ['udp', 'tcp', 'igmp']}]}
  protocol: one string,

  // YAML target: {'type': 'PortDef', 'required': False}
  target: lone tosca_datatypes_network_PortDef,

  // YAML target_range: {'type': 'range', 'required': False, 'constraints': [{'in_range': [1, 65535]}]}
  target_range: lone range,

  // YAML source: {'type': 'PortDef', 'required': False}
  source: lone tosca_datatypes_network_PortDef,

  // YAML source_range: {'type': 'range', 'required': False, 'constraints': [{'in_range': [1, 65535]}]}
  source_range: lone range,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  protocol.valid_values["udp" + "tcp" + "igmp"]
  some target_range implies target_range.in_range[1, 65535]
  some source_range implies source_range.in_range[1, 65535]

}

/** There exists some tosca.datatypes.network.PortSpec */
run Show_tosca_datatypes_network_PortSpec {
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_datatypes_network_PortSpec
  expect 1

// --------------------------------------------------
// Artifact Types
// --------------------------------------------------

//
// The TOSCA Artifact Type all other TOSCA Artifact Types derive from
//
sig tosca_artifacts_Root extends TOSCA/Artifact
{
} {
}

/** There exists some tosca.artifacts.Root */
run Show_tosca_artifacts_Root {
  tosca_artifacts_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Root
  expect 1

sig tosca_artifacts_File extends tosca_artifacts_Root
{
} {
}

/** There exists some tosca.artifacts.File */
run Show_tosca_artifacts_File {
  tosca_artifacts_File.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_File
  expect 1

//
// TOSCA base type for deployment artifacts
//
sig tosca_artifacts_Deployment extends tosca_artifacts_Root
{
} {
}

/** There exists some tosca.artifacts.Deployment */
run Show_tosca_artifacts_Deployment {
  tosca_artifacts_Deployment.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Deployment
  expect 1

sig tosca_artifacts_Deployment_Image extends tosca_artifacts_Deployment
{
} {
}

/** There exists some tosca.artifacts.Deployment.Image */
run Show_tosca_artifacts_Deployment_Image {
  tosca_artifacts_Deployment_Image.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Deployment_Image
  expect 1

//
// Virtual Machine (VM) Image
//
sig tosca_artifacts_Deployment_Image_VM extends tosca_artifacts_Deployment_Image
{
} {
}

/** There exists some tosca.artifacts.Deployment.Image.VM */
run Show_tosca_artifacts_Deployment_Image_VM {
  tosca_artifacts_Deployment_Image_VM.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Deployment_Image_VM
  expect 1

//
// TOSCA base type for implementation artifacts
//
sig tosca_artifacts_Implementation extends tosca_artifacts_Root
{
} {
}

/** There exists some tosca.artifacts.Implementation */
run Show_tosca_artifacts_Implementation {
  tosca_artifacts_Implementation.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Implementation
  expect 1

//
// Script artifact for the Unix Bash shell
//
sig tosca_artifacts_Implementation_Bash extends tosca_artifacts_Implementation
{
} {
  // YAML mime_type: application/x-sh
  mime_type["application/x-sh"]

  // YAML file_ext: ['sh']
  file_ext["sh"]
}

/** There exists some tosca.artifacts.Implementation.Bash */
run Show_tosca_artifacts_Implementation_Bash {
  tosca_artifacts_Implementation_Bash.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Implementation_Bash
  expect 1

//
// Artifact for the interpreted Python language
//
sig tosca_artifacts_Implementation_Python extends tosca_artifacts_Implementation
{
} {
  // YAML mime_type: application/x-python
  mime_type["application/x-python"]

  // YAML file_ext: ['py']
  file_ext["py"]
}

/** There exists some tosca.artifacts.Implementation.Python */
run Show_tosca_artifacts_Implementation_Python {
  tosca_artifacts_Implementation_Python.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_artifacts_Implementation_Python
  expect 1

// --------------------------------------------------
// Capability Types
// --------------------------------------------------

//
// The TOSCA root Capability Type all other TOSCA base Capability Types derive from
//
sig tosca_capabilities_Root extends TOSCA/Capability
{
} {
}

/** There exists some tosca.capabilities.Root */
run Show_tosca_capabilities_Root {
  tosca_capabilities_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Root
  expect 1

sig tosca_capabilities_Node extends tosca_capabilities_Root
{
} {
}

/** There exists some tosca.capabilities.Node */
run Show_tosca_capabilities_Node {
  tosca_capabilities_Node.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Node
  expect 1

sig tosca_capabilities_Network extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML name: {'type': 'string', 'required': False}
  property_name: lone string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.capabilities.Network */
run Show_tosca_capabilities_Network {
  tosca_capabilities_Network.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Network
  expect 1

sig tosca_capabilities_Storage extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML name: {'type': 'string', 'required': False}
  property_name: lone string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.capabilities.Storage */
run Show_tosca_capabilities_Storage {
  tosca_capabilities_Storage.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Storage
  expect 1

sig tosca_capabilities_Container extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML num_cpus: {'type': 'integer', 'required': False, 'constraints': [{'greater_or_equal': 1}]}
  property_num_cpus: lone integer,

  // YAML cpu_frequency: {'type': 'scalar-unit.frequency', 'required': False, 'constraints': [{'greater_or_equal': '0.1 GHz'}]}
  property_cpu_frequency: lone scalar_unit_frequency,

  // YAML disk_size: {'type': 'scalar-unit.size', 'required': False, 'constraints': [{'greater_or_equal': '0 MB'}]}
  property_disk_size: lone scalar_unit_size,

  // YAML mem_size: {'type': 'scalar-unit.size', 'required': False, 'constraints': [{'greater_or_equal': '0 MB'}]}
  property_mem_size: lone scalar_unit_size,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  some property_num_cpus implies property_num_cpus.greater_or_equal[1]
  some property_cpu_frequency implies property_cpu_frequency.greater_or_equal[1, Hz]
  some property_disk_size implies property_disk_size.greater_or_equal[0, MB]
  some property_mem_size implies property_mem_size.greater_or_equal[0, MB]

}

/** There exists some tosca.capabilities.Container */
run Show_tosca_capabilities_Container {
  tosca_capabilities_Container.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Container
  expect 1

sig tosca_capabilities_Endpoint extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML protocol: {'type': 'string', 'required': True, 'default': 'tcp'}
  property_protocol: one string,

  // YAML port: {'type': 'PortDef', 'required': False}
  property_port: lone tosca_datatypes_network_PortDef,

  // YAML secure: {'type': 'boolean', 'required': False, 'default': False}
  property_secure: lone boolean,

  // YAML url_path: {'type': 'string', 'required': False}
  property_url_path: lone string,

  // YAML port_name: {'type': 'string', 'required': False}
  property_port_name: lone string,

  // YAML network_name: {'type': 'string', 'required': False, 'default': 'PRIVATE'}
  property_network_name: lone string,

  // YAML initiator: {'type': 'string', 'required': False, 'default': 'source', 'constraints': [{'valid_values': ['source', 'target', 'peer']}]}
  property_initiator: lone string,

  // YAML ports: {'type': 'map', 'required': False, 'constraints': [{'min_length': 1}], 'entry_schema': {'type': 'PortSpec'}}
  property_ports: lone TOSCA/map_data/Map,

  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------

  // YAML ip_address: {'type': 'string'}
  attribute_ip_address: one string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_initiator.valid_values["source" + "target" + "peer"]
  some property_ports implies property_ports.min_length[1]

  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------


}

/** There exists some tosca.capabilities.Endpoint */
run Show_tosca_capabilities_Endpoint {
  tosca_capabilities_Endpoint.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Endpoint
  expect 1

sig tosca_capabilities_Endpoint_Public extends tosca_capabilities_Endpoint
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML network_name: {'type': 'string', 'default': 'PUBLIC', 'constraints': [{'equal': 'PUBLIC'}]}
  // NOTE: network_name overloaded

  // YAML floating: {'description': 'Indicates that the public address should be allocated from a pool of floating IPs that are associated with the network.', 'type': 'boolean', 'default': False, 'status': 'experimental'}
  //
  // Indicates that the public address should be allocated from a pool of floating IPs that are associated with the network.
  //
  property_floating: one boolean,

  // YAML dns_name: {'description': 'The optional name to register with DNS', 'type': 'string', 'required': False, 'status': 'experimental'}
  //
  // The optional name to register with DNS
  //
  property_dns_name: lone string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_network_name.equal["PUBLIC"]

}

/** There exists some tosca.capabilities.Endpoint.Public */
run Show_tosca_capabilities_Endpoint_Public {
  tosca_capabilities_Endpoint_Public.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Endpoint_Public
  expect 1

sig tosca_capabilities_Endpoint_Admin extends tosca_capabilities_Endpoint
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML secure: {'type': 'boolean', 'default': True, 'constraints': [{'equal': True}]}
  // NOTE: secure overloaded

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_secure.equal[true]

}

/** There exists some tosca.capabilities.Endpoint.Admin */
run Show_tosca_capabilities_Endpoint_Admin {
  tosca_capabilities_Endpoint_Admin.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Endpoint_Admin
  expect 1

sig tosca_capabilities_Endpoint_Database extends tosca_capabilities_Endpoint
{
} {
}

/** There exists some tosca.capabilities.Endpoint.Database */
run Show_tosca_capabilities_Endpoint_Database {
  tosca_capabilities_Endpoint_Database.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Endpoint_Database
  expect 1

sig tosca_capabilities_Attachment extends tosca_capabilities_Root
{
} {
}

/** There exists some tosca.capabilities.Attachment */
run Show_tosca_capabilities_Attachment {
  tosca_capabilities_Attachment.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Attachment
  expect 1

sig tosca_capabilities_OperatingSystem extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML architecture: {'type': 'string', 'required': False}
  property_architecture: lone string,

  // YAML type: {'type': 'string', 'required': False}
  property_type: lone string,

  // YAML distribution: {'type': 'string', 'required': False}
  property_distribution: lone string,

  // YAML version: {'type': 'version', 'required': False}
  property_version: lone version,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


}

/** There exists some tosca.capabilities.OperatingSystem */
run Show_tosca_capabilities_OperatingSystem {
  tosca_capabilities_OperatingSystem.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_OperatingSystem
  expect 1

sig tosca_capabilities_Scalable extends tosca_capabilities_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML min_instances: {'type': 'integer', 'default': 1, 'constraints': [{'greater_or_equal': 1}]}
  property_min_instances: one integer,

  // YAML max_instances: {'type': 'integer', 'default': 1, 'constraints': [{'greater_or_equal': 1}]}
  property_max_instances: one integer,

  // YAML default_instances: {'required': False, 'type': 'integer', 'constraints': [{'greater_or_equal': 1}]}
  property_default_instances: lone integer,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_min_instances.greater_or_equal[1]
  property_max_instances.greater_or_equal[1]
  some property_default_instances implies property_default_instances.greater_or_equal[1]

}

/** There exists some tosca.capabilities.Scalable */
run Show_tosca_capabilities_Scalable {
  tosca_capabilities_Scalable.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_Scalable
  expect 1

sig tosca_capabilities_network_Bindable extends tosca_capabilities_Node
{
} {
}

/** There exists some tosca.capabilities.network.Bindable */
run Show_tosca_capabilities_network_Bindable {
  tosca_capabilities_network_Bindable.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_network_Bindable
  expect 1

sig tosca_capabilities_network_Linkable extends tosca_capabilities_Node
{
} {
}

/** There exists some tosca.capabilities.network.Linkable */
run Show_tosca_capabilities_network_Linkable {
  tosca_capabilities_network_Linkable.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 1 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Interface,
  exactly 0 TOSCA/Requirement,
  exactly 0 TOSCA/Operation,
  exactly 1 tosca_capabilities_network_Linkable
  expect 1

// --------------------------------------------------
// Relationship Types
// --------------------------------------------------

//
// The TOSCA root Relationship Type all other TOSCA base Relationship Types derive from
//
sig tosca_relationships_Root extends TOSCA/Relationship
{
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------

  // YAML tosca_id: {'type': 'string'}
  attribute_tosca_id: one string,

  // YAML tosca_name: {'type': 'string'}
  attribute_tosca_name: one string,


  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Configure: {'type': 'tosca.interfaces.relationship.Configure'}
  interface_Configure: one tosca_interfaces_relationship_Configure,

} {
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------



  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Configure: {'type': 'tosca.interfaces.relationship.Configure'}
  interface[interface_Configure]
  interface_Configure.name["Configure"]

}

/** There exists some tosca.relationships.Root */
run Show_tosca_relationships_Root {
  tosca_relationships_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_Root
  expect 1

sig tosca_relationships_DependsOn extends tosca_relationships_Root
{
} {
  valid_target_types[tosca_capabilities_Node]
}

/** There exists some tosca.relationships.DependsOn */
run Show_tosca_relationships_DependsOn {
  tosca_relationships_DependsOn.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_DependsOn
  expect 1

sig tosca_relationships_HostedOn extends tosca_relationships_Root
{
} {
  valid_target_types[tosca_capabilities_Container]
}

/** There exists some tosca.relationships.HostedOn */
run Show_tosca_relationships_HostedOn {
  tosca_relationships_HostedOn.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_HostedOn
  expect 1

sig tosca_relationships_ConnectsTo extends tosca_relationships_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML credential: {'type': 'tosca.datatypes.Credential', 'required': False}
  property_credential: lone tosca_datatypes_Credential,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  valid_target_types[tosca_capabilities_Endpoint]
}

/** There exists some tosca.relationships.ConnectsTo */
run Show_tosca_relationships_ConnectsTo {
  tosca_relationships_ConnectsTo.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_ConnectsTo
  expect 1

sig tosca_relationships_AttachesTo extends tosca_relationships_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML location: {'type': 'string', 'constraints': [{'min_length': 1}]}
  property_location: one string,

  // YAML device: {'type': 'string', 'required': False}
  property_device: lone string,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_location.min_length[1]

  valid_target_types[tosca_capabilities_Attachment]
}

/** There exists some tosca.relationships.AttachesTo */
run Show_tosca_relationships_AttachesTo {
  tosca_relationships_AttachesTo.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_AttachesTo
  expect 1

sig tosca_relationships_RoutesTo extends tosca_relationships_ConnectsTo
{
} {
  valid_target_types[tosca_capabilities_Endpoint]
}

/** There exists some tosca.relationships.RoutesTo */
run Show_tosca_relationships_RoutesTo {
  tosca_relationships_RoutesTo.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_RoutesTo
  expect 1

sig tosca_relationships_network_LinksTo extends tosca_relationships_DependsOn
{
} {
  valid_target_types[tosca_capabilities_network_Linkable]
}

/** There exists some tosca.relationships.network.LinksTo */
run Show_tosca_relationships_network_LinksTo {
  tosca_relationships_network_LinksTo.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_network_LinksTo
  expect 1

sig tosca_relationships_network_BindsTo extends tosca_relationships_DependsOn
{
} {
  valid_target_types[tosca_capabilities_network_Bindable]
}

/** There exists some tosca.relationships.network.BindsTo */
run Show_tosca_relationships_network_BindsTo {
  tosca_relationships_network_BindsTo.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_relationships_network_BindsTo
  expect 1

// --------------------------------------------------
// Interface Types
// --------------------------------------------------

//
// The TOSCA root Interface Type all other TOSCA base Interface Types derive from
//
sig tosca_interfaces_Root extends TOSCA/Interface
{
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

} {
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

}

/** There exists some tosca.interfaces.Root */
run Show_tosca_interfaces_Root {
  tosca_interfaces_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 0 TOSCA/Operation,
  exactly 8 TOSCA/Parameter,
  exactly 1 tosca_interfaces_Root
  expect 1

sig tosca_interfaces_node_lifecycle_Standard extends tosca_interfaces_Root
{
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

  // YAML create: {'description': 'Standard lifecycle create operation.'}
  //
  // Standard lifecycle create operation.
  //
  operation_create: one TOSCA/Operation,

  // YAML configure: {'description': 'Standard lifecycle configure operation.'}
  //
  // Standard lifecycle configure operation.
  //
  operation_configure: one TOSCA/Operation,

  // YAML start: {'description': 'Standard lifecycle start operation.'}
  //
  // Standard lifecycle start operation.
  //
  operation_start: one TOSCA/Operation,

  // YAML stop: {'description': 'Standard lifecycle stop operation.'}
  //
  // Standard lifecycle stop operation.
  //
  operation_stop: one TOSCA/Operation,

  // YAML delete: {'description': 'Standard lifecycle delete operation.'}
  //
  // Standard lifecycle delete operation.
  //
  operation_delete: one TOSCA/Operation,

} {
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

  // YAML create: {'description': 'Standard lifecycle create operation.'}
  //
  // Standard lifecycle create operation.
  //
  operation_create.name["create"]
  operation[operation_create]

  // YAML configure: {'description': 'Standard lifecycle configure operation.'}
  //
  // Standard lifecycle configure operation.
  //
  operation_configure.name["configure"]
  operation[operation_configure]

  // YAML start: {'description': 'Standard lifecycle start operation.'}
  //
  // Standard lifecycle start operation.
  //
  operation_start.name["start"]
  operation[operation_start]

  // YAML stop: {'description': 'Standard lifecycle stop operation.'}
  //
  // Standard lifecycle stop operation.
  //
  operation_stop.name["stop"]
  operation[operation_stop]

  // YAML delete: {'description': 'Standard lifecycle delete operation.'}
  //
  // Standard lifecycle delete operation.
  //
  operation_delete.name["delete"]
  operation[operation_delete]

}

/** There exists some tosca.interfaces.node.lifecycle.Standard */
run Show_tosca_interfaces_node_lifecycle_Standard {
  tosca_interfaces_node_lifecycle_Standard.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 5 TOSCA/Operation,
  exactly 8 TOSCA/Parameter,
  exactly 1 tosca_interfaces_node_lifecycle_Standard
  expect 1

sig tosca_interfaces_relationship_Configure extends tosca_interfaces_Root
{
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

  // YAML pre_configure_source: {'description': 'Operation to pre-configure the source endpoint.'}
  //
  // Operation to pre-configure the source endpoint.
  //
  operation_pre_configure_source: one TOSCA/Operation,

  // YAML pre_configure_target: {'description': 'Operation to pre-configure the target endpoint.'}
  //
  // Operation to pre-configure the target endpoint.
  //
  operation_pre_configure_target: one TOSCA/Operation,

  // YAML post_configure_source: {'description': 'Operation to post-configure the source endpoint.'}
  //
  // Operation to post-configure the source endpoint.
  //
  operation_post_configure_source: one TOSCA/Operation,

  // YAML post_configure_target: {'description': 'Operation to post-configure the target endpoint.'}
  //
  // Operation to post-configure the target endpoint.
  //
  operation_post_configure_target: one TOSCA/Operation,

  // YAML add_target: {'description': 'Operation to notify the source node of a target node being added via a relationship.'}
  //
  // Operation to notify the source node of a target node being added via a relationship.
  //
  operation_add_target: one TOSCA/Operation,

  // YAML add_source: {'description': 'Operation to notify the target node of a source node which is now available via a relationship.'}
  //
  // Operation to notify the target node of a source node which is now available via a relationship.
  //
  operation_add_source: one TOSCA/Operation,

  // YAML target_changed: {'description': 'Operation to notify source some property or attribute of the target changed'}
  //
  // Operation to notify source some property or attribute of the target changed
  //
  operation_target_changed: one TOSCA/Operation,

  // YAML remove_target: {'description': 'Operation to remove a target node.'}
  //
  // Operation to remove a target node.
  //
  operation_remove_target: one TOSCA/Operation,

} {
  // --------------------------------------------------
  // Operations
  // --------------------------------------------------

  // YAML pre_configure_source: {'description': 'Operation to pre-configure the source endpoint.'}
  //
  // Operation to pre-configure the source endpoint.
  //
  operation_pre_configure_source.name["pre_configure_source"]
  operation[operation_pre_configure_source]

  // YAML pre_configure_target: {'description': 'Operation to pre-configure the target endpoint.'}
  //
  // Operation to pre-configure the target endpoint.
  //
  operation_pre_configure_target.name["pre_configure_target"]
  operation[operation_pre_configure_target]

  // YAML post_configure_source: {'description': 'Operation to post-configure the source endpoint.'}
  //
  // Operation to post-configure the source endpoint.
  //
  operation_post_configure_source.name["post_configure_source"]
  operation[operation_post_configure_source]

  // YAML post_configure_target: {'description': 'Operation to post-configure the target endpoint.'}
  //
  // Operation to post-configure the target endpoint.
  //
  operation_post_configure_target.name["post_configure_target"]
  operation[operation_post_configure_target]

  // YAML add_target: {'description': 'Operation to notify the source node of a target node being added via a relationship.'}
  //
  // Operation to notify the source node of a target node being added via a relationship.
  //
  operation_add_target.name["add_target"]
  operation[operation_add_target]

  // YAML add_source: {'description': 'Operation to notify the target node of a source node which is now available via a relationship.'}
  //
  // Operation to notify the target node of a source node which is now available via a relationship.
  //
  operation_add_source.name["add_source"]
  operation[operation_add_source]

  // YAML target_changed: {'description': 'Operation to notify source some property or attribute of the target changed'}
  //
  // Operation to notify source some property or attribute of the target changed
  //
  operation_target_changed.name["target_changed"]
  operation[operation_target_changed]

  // YAML remove_target: {'description': 'Operation to remove a target node.'}
  //
  // Operation to remove a target node.
  //
  operation_remove_target.name["remove_target"]
  operation[operation_remove_target]

}

/** There exists some tosca.interfaces.relationship.Configure */
run Show_tosca_interfaces_relationship_Configure {
  tosca_interfaces_relationship_Configure.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 0 LocationGraphs/Location,
  exactly 0 LocationGraphs/Name,
  exactly 0 LocationGraphs/Role,
  exactly 0 LocationGraphs/Process,
  exactly 0 LocationGraphs/Sort,
  exactly 0 TOSCA/Artifact,
  exactly 0 TOSCA/Attribute,
  exactly 8 TOSCA/Operation,
  exactly 8 TOSCA/Parameter,
  exactly 1 tosca_interfaces_relationship_Configure
  expect 1

// --------------------------------------------------
// Node Types
// --------------------------------------------------

//
// The TOSCA Node Type all other TOSCA base Node Types derive from
//
sig tosca_nodes_Root extends TOSCA/Node
{
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------

  // YAML tosca_id: {'type': 'string'}
  attribute_tosca_id: one string,

  // YAML tosca_name: {'type': 'string'}
  attribute_tosca_name: one string,

  // YAML state: {'type': 'string'}
  attribute_state: one string,


  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Standard: {'type': 'tosca.interfaces.node.lifecycle.Standard'}
  interface_Standard: one tosca_interfaces_node_lifecycle_Standard,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML feature: {'type': 'tosca.capabilities.Node'}
  capability_feature: some tosca_capabilities_Node,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML dependency: {'capability': 'tosca.capabilities.Node', 'node': 'tosca.nodes.Root', 'relationship': 'tosca.relationships.DependsOn', 'occurrences': [0, 'UNBOUNDED']}
  requirement_dependency: set TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------




  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Standard: {'type': 'tosca.interfaces.node.lifecycle.Standard'}
  interface[interface_Standard]
  interface_Standard.name["Standard"]

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML feature: {'type': 'tosca.capabilities.Node'}
  capability_feature.name["feature"]
  capability[capability_feature]

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML dependency: {'capability': 'tosca.capabilities.Node', 'node': 'tosca.nodes.Root', 'relationship': 'tosca.relationships.DependsOn', 'occurrences': [0, 'UNBOUNDED']}
  requirement["dependency", requirement_dependency]
  requirement_dependency.capability[tosca_capabilities_Node]
  requirement_dependency.relationship[tosca_relationships_DependsOn]
  requirement_dependency.node[tosca_nodes_Root]
  // YAML occurrences: [0, 'UNBOUNDED']

}

/** There exists some tosca.nodes.Root */
run Show_tosca_nodes_Root {
  tosca_nodes_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_Root
  expect 1

sig tosca_nodes_Compute extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------

  // YAML private_address: {'type': 'string'}
  attribute_private_address: one string,

  // YAML public_address: {'type': 'string'}
  attribute_public_address: one string,

  // YAML networks: {'type': 'map', 'entry_schema': {'type': 'tosca.datatypes.network.NetworkInfo'}}
  attribute_networks: one TOSCA/map_data/Map,

  // YAML ports: {'type': 'map', 'entry_schema': {'type': 'tosca.datatypes.network.PortInfo'}}
  attribute_ports: one TOSCA/map_data/Map,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.SoftwareComponent']}
  capability_host: some tosca_capabilities_Container,

  // YAML endpoint: {'type': 'tosca.capabilities.Endpoint.Admin'}
  capability_endpoint: some tosca_capabilities_Endpoint_Admin,

  // YAML os: {'type': 'tosca.capabilities.OperatingSystem'}
  capability_os: some tosca_capabilities_OperatingSystem,

  // YAML scalable: {'type': 'tosca.capabilities.Scalable'}
  capability_scalable: some tosca_capabilities_Scalable,

  // YAML binding: {'type': 'tosca.capabilities.network.Bindable'}
  capability_binding: some tosca_capabilities_network_Bindable,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML local_storage: {'capability': 'tosca.capabilities.Attachment', 'node': 'tosca.nodes.BlockStorage', 'relationship': 'tosca.relationships.AttachesTo', 'occurrences': [0, 'UNBOUNDED']}
  requirement_local_storage: set TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Attributes
  // --------------------------------------------------





  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.SoftwareComponent']}
  capability_host.name["host"]
  capability[capability_host]
  capability_host.valid_source_types[tosca_nodes_SoftwareComponent]

  // YAML endpoint: {'type': 'tosca.capabilities.Endpoint.Admin'}
  capability_endpoint.name["endpoint"]
  capability[capability_endpoint]

  // YAML os: {'type': 'tosca.capabilities.OperatingSystem'}
  capability_os.name["os"]
  capability[capability_os]

  // YAML scalable: {'type': 'tosca.capabilities.Scalable'}
  capability_scalable.name["scalable"]
  capability[capability_scalable]

  // YAML binding: {'type': 'tosca.capabilities.network.Bindable'}
  capability_binding.name["binding"]
  capability[capability_binding]

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML local_storage: {'capability': 'tosca.capabilities.Attachment', 'node': 'tosca.nodes.BlockStorage', 'relationship': 'tosca.relationships.AttachesTo', 'occurrences': [0, 'UNBOUNDED']}
  requirement["local_storage", requirement_local_storage]
  requirement_local_storage.capability[tosca_capabilities_Attachment]
  requirement_local_storage.relationship[tosca_relationships_AttachesTo]
  requirement_local_storage.node[tosca_nodes_BlockStorage]
  // YAML occurrences: [0, 'UNBOUNDED']

}

/** There exists some tosca.nodes.Compute */
run Show_tosca_nodes_Compute {
  tosca_nodes_Compute.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_Compute
  expect 1

sig tosca_nodes_SoftwareComponent extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML component_version: {'type': 'version', 'required': False}
  property_component_version: lone version,

  // YAML admin_credential: {'type': 'tosca.datatypes.Credential', 'required': False}
  property_admin_credential: lone tosca_datatypes_Credential,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.Compute', 'relationship': 'tosca.relationships.HostedOn'}
  requirement_host: one TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.Compute', 'relationship': 'tosca.relationships.HostedOn'}
  requirement["host", requirement_host]
  requirement_host.capability[tosca_capabilities_Container]
  requirement_host.relationship[tosca_relationships_HostedOn]
  requirement_host.node[tosca_nodes_Compute]

}

/** There exists some tosca.nodes.SoftwareComponent */
run Show_tosca_nodes_SoftwareComponent {
  tosca_nodes_SoftwareComponent.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 3 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_SoftwareComponent
  expect 1

sig tosca_nodes_WebServer extends tosca_nodes_SoftwareComponent
{
  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML data_endpoint: tosca.capabilities.Endpoint
  capability_data_endpoint: some tosca_capabilities_Endpoint,

  // YAML admin_endpoint: tosca.capabilities.Endpoint.Admin
  capability_admin_endpoint: some tosca_capabilities_Endpoint_Admin,

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.WebApplication']}
  capability_host: some tosca_capabilities_Container,

} {
  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML data_endpoint: tosca.capabilities.Endpoint
  capability_data_endpoint.name["data_endpoint"]
  capability[capability_data_endpoint]

  // YAML admin_endpoint: tosca.capabilities.Endpoint.Admin
  capability_admin_endpoint.name["admin_endpoint"]
  capability[capability_admin_endpoint]

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.WebApplication']}
  capability_host.name["host"]
  capability[capability_host]
  capability_host.valid_source_types[tosca_nodes_WebApplication]

}

/** There exists some tosca.nodes.WebServer */
run Show_tosca_nodes_WebServer {
  tosca_nodes_WebServer.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 3 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_WebServer
  expect 1

sig tosca_nodes_WebApplication extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML context_root: {'type': 'string', 'required': False}
  property_context_root: lone string,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML app_endpoint: {'type': 'tosca.capabilities.Endpoint'}
  capability_app_endpoint: some tosca_capabilities_Endpoint,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.WebServer', 'relationship': 'tosca.relationships.HostedOn'}
  requirement_host: one TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML app_endpoint: {'type': 'tosca.capabilities.Endpoint'}
  capability_app_endpoint.name["app_endpoint"]
  capability[capability_app_endpoint]

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.WebServer', 'relationship': 'tosca.relationships.HostedOn'}
  requirement["host", requirement_host]
  requirement_host.capability[tosca_capabilities_Container]
  requirement_host.relationship[tosca_relationships_HostedOn]
  requirement_host.node[tosca_nodes_WebServer]

}

/** There exists some tosca.nodes.WebApplication */
run Show_tosca_nodes_WebApplication {
  tosca_nodes_WebApplication.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 5 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 5 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_WebApplication
  expect 1

sig tosca_nodes_DBMS extends tosca_nodes_SoftwareComponent
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML root_password: {'type': 'string', 'required': False, 'description': 'the optional root password for the DBMS service'}
  //
  // the optional root password for the DBMS service
  //
  property_root_password: lone string,

  // YAML port: {'type': 'integer', 'required': False, 'description': 'the port the DBMS service will listen to for data and requests'}
  //
  // the port the DBMS service will listen to for data and requests
  //
  property_port: lone integer,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.Database']}
  capability_host: some tosca_capabilities_Container,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.Database']}
  capability_host.name["host"]
  capability[capability_host]
  capability_host.valid_source_types[tosca_nodes_Database]

}

/** There exists some tosca.nodes.DBMS */
run Show_tosca_nodes_DBMS {
  tosca_nodes_DBMS.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 3 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_DBMS
  expect 1

sig tosca_nodes_Database extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML name: {'type': 'string', 'description': 'the logical name of the database'}
  //
  // the logical name of the database
  //
  property_name: one string,

  // YAML port: {'type': 'integer', 'description': 'the port the underlying database service will listen to for data', 'required': False}
  //
  // the port the underlying database service will listen to for data
  //
  property_port: lone integer,

  // YAML user: {'type': 'string', 'description': 'the optional user account name for DB administration', 'required': False}
  //
  // the optional user account name for DB administration
  //
  property_user: lone string,

  // YAML password: {'type': 'string', 'description': 'the optional password for the DB user account', 'required': False}
  //
  // the optional password for the DB user account
  //
  property_password: lone string,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML database_endpoint: {'type': 'tosca.capabilities.Endpoint.Database'}
  capability_database_endpoint: some tosca_capabilities_Endpoint_Database,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.DBMS', 'relationship': 'tosca.relationships.HostedOn'}
  requirement_host: one TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML database_endpoint: {'type': 'tosca.capabilities.Endpoint.Database'}
  capability_database_endpoint.name["database_endpoint"]
  capability[capability_database_endpoint]

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.DBMS', 'relationship': 'tosca.relationships.HostedOn'}
  requirement["host", requirement_host]
  requirement_host.capability[tosca_capabilities_Container]
  requirement_host.relationship[tosca_relationships_HostedOn]
  requirement_host.node[tosca_nodes_DBMS]

}

/** There exists some tosca.nodes.Database */
run Show_tosca_nodes_Database {
  tosca_nodes_Database.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 5 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 5 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_Database
  expect 1

sig tosca_nodes_ObjectStorage extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML name: {'type': 'string'}
  property_name: one string,

  // YAML size: {'type': 'scalar-unit.size', 'constraints': [{'greater_or_equal': '0 GB'}], 'required': False}
  property_size: lone scalar_unit_size,

  // YAML maxsize: {'type': 'scalar-unit.size', 'constraints': [{'greater_or_equal': '0 GB'}], 'required': False}
  property_maxsize: lone scalar_unit_size,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML storage_endpoint: {'type': 'tosca.capabilities.Endpoint'}
  capability_storage_endpoint: some tosca_capabilities_Endpoint,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  some property_size implies property_size.greater_or_equal[0, GB]
  some property_maxsize implies property_maxsize.greater_or_equal[0, GB]

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML storage_endpoint: {'type': 'tosca.capabilities.Endpoint'}
  capability_storage_endpoint.name["storage_endpoint"]
  capability[capability_storage_endpoint]

}

/** There exists some tosca.nodes.ObjectStorage */
run Show_tosca_nodes_ObjectStorage {
  tosca_nodes_ObjectStorage.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_ObjectStorage
  expect 1

sig tosca_nodes_BlockStorage extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML size: {'type': 'scalar-unit.size', 'constraints': [{'greater_or_equal': '1 MB'}]}
  property_size: one scalar_unit_size,

  // YAML volume_id: {'type': 'string', 'required': False}
  property_volume_id: lone string,

  // YAML snapshot_id: {'type': 'string', 'required': False}
  property_snapshot_id: lone string,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML attachment: {'type': 'tosca.capabilities.Attachment'}
  capability_attachment: some tosca_capabilities_Attachment,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_size.greater_or_equal[1, MB]

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML attachment: {'type': 'tosca.capabilities.Attachment'}
  capability_attachment.name["attachment"]
  capability[capability_attachment]

}

/** There exists some tosca.nodes.BlockStorage */
run Show_tosca_nodes_BlockStorage {
  tosca_nodes_BlockStorage.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_BlockStorage
  expect 1

sig tosca_nodes_Container_Runtime extends tosca_nodes_SoftwareComponent
{
  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.Container.Application']}
  capability_host: some tosca_capabilities_Container,

  // YAML scalable: {'type': 'tosca.capabilities.Scalable'}
  capability_scalable: some tosca_capabilities_Scalable,

} {
  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML host: {'type': 'tosca.capabilities.Container', 'valid_source_types': ['tosca.nodes.Container.Application']}
  capability_host.name["host"]
  capability[capability_host]
  capability_host.valid_source_types[tosca_nodes_Container_Application]

  // YAML scalable: {'type': 'tosca.capabilities.Scalable'}
  capability_scalable.name["scalable"]
  capability[capability_scalable]

}

/** There exists some tosca.nodes.Container.Runtime */
run Show_tosca_nodes_Container_Runtime {
  tosca_nodes_Container_Runtime.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 3 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_Container_Runtime
  expect 1

sig tosca_nodes_Container_Application extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.Container.Runtime', 'relationship': 'tosca.relationships.HostedOn'}
  requirement_host: one TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML host: {'capability': 'tosca.capabilities.Container', 'node': 'tosca.nodes.Container.Runtime', 'relationship': 'tosca.relationships.HostedOn'}
  requirement["host", requirement_host]
  requirement_host.capability[tosca_capabilities_Container]
  requirement_host.relationship[tosca_relationships_HostedOn]
  requirement_host.node[tosca_nodes_Container_Runtime]

}

/** There exists some tosca.nodes.Container.Application */
run Show_tosca_nodes_Container_Application {
  tosca_nodes_Container_Application.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 5 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 5 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_Container_Application
  expect 1

sig tosca_nodes_LoadBalancer extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML algorithm: {'type': 'string', 'required': False, 'status': 'experimental'}
  property_algorithm: lone string,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML client: {'type': 'tosca.capabilities.Endpoint.Public', 'occurrences': [0, 'UNBOUNDED'], 'description': 'The Floating (IP) client’s on the public network can connect to'}
  //
  // The Floating (IP) client’s on the public network can connect to
  //
  capability_client: set tosca_capabilities_Endpoint_Public,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML application: {'capability': 'tosca.capabilities.Endpoint', 'relationship': 'tosca.relationships.RoutesTo', 'occurrences': [0, 'UNBOUNDED'], 'description': 'Connection to one or more load balanced applications'}
  //
  // Connection to one or more load balanced applications
  //
  requirement_application: set TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------


  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  //
  // The Floating (IP) client’s on the public network can connect to
  //
  // YAML client: {'type': 'tosca.capabilities.Endpoint.Public', 'occurrences': [0, 'UNBOUNDED'], 'description': 'The Floating (IP) client’s on the public network can connect to'}
  capability_client.name["client"]
  capability[capability_client]
  // YAML occurrences: [0, 'UNBOUNDED']

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML application: {'capability': 'tosca.capabilities.Endpoint', 'relationship': 'tosca.relationships.RoutesTo', 'occurrences': [0, 'UNBOUNDED'], 'description': 'Connection to one or more load balanced applications'}
  //
  // Connection to one or more load balanced applications
  //
  requirement["application", requirement_application]
  requirement_application.capability[tosca_capabilities_Endpoint]
  requirement_application.relationship[tosca_relationships_RoutesTo]
  // YAML occurrences: [0, 'UNBOUNDED']

}

/** There exists some tosca.nodes.LoadBalancer */
run Show_tosca_nodes_LoadBalancer {
  tosca_nodes_LoadBalancer.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_LoadBalancer
  expect 1

sig tosca_nodes_network_Network extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML ip_version: {'type': 'integer', 'required': False, 'default': 4, 'constraints': [{'valid_values': [4, 6]}]}
  property_ip_version: lone integer,

  // YAML cidr: {'type': 'string', 'required': False}
  property_cidr: lone string,

  // YAML start_ip: {'type': 'string', 'required': False}
  property_start_ip: lone string,

  // YAML end_ip: {'type': 'string', 'required': False}
  property_end_ip: lone string,

  // YAML gateway_ip: {'type': 'string', 'required': False}
  property_gateway_ip: lone string,

  // YAML network_name: {'type': 'string', 'required': False}
  property_network_name: lone string,

  // YAML network_id: {'type': 'string', 'required': False}
  property_network_id: lone string,

  // YAML segmentation_id: {'type': 'string', 'required': False}
  property_segmentation_id: lone string,

  // YAML network_type: {'type': 'string', 'required': False}
  property_network_type: lone string,

  // YAML physical_network: {'type': 'string', 'required': False}
  property_physical_network: lone string,

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML link: {'type': 'tosca.capabilities.network.Linkable'}
  capability_link: some tosca_capabilities_network_Linkable,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_ip_version.valid_values[4 + 6]

  // --------------------------------------------------
  // Capabilities
  // --------------------------------------------------

  // YAML link: {'type': 'tosca.capabilities.network.Linkable'}
  capability_link.name["link"]
  capability[capability_link]

}

/** There exists some tosca.nodes.network.Network */
run Show_tosca_nodes_network_Network {
  tosca_nodes_network_Network.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_network_Network
  expect 1

sig tosca_nodes_network_Port extends tosca_nodes_Root
{
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  // YAML ip_address: {'type': 'string', 'required': False}
  property_ip_address: lone string,

  // YAML order: {'type': 'integer', 'required': True, 'default': 0, 'constraints': [{'greater_or_equal': 0}]}
  property_order: one integer,

  // YAML is_default: {'type': 'boolean', 'required': False, 'default': False}
  property_is_default: lone boolean,

  // YAML ip_range_start: {'type': 'string', 'required': False}
  property_ip_range_start: lone string,

  // YAML ip_range_end: {'type': 'string', 'required': False}
  property_ip_range_end: lone string,

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML link: {'capability': 'tosca.capabilities.network.Linkable', 'relationship': 'tosca.relationships.network.LinksTo'}
  requirement_link: one TOSCA/Requirement,

  // YAML binding: {'capability': 'tosca.capabilities.network.Bindable', 'relationship': 'tosca.relationships.network.BindsTo'}
  requirement_binding: one TOSCA/Requirement,

} {
  // --------------------------------------------------
  // Properties
  // --------------------------------------------------

  property_order.greater_or_equal[0]

  // --------------------------------------------------
  // Requirements
  // --------------------------------------------------

  // YAML link: {'capability': 'tosca.capabilities.network.Linkable', 'relationship': 'tosca.relationships.network.LinksTo'}
  requirement["link", requirement_link]
  requirement_link.capability[tosca_capabilities_network_Linkable]
  requirement_link.relationship[tosca_relationships_network_LinksTo]

  // YAML binding: {'capability': 'tosca.capabilities.network.Bindable', 'relationship': 'tosca.relationships.network.BindsTo'}
  requirement["binding", requirement_binding]
  requirement_binding.capability[tosca_capabilities_network_Bindable]
  requirement_binding.relationship[tosca_relationships_network_BindsTo]

}

/** There exists some tosca.nodes.network.Port */
run Show_tosca_nodes_network_Port {
  tosca_nodes_network_Port.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 3 LocationGraphs/Location,
  exactly 35 LocationGraphs/Value,
  exactly 3 LocationGraphs/Name,
  exactly 1 LocationGraphs/Sort,
  exactly 1 LocationGraphs/Process,
  exactly 0 TOSCA/Group,
  exactly 0 TOSCA/Policy,
  exactly 1 tosca_nodes_network_Port
  expect 1

// --------------------------------------------------
// Group Types
// --------------------------------------------------

//
// The TOSCA Group Type all other TOSCA Group Types derive from
//
sig tosca_groups_Root extends TOSCA/Group
{

  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Standard: {'type': 'tosca.interfaces.node.lifecycle.Standard'}
  interface_Standard: one tosca_interfaces_node_lifecycle_Standard,

} {
  // --------------------------------------------------
  // Interfaces
  // --------------------------------------------------

  // YAML Standard: {'type': 'tosca.interfaces.node.lifecycle.Standard'}
  interface[interface_Standard]
  interface_Standard.name["Standard"]

}

/** There exists some tosca.groups.Root */
run Show_tosca_groups_Root {
  tosca_groups_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_groups_Root
  expect 1

// --------------------------------------------------
// Policy Types
// --------------------------------------------------

//
// The TOSCA Policy Type all other TOSCA Policy Types derive from
//
sig tosca_policies_Root extends TOSCA/Policy
{
} {
}

/** There exists some tosca.policies.Root */
run Show_tosca_policies_Root {
  tosca_policies_Root.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_policies_Root
  expect 1

//
// The TOSCA Policy Type definition that is used to govern placement of TOSCA nodes or groups of nodes.
//
sig tosca_policies_Placement extends tosca_policies_Root
{
} {
}

/** There exists some tosca.policies.Placement */
run Show_tosca_policies_Placement {
  tosca_policies_Placement.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_policies_Placement
  expect 1

//
// The TOSCA Policy Type definition that is used to govern scaling of TOSCA nodes or groups of nodes.
//
sig tosca_policies_Scaling extends tosca_policies_Root
{
} {
}

/** There exists some tosca.policies.Scaling */
run Show_tosca_policies_Scaling {
  tosca_policies_Scaling.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_policies_Scaling
  expect 1

//
// The TOSCA Policy Type definition that is used to govern update of TOSCA nodes or groups of nodes.
//
sig tosca_policies_Update extends tosca_policies_Root
{
} {
}

/** There exists some tosca.policies.Update */
run Show_tosca_policies_Update {
  tosca_policies_Update.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_policies_Update
  expect 1

//
// The TOSCA Policy Type definition that is used to declare performance requirements for TOSCA nodes or groups of nodes.
//
sig tosca_policies_Performance extends tosca_policies_Root
{
} {
}

/** There exists some tosca.policies.Performance */
run Show_tosca_policies_Performance {
  tosca_policies_Performance.no_name[]
} for 5 but
  8 Int,
  5 seq,
  // NOTE: Setting following scopes strongly reduces the research space.
  exactly 0 LocationGraphs/LocationGraph,
  exactly 1 LocationGraphs/Location,
  exactly 1 LocationGraphs/Name,
  exactly 1 LocationGraphs/Process,
  exactly 1 LocationGraphs/Sort,
  exactly 1 tosca_policies_Performance
  expect 1

