#! /bin/bash
######################################################################
#
# Software Name: Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2022 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
#
######################################################################

# Load cloudnet commands.
CLOUDNET_BINDIR="../../bin"
. "${CLOUDNET_BINDIR}/cloudnet_rc.sh"

# Base URL where TOSCA service templates are.
BASE_URL="https://raw.githubusercontent.com/oasis-open/tosca-community-contributions/master"

# Compile TOSCA profiles
export TOSCAWARE_OPTS="--config-file tosca2cloudnet-profiles.yaml"
for file in \
      profiles/org.oasis-open/simple/1.0/artifact \
      profiles/org.oasis-open/simple/1.0/capability \
      profiles/org.oasis-open/simple/1.0/data \
      profiles/org.oasis-open/simple/1.0/group \
      profiles/org.oasis-open/simple/1.0/interface \
      profiles/org.oasis-open/simple/1.0/node \
      profiles/org.oasis-open/simple/1.0/policy \
      profiles/org.oasis-open/simple/1.0/profile \
      profiles/org.oasis-open/simple/1.0/relationship \
      \
      profiles/org.oasis-open/simple/1.1/artifact \
      profiles/org.oasis-open/simple/1.1/capability \
      profiles/org.oasis-open/simple/1.1/data \
      profiles/org.oasis-open/simple/1.1/group \
      profiles/org.oasis-open/simple/1.1/interface \
      profiles/org.oasis-open/simple/1.1/node \
      profiles/org.oasis-open/simple/1.1/policy \
      profiles/org.oasis-open/simple/1.1/profile \
      profiles/org.oasis-open/simple/1.1/relationship \
      \
      profiles/org.oasis-open/simple/1.2/artifact \
      profiles/org.oasis-open/simple/1.2/capability \
      profiles/org.oasis-open/simple/1.2/data \
      profiles/org.oasis-open/simple/1.2/group \
      profiles/org.oasis-open/simple/1.2/interface \
      profiles/org.oasis-open/simple/1.2/node \
      profiles/org.oasis-open/simple/1.2/policy \
      profiles/org.oasis-open/simple/1.2/profile \
      profiles/org.oasis-open/simple/1.2/relationship \
      \
      profiles/org.oasis-open/simple/1.3/artifact \
      profiles/org.oasis-open/simple/1.3/capability \
      profiles/org.oasis-open/simple/1.3/data \
      profiles/org.oasis-open/simple/1.3/group \
      profiles/org.oasis-open/simple/1.3/interface \
      profiles/org.oasis-open/simple/1.3/node \
      profiles/org.oasis-open/simple/1.3/policy \
      profiles/org.oasis-open/simple/1.3/profile \
      profiles/org.oasis-open/simple/1.3/relationship \
      \
      profiles/org.oasis-open/simple/2.0/artifact_types \
      profiles/org.oasis-open/simple/2.0/capability_types \
      profiles/org.oasis-open/simple/2.0/data_types \
      profiles/org.oasis-open/simple/2.0/group_types \
      profiles/org.oasis-open/simple/2.0/interface_types \
      profiles/org.oasis-open/simple/2.0/node_types \
      profiles/org.oasis-open/simple/2.0/policy_types \
      profiles/org.oasis-open/simple/2.0/profile \
      profiles/org.oasis-open/simple/2.0/relationship_types
do
  translate $BASE_URL/$file.yaml
done

# Compile TOSCA examples
unset TOSCAWARE_OPTS
for file in \
      examples/1.2/simple-for-nfv/simple-for-nfv.yaml \
      examples/1.3/examples-from-spec/inputs-and-outputs/inputs-and-outputs.yaml \
      examples/1.3/examples-from-spec/hello-world/hello-world.yaml \
      examples/1.3/examples-from-spec/mysql/mysql.yaml \
      examples/1.3/examples-from-spec/mysql/non-normative-types.yaml \
      examples/basic-template/basic-template.yml \
      interop/iaas/simple-compute/main.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/artifacts.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/capabilities.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/data.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/nodes.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/profile.yaml \
      profiles/org.oasis-open/simple-for-nfv/1.0/relationships.yaml \
      profiles/org.oasis-open/non-normative/artifact.yaml \
      profiles/org.oasis-open/non-normative/capability.yaml \
      profiles/org.oasis-open/non-normative/node.yaml \
      profiles/org.oasis-open/non-normative/profile.yaml \
      profiles/cloud.puccini/helm/1.0/artifacts.yaml \
      profiles/cloud.puccini/helm/1.0/nodes.yaml \
      profiles/cloud.puccini/helm/1.0/profile.yaml \
      profiles/cloud.puccini/kubernetes/1.0/artifacts.yaml \
      profiles/cloud.puccini/kubernetes/1.0/capabilities.yaml \
      profiles/cloud.puccini/kubernetes/1.0/data.yaml \
      profiles/cloud.puccini/kubernetes/1.0/groups.yaml \
      profiles/cloud.puccini/kubernetes/1.0/interfaces.yaml \
      profiles/cloud.puccini/kubernetes/1.0/nodes.yaml \
      profiles/cloud.puccini/kubernetes/1.0/policies.yaml \
      profiles/cloud.puccini/kubernetes/1.0/profile.yaml \
      profiles/cloud.puccini/kubernetes/1.0/relationships.yaml \
      profiles/cloud.puccini/kubernetes/1.0/repositories.yaml \
      profiles/cloud.puccini/kubevirt/1.0/artifacts.yaml \
      profiles/cloud.puccini/kubevirt/1.0/capabilities.yaml \
      profiles/cloud.puccini/kubevirt/1.0/data.yaml \
      profiles/cloud.puccini/kubevirt/1.0/profile.yaml \
      profiles/cloud.puccini/openstack/1.0/capabilities.yaml \
      profiles/cloud.puccini/openstack/1.0/data.yaml \
      profiles/cloud.puccini/openstack/1.0/nodes.yaml \
      profiles/cloud.puccini/openstack/1.0/profile.yaml \
      profiles/cloud.puccini/openstack/1.0/relationships.yaml
do
  translate $BASE_URL/$file
done

#TODO: examples/1.3/turandot/hello-world/hello-world.yaml
#TODO: examples/1.3/turandot/telephony-network-service/*.yaml
#TODO: examples/1.3/tutorial/*.yaml

# Generate TOSCA diagrams.
generate_tosca_diagrams diagrams/tosca/*.dot

# Generate UML diagrams.
generate_uml2_diagrams diagrams/uml2/*.plantuml

# Remove useless generated files.
rm -rf diagrams/tosca/*.dot
rm -rf diagrams/uml2/*.plantuml
