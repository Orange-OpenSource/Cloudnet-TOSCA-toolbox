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

# Check that the argument is correct.
if [ ! -f ${CLOUDNET_BINDIR}/cloudnet_rc.sh ]
then
  echo "Invalid argument ${CLOUDNET_BINDIR}!"
fi

# Generate Alloy and diagram files.
translate()
{
  echo Translate $1...
  run_toscaware $1
}

run_toscaware()
{
  local container_dest_volume="/work"
  docker run \
    --user $(id -u):$(id -g) \
    --volume="${PWD}:${container_dest_volume}" \
    --volume="${PWD}/${CLOUDNET_BINDIR}/cloudnet:/cloudnet" \
    --workdir="${container_dest_volume}" \
    --rm \
    --attach=stdin --attach=stdout --attach=stderr \
    toscaware/toscaware \
    python /cloudnet/tosca/tosca2cloudnet.py --template-file $1
}

# Parse and type check generated Alloy files.
alloy_parse()
{
  echo Parsing and type checking generated Alloy files...
  for file in "$@"
  do
    ${CLOUDNET_BINDIR}/Alloy/alloy.sh parse "$file"
  done
}

# Analyse generated Alloy files.
alloy_execute()
{
  echo Analysing generated Alloy files...
  ${CLOUDNET_BINDIR}/Alloy/alloy.sh execute $@
}

# Generate TOSCA diagrams.
generate_tosca_diagrams()
{
  echo Generating TOSCA diagrams...
  for file in "$@"
  do
    echo "-" $file
    run_dot "$file"
  done
}

run_dot()
{
  local container_dest_volume="/work"
  docker run \
	  --user $(id -u):$(id -g) \
          --volume="${PWD}:${container_dest_volume}" \
          --workdir="${container_dest_volume}" \
          --rm \
          --attach=stdin --attach=stdout --attach=stderr \
          toscaware/dot \
          -Tpng "$1" > $(dirname "$1")/"$(basename -s .dot "$1")".png
}

# Generate network diagrams.
generate_network_diagrams()
{
  echo Generating network diagrams...
  for file in "$@"
  do
    echo "-" $file
    ${CLOUDNET_BINDIR}/nwdiag/nwdiag "$file"
  done
}

# Generate UML2 diagrams.
generate_uml2_diagrams()
{
  echo Generating UML2 diagrams...
  for file in "$@"
  do
    echo "-" $file
    ${CLOUDNET_BINDIR}/plantuml/plantuml "$file"
  done
}
