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

echo Cloning the kubetos repository...
if [ ! -e kubetos ]
then
  git clone https://github.com/Shishqa/kubetos.git
fi

echo Processing all kubetos templates...
for file in $(grep -r -l tosca_definitions_version kubetos | grep -E '\.(yaml|yml)$')
do
    translate "$file"
done

# Generate all TOSCA diagrams.
generate_tosca_diagrams diagrams/tosca/*.dot

# Generate all UML2 diagrams.
generate_uml2_diagrams diagrams/uml2/*.plantuml

# Remove useless generated files.
rm -rf diagrams/tosca/*.dot
rm -rf diagrams/uml2/*.plantuml
