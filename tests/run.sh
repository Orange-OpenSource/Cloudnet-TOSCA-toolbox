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
# Software description: Tests for TOSCA to Cloudnet Translator
######################################################################

# Load cloudnet commands.
CLOUDNET_BINDIR=../bin
. ${CLOUDNET_BINDIR}/cloudnet_rc.sh

exit_code=0

check_regression()
{
  translate $1 2> /tmp/cloudnet_translate.log
  expected_errors="`grep ERROR $1 | wc -l`"
  generated_errors="`grep ERROR /tmp/cloudnet_translate.log | wc -l`"
  echo ${expected_errors} expected errors and ${generated_errors} generated errors
  if [[ ${expected_errors} == ${generated_errors} ]]
  then
    echo No regression on $1
  else
    echo Regression on $1!
    exit_code=1
  fi
}

# TOSCA syntax checking
check_regression syntax_checking.yaml # tosca_definitions_version: tosca_simple_yaml_1_2
check_regression syntax_checking-1.3.yaml # tosca_definitions_version: tosca_simple_yaml_1_3

# TOSCA type checking
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_0/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_1/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_2/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_3/types.yaml
check_regression type_checking.yaml

exit ${exit_code}
