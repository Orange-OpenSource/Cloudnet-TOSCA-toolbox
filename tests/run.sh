#! /bin/bash
######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-22 Orange
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
# shellcheck source=./bin/cloudnet_rc.sh
CLOUDNET_BINDIR="../bin"
. "${CLOUDNET_BINDIR}/cloudnet_rc.sh"

exit_code=0

# Define colors
RED="\033[0;31m"
GREEN="\033[0;32m"
RESET="\033[0m"

check_regression()
{
  translate $1 2> /tmp/cloudnet_translate.log
  expected_errors="`grep ERROR $1 | wc -l`"
  generated_errors="`grep ERROR /tmp/cloudnet_translate.log | wc -l`"
  expected_warnings="`grep WARNING $1 | wc -l`"
  generated_warnings="`grep Warning /tmp/cloudnet_translate.log | wc -l`"
  echo ${expected_errors} expected errors and ${generated_errors} generated errors
  echo ${expected_warnings} expected warnings and ${generated_warnings} generated warnings
  if [ ${expected_errors} == ${generated_errors} ] && [ ${expected_warnings} == ${generated_warnings} ]
  then
    echo -e ${GREEN}No regression in $1${RESET}
  else
    echo -e ${RED}Regression in $1! ${RESET}
    exit_code=1
  fi
}

# YAML parsing
check_regression yaml_parsing/incorrect_indentation_in_definition.yaml
check_regression yaml_parsing/incorrect_indentation_in_mapping.yaml
check_regression yaml_parsing/incorrect_indentation_in_sequence.yaml
check_regression yaml_parsing/missed_quote_error.yaml
check_regression yaml_parsing/string_must_be_quoted.yaml
check_regression yaml_parsing/unexpected_carriage_return.yaml

# TOSCA syntax checking
check_regression syntax_checking-1.2.yaml # tosca_definitions_version: tosca_simple_yaml_1_2
check_regression syntax_checking-1.3.yaml # tosca_definitions_version: tosca_simple_yaml_1_3

# TOSCA type checking
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_0/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_1/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_2/types.yaml
translate /cloudnet/tosca/profiles/tosca_simple_yaml_1_3/types.yaml
check_regression type_checking.yaml
check_regression type_checking-1.3.yaml
check_regression topology_template_substitution_mapping.yaml

# Cloudnet TOSCA Toolbox issues
check_regression issues/issue_39.yaml
check_regression issues/issue_40.yaml
check_regression issues/issue_41.yaml
check_regression issues/issue_42.yaml
check_regression issues/issue_43.yaml
check_regression issues/issue_52.yaml
check_regression issues/issue_54.yaml
check_regression issues/issue_55.yaml

exit ${exit_code}
