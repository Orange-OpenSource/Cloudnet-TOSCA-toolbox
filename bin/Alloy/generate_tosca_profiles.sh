#!/usr/bin/env bash
######################################################################
#
# Script to generate TOSCA profiles.
#
# Copyright (c) 2021 Orange
#
# Author(s):
# - Philippe Merle <philippe.merle@inria.fr>
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
######################################################################

# Load cloudnet commands.
CLOUDNET_BINDIR=$PWD/..
. ${CLOUDNET_BINDIR}/cloudnet_rc.sh

generate_tosca_profile()
{
  translate /cloudnet/tosca/profiles/$1/types.yaml
  cat tosca_profile_headers/$1.als Results/Alloy/$1.als > models/cloudnet/$1.als
}

generate_tosca_profile tosca_simple_yaml_1_0
generate_tosca_profile tosca_simple_yaml_1_1
generate_tosca_profile tosca_simple_yaml_1_2
generate_tosca_profile tosca_simple_yaml_1_3

rm -rf Results
