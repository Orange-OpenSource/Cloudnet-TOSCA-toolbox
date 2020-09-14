#! /bin/sh
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
# Software description: Use case for TOSCA to Cloudnet Translator
######################################################################

# Load cloundnet commands.
CLOUDNET_BINDIR=../../bin
. ${CLOUDNET_BINDIR}/cloudnet_rc.sh

# Translate TOSCA-based templates.
translate OpenStack_types.yaml
translate OpenStack-1.yaml
translate OpenStack-2.yaml

# Generate TOSCA diagrams.
generate_tosca_diagrams tosca_diagrams/*.dot

# Generate UML2 diagrams.
generate_uml2_diagrams uml2/*.plantuml
