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

module tosca_simple_yaml_1_1

open LocationGraphs as LG
open TOSCA as TOSCA
// --------------------------------------------------
// TOSCA Topology Metadata
// --------------------------------------------------

// tosca_definitions_version: tosca_simple_yaml_1_1
// description: OASIS TOSCA 1.1 os normative types


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

