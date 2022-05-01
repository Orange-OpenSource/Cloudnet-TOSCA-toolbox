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

KHUTULUN_URL=https://raw.githubusercontent.com/tliron/khutulun

# Compile Khutulun profile
for file in artifacts capabilities data groups interfaces nodes policies profile relationships
do
  translate $KHUTULUN_URL/main/assets/tosca/profiles/khutulun/$file.yaml
done

translate $KHUTULUN_URL/main/examples/hello-world/hello-world.yaml

translate refactored_nodes.yaml

# Generate TOSCA diagrams.
generate_tosca_diagrams diagrams/tosca/*.dot

# Generate network diagrams.
generate_network_diagrams diagrams/network/*.nwdiag

# Generate UML2 diagrams.
generate_uml2_diagrams diagrams/uml2/*.plantuml

# Remove useless generated files.
rm -rf diagrams/tosca/*.dot \
       diagrams/network/*.nwdiag \
       diagrams/uml2/*.plantuml
