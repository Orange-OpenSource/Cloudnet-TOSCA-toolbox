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

module tosca_simple_yaml_1_1

open LocationGraphs as LG
open TOSCA as TOSCA

sig tosca_datatypes_Root extends TOSCA/Data
{
} {
}

sig tosca_artifacts_Root extends TOSCA/Artifact
{
} {
}

sig tosca_artifacts_Deployment_Image extends tosca_artifacts_Root
{
} {
}

sig tosca_artifacts_Implementation extends tosca_artifacts_Root
{
} {
}

sig tosca_capabilities_Root extends TOSCA/Capability
{
} {
}

sig tosca_relationships_Root extends TOSCA/Relationship
{
} {
}

sig tosca_interfaces_Root extends TOSCA/Interface
{
} {
}

sig tosca_relationships_DependsOn extends tosca_relationships_Root
{
} {
}

sig tosca_nodes_Root extends TOSCA/Node
{
} {
}

sig tosca_groups_Root extends TOSCA/Group
{
} {
}

sig tosca_policies_Root extends TOSCA/Policy
{
} {
}

sig tosca_policies_Placement extends tosca_policies_Root
{
} {
}
