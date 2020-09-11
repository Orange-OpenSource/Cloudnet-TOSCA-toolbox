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

# Chapter 2
translate example-2-1.yaml
translate example-2-2.yaml
translate example-2-3.yaml
translate example-2-4.yaml
translate example-2-5.yaml
translate example-2-6.yaml
translate example-2-7.yaml
translate example-2-8.yaml
translate example-2-9.yaml
translate example-2-10.yaml
translate example-2-14.yaml
translate example-2-20.yaml
translate example-2-21.yaml
translate example-2-22.yaml

# Chapter 5
#translate tosca_simple_yaml_1_2.yaml

# Concat the copyright header and the previous generated file into cloudnet/
#cat tosca_simple_yaml_1_2.header Alloy/tosca_simple_yaml_1_2.als > ../../bin/Alloy/models/cloudnet/tosca_simple_yaml_1_2.als

# Remove the previous generated file.
#rm Alloy/tosca_simple_yaml_1_2.als

# Chapter 8
translate example-8.6.1.yaml
translate example-8.6.2.yaml

# Chapter 9
translate non_normative_types.yaml

# Chapter 11
translate Compute.yaml
translate SoftwareComponent-1.yaml
translate BlockStorage-1.yaml
translate BlockStorage-2.yaml
translate BlockStorage-3.yaml
translate BlockStorage-4.yaml
translate BlockStorage-5.yaml
translate BlockStorage-6.yaml
translate ObjectStorage-1.yaml
translate Network-1.yaml
translate Network-2.yaml
translate Network-3.yaml
translate Network-4.yaml
translate WebServer-DBMS-1.yaml
translate WebServer-DBMS-2.yaml
translate Container-1.yaml

# Other examples
translate cyclic-dependencies.yaml

# Parse and type check all Alloy specifications.
alloy_parse Alloy/*.als

# Generate TOSCA diagrams.
generate_tosca_diagrams tosca_diagrams/*.dot

# Generate UML2 diagrams.
generate_uml2_diagrams uml2/*.plantuml
