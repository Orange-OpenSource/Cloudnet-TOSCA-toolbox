#!/usr/bin/env bash
######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-21 Orange
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
if [ ! -f "${CLOUDNET_BINDIR}"/cloudnet_rc.sh ]
then
  echo CLOUDNET_BINDIR environment variable incorrectly set!
fi

export CLOUDNET_BINDIR

# Generate Alloy and diagram files.
translate()
{
  local file
  echo Translate TOSCA files...
  for file in "$@"
  do
    echo "- $file"
    "${CLOUDNET_BINDIR}"/toscaware/toscaware "$file"
  done
}

# To configure Alloy Parse options, e.g.:
# ALLOY_PARSE_OPTS="options"

# Parse and type check generated Alloy files.
alloy_parse()
{
  local file
  echo Parsing and type checking generated Alloy files...
  for file in "$@"
  do
    echo "- $file"
    "${CLOUDNET_BINDIR}"/Alloy/alloy.sh parse "${ALLOY_PARSE_OPTS}" "$file"
  done
}

# To configure Alloy Execute options
# only execute commands related to topology templates
ALLOY_EXECUTE_OPTS='-c "Show_.*_topology_template"'

# Analyse generated Alloy files.
alloy_execute()
{
  echo Analysing generated Alloy files...
  local file
  for file in "$@"
  do
    echo "- $file"
    "${CLOUDNET_BINDIR}"/Alloy/alloy.sh execute "${ALLOY_EXECUTE_OPTS}" "$file"
  done
}

# To configure dot options, e.g.:
# DOT_OPTS="options"

# Generate TOSCA diagrams.
generate_tosca_diagrams()
{
  local file
  echo Generating TOSCA diagrams...
  for file in "$@"
  do
    echo "- $file"
    filebase="$(dirname "$file")/$(basename -s .dot "$file")"
    # generate TOSCA diagram as a PNG image
    "${CLOUDNET_BINDIR}"/dot/dot -o"$filebase.png" -Tpng "$file"
    # generate TOSCA diagram as a SVG file
    "${CLOUDNET_BINDIR}"/dot/dot -o"$filebase.svg" -Tsvg "$file"
  done
}

# To configure nwdiag options
# By default, apply anti-alias filter to generated network diagrams.
# This improves the graphical quality of generated network diagrams.
# NWDIAG_OPTS="-a"

# Generate network diagrams.
generate_network_diagrams()
{
  local file
  local current_directory
  echo Generating network diagrams...
  for file in "$@"
  do
    echo "- $file"
    current_directory="$PWD" # store current directory
    if [ -d "${nwdiag_target_directory}" ]
    then
      cd "$(dirname "$file")" # go to directory containing generated network diagrams
      # generate network diagram as a PNG image
      "${CLOUDNET_BINDIR}"/nwdiag/nwdiag -a -Tpng "$(basename "$file")"
      # generate network diagram as a SVG file
      "${CLOUDNET_BINDIR}"/nwdiag/nwdiag -Tsvg "$(basename "$file")"
      cd "${current_directory}" # back to current directory
    fi
  done
}

# To configure PlantUML options, e.g.
# - set the limit size of PlantUML diagrams
export PLANTUML_OPTS="-DPLANTUML_LIMIT_SIZE=50000"

# Generate UML2 diagrams.
generate_uml2_diagrams()
{
  local file
  echo Generating UML2 diagrams...
  for file in "$@"
  do
    echo "- $file"
    # generate UML2 diagram as a PNG image
    "${CLOUDNET_BINDIR}"/plantuml/plantuml -Tpng "$file"
    # generate UML2 diagram as a SVG file
    "${CLOUDNET_BINDIR}"/plantuml/plantuml -Tsvg "$file"
  done
}
