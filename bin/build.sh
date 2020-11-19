#!/usr/bin/env bash
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
# Software description: TOSCA to Cloudnet Translator
######################################################################

docker_build()
{
  echo -------------------- $1 Docker image --------------------
  echo Building $1 Docker image...
  docker build -t $1 $2
  echo
}

docker_build toscaware/dot dot
docker_build toscaware/nwdiag nwdiag
docker_build toscaware/plantuml plantuml
docker_build toscaware/toscaware toscaware
