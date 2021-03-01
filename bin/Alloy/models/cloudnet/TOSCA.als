/******************************************************************************
 *
 * Software Name : Cloudnet TOSCA toolbox
 * Version: 1.0
 * SPDX-FileCopyrightText: Copyright (c) 2020 Orange
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

module TOSCA

open LocationGraphs as LG

/** Definition for maps. */
open map[Int] as map_integer
open map[String] as map_string
open map[Data] as map_data
open map[map_data/Map] as map_map_data
// TODO: add other maps if needed.

/*******************************************************************************
 * TOSCA scalar types.
 *******************************************************************************/

let any = (Int + String + boolean + Scalar + map_integer/Map + map_string/Map + Data + map_data/Map + map_map_data/Map)
enum boolean { true, false }
let string = String
let EMPTY_STRING = "<empty string>" // empty string is not allowed by Alloy Analyzer
let version = String // TODO: WOULD be revisited
let range = String   // TODO: MUST be revisited
let integer = Int
let float = String     // ISSUE: Use string as there is no float primitive type in Alloy.
let timestamp=String

/** Definition for scalar-unit.* */

abstract sig Scalar {
  value: one Int
} {
  value >= 0 // A scalar is a positive integer.
}

enum SizeUnits { B, kB, KiB, MB, MiB, GB, GiB, TB, TiB }

sig scalar_unit_size extends Scalar {
  unit: one SizeUnits
}

pred scalar_unit_size.init[v: one Int, u: one SizeUnits]
{
  this.value = v
  this.unit = u
}

/** Is a size greater than or equal to another size. */
pred scalar_unit_size.greater_or_equal[v: one Int, u: one SizeUnits]
{
  v != 0 implies // if v = 0 then this predicate is true
  this.unit = u
    implies
      this.value >= v
    else
      this.unit.gt[u] // as size units are listed from the lower to the higher unit.
}
enum FrequencyUnits { Hz, kHz, MHz, GHz }

sig scalar_unit_frequency extends Scalar {
  unit: one FrequencyUnits
}

pred scalar_unit_frequency.init[v: one Int, u: one FrequencyUnits]
{
  this.value = v
  this.unit = u
}

/** Is a frequency greater than or equal to another frequency. */
pred scalar_unit_frequency.greater_or_equal[v: one Int, u: one FrequencyUnits]
{
  v != 0 implies // if v = 0 then this predicate is true
  this.unit = u
    implies
      this.value >= v
    else
      this.unit.gt[u] // as size units are listed from the lower to the higher unit.
}

enum TimeUnits { d, h, m, s, ms, us, ns }

sig scalar_unit_time extends Scalar {
  unit: one TimeUnits
}

pred scalar_unit_time.init[v: one Int, u: one TimeUnits]
{
  this.value = v
  this.unit = u
}

/** Is a time greater than or equal to another time. */
pred scalar_unit_time.greater_or_equal[v: one Int, u: one TimeUnits]
{
  v != 0 implies // if v = 0 then this predicate is true
  this.unit = u
    implies
      this.value >= v
    else
      this.unit.lt[u] // as time units are listed from the higher to the lower unit.
}

/** Is a time greater than or equal to another time. */
pred scalar_unit_time.greater_or_equal[sut: one scalar_unit_time]
{
  this.greater_or_equal[sut.value, sut.unit]
}

/** Is a time greater than another time. */
pred scalar_unit_time.greater_than[v: one Int, u: one TimeUnits]
{
  v != 0 implies // if v = 0 then this predicate is true
  this.unit = u
    implies
      this.value > v
    else
      this.unit.lt[u] // as time units are listed from the higher to the lower unit.
}

/** Is a time greater than another time. */
pred scalar_unit_time.greater_than[sut: one scalar_unit_time]
{
  this.greater_than[sut.value, sut.unit]
}

/*******************************************************************************
 * TOSCA scalar predicates.
 *******************************************************************************/

pred valid_values[variable: one String, values: set String]
{
  variable in values
}

pred string.pattern[value: one string]
{
  // Do nothing as can not be expressed with Alloy.
}

pred integer.valid_values[values: set integer]
{
  this in values
}

/*
pred valid_values[variable: one String, value1: one Int, value2: one Int]
{
// TODO:  variable in values
}
*/

pred in_range[variable: one range, value1: one Int, value2: one Int]
{
  // NOTE: Always true because not supported currently.
}

pred float.in_range[lower: one float, upper: one float]
{
  // NOTE: Always true because not supported currently.
}

pred float.greater_or_equal[value: one float]
{
  // NOTE: Always true because not supported currently.
}

pred integer.greater_or_equal[value: one Int]
{
  one this implies this >= value
}

pred integer.greater_than[value: one Int]
{
  one this implies this > value
}

pred integer.less_or_equal[value: one Int]
{
  one this implies this <= value
}

pred integer.in_range[lower: one integer, upper: one integer]
{
  one this implies {
    lower <= this
    this <= upper
  }
}

pred min_length[variable: one String, value: one Int]
{
  // NOTE: Always true because not supported currently.
}

/*
pred min_length[variable: set String -> univ, value: one Int]
{
  #variable >= value
}
*/

//fk added following an error in SOL001 2.8.1 NSD_types: 'constraints: min_length' has been applied to a list in tosca.policies.nfv.NsMonitoring
pred min_length[variable: seq univ, value: one Int]
{
  #variable >= value
}

pred boolean.equal[value: one boolean]
{
  this = value
}

pred string.equal[value: one String]
{
  this = value
}

/*******************************************************************************
 * TOSCA range predicates.
 *******************************************************************************/

// pm: TODO must be changed when the signature Range will be introduced
pred range.init[p : set integer]
{
  // TODO: Nothing currently until waiting for the introduction of the Range signature.
}

/*******************************************************************************
 * TOSCA nodes, relationships, groups, and policies are named LG locations.
 *******************************************************************************/

abstract sig ToscaComponent extends LG/Location
{
  _name_ : lone String,
  attributes: set Attribute,
  interfaces : set Interface,
} {
  // Each attribute has a distinct name.
  distinct_names[attributes]

  // Each interface has a distinct name.
  distinct_names[interfaces]

// TBR
// Commented because a TOSCA profile could have no tosca_name attribute.
// one attribute["tosca_name"] implies attribute["tosca_name"].value = _name_
}

pred ToscaComponent.no_name[]
{
  no this._name_
}

pred ToscaComponent.name[n: one String]
{
  this._name_ = n
}

pred distinct_names[components : set ToscaComponent]
{
  all disj c1, c2 : components | c1._name_ != c2._name_
}

fun component[components: set ToscaComponent, component_name: one String] : one ToscaComponent
{
  { c : components { c._name_ = component_name } }
}

/** An attribute is owned by this TOSCA component. */
pred ToscaComponent.attribute[attribute: one Attribute]
{
  attribute in this.attributes
}

fun ToscaComponent.attribute[name: one String] : one Attribute
{
  get_value[this.attributes, name]
}

/** An interface is owned by this TOSCA component. */
pred ToscaComponent.interface[interface:  one Interface]
{
  interface in this.interfaces
}

fun ToscaComponent.interface[name: one String] : one Interface
{
  get_value[this.interfaces, name]
}

/*******************************************************************************
 * TOSCA requirements and capabilities are named LG roles.
 *******************************************************************************/

abstract sig ToscaRole extends LG/Role {
  _name_: one String,
} {
}

pred ToscaRole.no_name[]
{
  this._name_= "(anonymous)"
}

pred ToscaRole.name[n: one String]
{
  this._name_ in n
// NOTE: Could be also
// some this implies this.name = n
// but this produces more SAT vars and clauses.
}

fun role[roles: set ToscaRole, role_name: one String] : set ToscaRole
{
  { r : roles { r._name_ = role_name } }
}

/*******************************************************************************
 * TOSCA interfaces, operations, and artifacts are named LG values.
 *******************************************************************************/

abstract sig ToscaValue extends LG/Value
{
  _name_: lone String,
}

pred ToscaValue.no_name[]
{
  no this._name_
}

pred ToscaValue.name[n: one String]
{
  this._name_ = n
}

pred distinct_names[values : set ToscaValue]
{
  all disj v1, v2 : values | v1._name_ != v2._name_
}

fun get_value[values: set ToscaValue, value_name: one String] : one ToscaValue
{
  { v : values { v._name_ = value_name } }
}

/*******************************************************************************
 * TOSCA Topology Template.
 *******************************************************************************/

sig TopologyTemplate extends LG/LocationGraph
{
  description: lone string, // The optional description for the Topology Template.
  inputs: set Parameter, // An optional list of input parameters (i.e., as parameter definitions) for the Topology Template.
  nodes : set Node, // An optional list of node template definitions for the Topology Template.
  relationships : set Relationship, // An optional list of relationship templates for the Topology Template.
  groups : set Group, // An optional list of Group definitions whose members are node templates defined within this same Topology Template.
  policies : set Policy, // An optional list of Policy definitions for the Topology Template.
  outputs: set Parameter, // An optional list of output parameters (i.e., as parameter definitions) for the Topology Template.
  substitution_mapping: lone Node, // An optional declaration that exports the topology template as an implementation of a Node type. This also includes the mappings between the external Node Types named capabilities and requirements to existing implementations of those capabilities and requirements on Node templates declared within the topology template.
// TODO  workflows: set Workflow, // An optional map of imperative workflow definition for the Topology Template.
} {
  // Each input has a distinct name.
  distinct_names[inputs]

  // Each node has a distinct name.
  distinct_names[nodes]

  // Each relationskip has a distinct name.
  distinct_names[relationships]

  // Each group has a distinct name.
  distinct_names[groups]

  // Each policy has a distinct name.
  distinct_names[policies]

  // Each output has a distinct name.
  distinct_names[outputs]

  // if one substitution_mapping then it is distinct of nodes.
  one substitution_mapping implies substitution_mapping not in nodes

  //
  // Mapping TOSCA to Location Graphs.
  //
  // nodes, relationships, groups and policies are locations of this location graph.
// TBR  locations = nodes + relationships + groups + policies + nodes.requirements.relationship
  locations = nodes + relationships + groups + policies + (String.(nodes.requirements)).relationship
  // NOTE: substitution_mapping is not a location of this location graph but
  // will be part of the location graphs where it will be substituted.
}

fun TopologyTemplate.input[name: one String] : one Parameter
{
  get_value[this.inputs, name]
}

fun TopologyTemplate.get_input[name: one String]: one any
{
  this.input[name].value
}

fun TopologyTemplate.get_artifact[node: one Node, artifact_name: one String]: one string
{
  node.artifact[artifact_name].file
}

fun TopologyTemplate.get_attribute[node: one Node, attribute_name: one String]: one string
{
  node.attribute[attribute_name].value
}

pred TopologyTemplate.set_input[name: one String, v: one any]
{
  this.input[name].set_value[v]
}

pred TopologyTemplate.with_inputs[args: String -> lone any]
{
  all input : this.inputs {
    let arg_value=args[input._name_] {
      one arg_value
        implies
          input.set_value[arg_value]
        else
          let default_value=input.default {
            one default_value
              implies
                input.set_value[default_value]
              else
                no input.value
            }
      }
  }
}

/** A node is part of this topology. */
pred TopologyTemplate.node[node: Node]
{
  node in this.nodes
}

fun TopologyTemplate.node[name: String] : one Node
{
  component[this.nodes, name]
}

/** A relationship is part of this topology. */
pred TopologyTemplate.relationship[relationship: Relationship]
{
  relationship in this.relationships
}

fun TopologyTemplate.relationship[name: String] : one Relationship
{
  component[this.relationships, name]
}

/** A group is part of this topology. */
pred TopologyTemplate.group[group: Group]
{
  group in this.groups
}

fun TopologyTemplate.group[name: String] : one Group
{
  component[this.groups, name]
}

/** A policy is part of this topology. */
pred TopologyTemplate.policy[policy: Policy]
{
  policy in this.policies
}

fun TopologyTemplate.policy[name: String] : one Policy
{
  component[this.policies, name]
}

pred TopologyTemplate.output[output: one Parameter]
{
  output in this.outputs
}

fun TopologyTemplate.output[name: one String] : one Parameter
{
  get_value[this.outputs, name]
}

pred TopologyTemplate.substitution_mappings[node: Node]
{
  this.substitution_mapping = node
}

pred connectCapability[capabilities: set Capability, node_capabilities: set Capability]
{
  one cap : node_capabilities {
    cap in capabilities
  }
}

pred connectRequirement[requirements: set Requirement, node_requirements: set Requirement]
{
  one req : node_requirements {
    req in requirements
  }
}

pred TopologyTemplate.apply_substitution[]
{
  let substitution_mapping_nodes=TopologyTemplate.substitution_mapping {
    all node : this.nodes {
      let node_type=node.node_type_name {
        node_type in substitution_mapping_nodes.node_type_name - this.substitution_mapping.node_type_name
          implies
            one sub : { n : substitution_mapping_nodes | n.node_type_name = node_type } {
              node = sub
            }
       }
    }
  }
}

/*******************************************************************************
 * TOSCA Node.
 *******************************************************************************/

abstract sig Node extends ToscaComponent {
  node_type_name: lone String, // NOTE: Used by the substitution algorithm.
// TBR:  requirements : set Requirement,
  requirements :  String -> Requirement,
  capabilities : set Capability,
  artifacts : set Artifact,
} {
  // Each artifact has a distinct name.
  distinct_names[artifacts]

  //
  // Mapping TOSCA to Location Graphs.
  //
  // Requirements are required roles of this location.
// TBR:  required = requirements
  required = String.requirements
  //
  // Capabilities are provided roles of this location.
  provided = capabilities
}

/** A capability is owned by this node. */
pred Node.capability[capability: one Capability]
{
  capability in this.capabilities
}

fun Node.capability[name: one String] : set Capability
{
  role[this.capabilities, name]
}

/** A requirement is owned by this node. */
// TBR: pred Node.requirement[requirement:  one Requirement]
pred Node.requirement[name: String, requirement:  one Requirement]
{
// TBR:  requirement in this.requirements
  (name -> requirement) in this.requirements
}

fun Node.requirement[name: one String] : set Requirement
{
// TBR:  role[this.requirements, name]
  this.requirements[name]
}

/** An artefact is owned by this node. */
pred Node.artifact[artifact:  one Artifact]
{
  artifact in this.artifacts
}

fun Node.artifact[name: one String] : one Artifact
{
  get_value[this.artifacts, name]
}

/*******************************************************************************
 * TOSCA Requirement.
 *******************************************************************************/

// TODO: to remove as perhaps not required
// abstract // TBR: abstract is not necessary
sig Requirement extends ToscaRole {
  relationship: lone Relationship
} {
  //
  // TOSCA constraints.
  //
  // The source of the relationship is this requirement.
  one relationship implies relationship.source = this

  // The name of requirement is stored by the node owning this reference.
  no_name[]
}

/* Return the node owning a given requirement. */
fun Requirement.node[] : set Node {
// TBR:  ~(Node<:requirements)[this]
  ~(Node<:select13[requirements])[this]
}

// Copied from ternary.als
/** returns the first and last columns of a ternary relation */
fun select13 [r: univ->univ->univ] : ((r.univ).univ) -> (univ.(univ.r)) {
  {x: (r.univ).univ, z: univ.(univ.r) | some (x.r).z}
}

/** The capability targetted by this requirement is of given capability types. */
pred Requirement.capability[capabilities: set Capability]
{
  this.relationship.target in capabilities
}

/** The capability targetted by this requirement is owned by given node types. */
pred Requirement.node[nodes: set Node]
{
  this.relationship.target.node in nodes
}

pred Requirement.relationship[rel: set Relationship]
{
  this.relationship in rel
}

/** The target node of this requirement. */
fun Requirement.node_filter[]: set Node
{
  this.relationship.target.node
}

pred connect[requirements : set Requirement, capabilities : set Capability]
{
  one requirement : requirements {
    requirement.relationship.source = requirement
    one capability : capabilities {
      requirement.relationship.target = capability
    }
  }
}

/*******************************************************************************
 * TOSCA Capability.
 *******************************************************************************/

abstract sig Capability extends ToscaRole {
  attributes: set Attribute
} {
  // Each attribute has a distinct name.
  distinct_names[attributes]
}

/* Return the node owning a given capability. */
fun Capability.node[] : one Node {
  ~(Node<:capabilities)[this]
}

/** An attribute is owned by this TOSCA capability. */
pred Capability.attribute[attribute: one Attribute]
{
  attribute in this.attributes
}

fun Capability.attribute[name: one String] : one Attribute
{
  get_value[this.attributes, name]
}

/** The requirements targetting this capability are owned by given node types. */
pred Capability.valid_source_types[nodes: set Node]
{
  ~(Relationship<:target)[this].source.node in nodes
}

/*******************************************************************************
 * TOSCA Relationship.
 *******************************************************************************/

abstract sig Relationship extends ToscaComponent {
  source : one Requirement,
  target: one Capability
} {
  //
  // Mapping TOSCA to Location Graphs.
  //
  // The source requirement is a provided role of this location.
  provided = source
  //
  // The target capability is a required role of this location.
  required = target
}

pred Relationship.valid_target_types[capabilities: set Capability]
{
  this.target in capabilities
}

/*******************************************************************************
 * TOSCA Group.
 *******************************************************************************/

abstract sig Group extends ToscaComponent
{
  members: set Node
} {
  // TODO: members must be owned by the location graph owning this group.
}

pred Group.members_type[nodes: set Node]
{
  this.members in nodes
}

pred Group.members[nodes: set Node]
{
  this.members = nodes
}

/*******************************************************************************
 * TOSCA Policy.
 *******************************************************************************/

abstract sig Policy extends ToscaComponent
{
  targets: set Node + Group
} {
  // TODO: targets must be owned by the location graph owning this policy.
}

pred Policy.targets_type[nodesAndGroups: set Node + Group]
{
  this.targets in nodesAndGroups
}

pred Policy.targets[nodesAndGroups: set Node + Group]
{
    this.targets = nodesAndGroups
}

/*******************************************************************************
 * TOSCA Interface.
 *******************************************************************************/

abstract sig Interface extends ToscaValue
{
  operations: set Operation,
} {
  // Each operation has a distinct name.
  distinct_names[operations]
}

pred Interface.operation[operation: Operation]
{
  operation in this.operations
}

fun Interface.operation[name: String] : one Operation
{
  get_value[this.operations, name]
}

/*******************************************************************************
 * TOSCA Operation.
 *******************************************************************************/

sig Operation extends ToscaValue
{
  implementation: lone Artifact,
  inputs: set Parameter,
} {
  // Each input has a distinct name.
  distinct_names[inputs]
}

fun Operation.input[name: one String] : one Parameter
{
  get_value[this.inputs, name]
}

pred Operation.implementation[artifact_type: set Artifact, impl: one String]
{
  this.implementation in artifact_type
  this.implementation.file = impl
  no this.implementation._name_
}

/*******************************************************************************
 * TOSCA Attribute.
 *******************************************************************************/

sig Attribute extends ToscaValue
{
  value: one any,
}

pred Attribute.type[types: set any]
{
  this.value in types
}

/*******************************************************************************
 * TOSCA Artifact.
 *******************************************************************************/

abstract sig Artifact extends ToscaValue
{
  mime_type: lone String,
  file_ext: set String,
  file: lone String,
}

pred Artifact.mime_type[mt: one String]
{
  this.mime_type = mt
}

pred Artifact.file_ext[fe: set String]
{
  this.file_ext = fe
}

pred Artifact.file[f: set String]
{
  this.file = f
}

/*******************************************************************************
 * TOSCA Data.
 *******************************************************************************/

abstract sig Data extends LG/Value
{
}

/*******************************************************************************
 * TOSCA Property and Parameter.
 *******************************************************************************/

abstract sig AbstractProperty extends ToscaValue
{
  type: lone string, // The required data type for the property.
  description: lone string, // The optional description for the property.
  required: lone boolean, // An optional key that declares a property as required (true) or not (false). Default is true.
  default: lone any, // An optional key that may provide a value to be used as a default if not provided by another means.
  status: lone // The optional status of the property relative to the specification or implementation. Default is "supported".
                    "supported"      // Indicates the property is supported. This is the default value for all property definitions.
                 + "unsupported"  // Indicates the property is not supported.
                 + "experimental" // Indicates the property is experimental and has no official standing.
                 +  "deprecated",  // Indicates the property has been deprecated by a new specification version.
// NOTE: AbstractProperty constraints are mapped to Alloy facts.
//  constraints: set string, // The optional list of sequenced constraint clauses for the property.
// NOTE: AbstractProperty entry_schema are mapped to Alloy facts.
//  entry_schema: lone string, // The optional key that is used to declare the name of the Datatype definition for entries of set types such as the TOSCA list or map.
  external_schema: lone string, // The optional key that contains a schema definition that TOSCA Orchestrators MAY use for validation when the “type” key’s value indicates an External schema (e.g., “json”) See section “External schema” below for further explanation and usage.
  metadata: String -> lone string, // Defines a section used to declare additional metadata information.
}

sig Property extends AbstractProperty
{
} {
  one type // The type of a property is required.
}

sig Parameter extends AbstractProperty
{
  value: lone any, // The type-compatible value to assign to the named parameter. Parameter values may be provided as the result from the evaluation of an expression or a function.
}

pred Parameter.type[types: set any]
{
  this.value in types
  this.default in types
}

pred Parameter.required[req: one boolean]
{
  this.required = req
// TODO: Following is commented currently because this does not work correctly for topology template outputs.
//  req = true implies one this.value
}

pred Parameter.set_value[v: one any]
{
  this.value = v
}

pred Parameter.undefined[]
{
  no this.type
  no this.description
  no this.required
  no this.default
  no this.status
  no this.external_schema
  no this.metadata
}

/*******************************************************************************
 * Consistency Property.
 ******************************************************************************/

/** Consistency means that there exists some TOSCA topology. */
run Model {}

run OneTopologyWithTwoNodeOneRelationship
{
  "string1" + "string2" in String
  Node in TopologyTemplate.nodes
  Relationship in TopologyTemplate.relationships
} for 10 but exactly 1 TopologyTemplate, exactly 2 Node, exactly 1 Relationship
