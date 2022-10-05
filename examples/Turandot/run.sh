#! /bin/bash
######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2022 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: Cloudnet TOSCA toolbox
######################################################################

# Load cloudnet commands.
CLOUDNET_BINDIR="../../bin"
. "${CLOUDNET_BINDIR}/cloudnet_rc.sh"

TURANDOT_URL=https://raw.githubusercontent.com/tliron/turandot
PROFILES=$TURANDOT_URL/main/assets/tosca/profiles
EXAMPLES=$TURANDOT_URL/main/examples

translate $PROFILES/ansible/1.0/artifacts.yaml
translate $PROFILES/ansible/1.0/profile.yaml
translate $PROFILES/helm/1.0/artifacts.yaml
translate $PROFILES/helm/1.0/nodes.yaml
translate $PROFILES/helm/1.0/profile.yaml
translate $PROFILES/kubernetes/1.0/_data.yaml
translate $PROFILES/kubernetes/1.0/artifacts.yaml
translate $PROFILES/kubernetes/1.0/capabilities.yaml
translate $PROFILES/kubernetes/1.0/data.yaml
translate $PROFILES/kubernetes/1.0/groups.yaml
translate $PROFILES/kubernetes/1.0/interfaces.yaml
translate $PROFILES/kubernetes/1.0/nodes.yaml
translate $PROFILES/kubernetes/1.0/policies.yaml
translate $PROFILES/kubernetes/1.0/profile.yaml
translate $PROFILES/kubernetes/1.0/relationships.yaml
translate $PROFILES/kubernetes/1.0/repositories.yaml
translate $PROFILES/kubevirt/1.0/artifacts.yaml
translate $PROFILES/kubevirt/1.0/capabilities.yaml
translate $PROFILES/kubevirt/1.0/data.yaml
translate $PROFILES/kubevirt/1.0/profile.yaml
translate $PROFILES/mariadb/capabilities.yaml
translate $PROFILES/mariadb/nodes.yaml
translate $PROFILES/mariadb/profile.yaml
translate $PROFILES/orchestration/1.0/artifacts.yaml
translate $PROFILES/orchestration/1.0/data.yaml
translate $PROFILES/orchestration/1.0/interfaces.yaml
translate $PROFILES/orchestration/1.0/policies.yaml
translate $PROFILES/orchestration/1.0/profile.yaml

translate $EXAMPLES/hello-world/hello-world.yaml
translate $EXAMPLES/helm/helm.yaml
translate $EXAMPLES/self-contained/self-contained.yaml
translate $EXAMPLES/telephony-network-service/profiles/network-service/profile.yaml
translate $EXAMPLES/telephony-network-service/profiles/telephony/profile.yaml
translate $EXAMPLES/telephony-network-service/asterisk-cnf.yaml
translate $EXAMPLES/telephony-network-service/asterisk-vnf.yaml
translate $EXAMPLES/telephony-network-service/simple-data-plane.yaml
translate $EXAMPLES/telephony-network-service/telephony-network-service.yaml

# Generate TOSCA diagrams.
generate_tosca_diagrams diagrams/tosca/*.dot

# Generate UML2 diagrams.
generate_uml2_diagrams diagrams/uml2/*.plantuml

# Remove useless generated files.
rm -rf diagrams/tosca/*.dot \
       diagrams/uml2/*.plantuml
