#!/usr/bin/env bash
######################################################################
#
# Script to execute Alloy.
#
# Copyright (c) 2019 Orange
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

DIR=$(dirname "$0")

if [[ $1 == "gui" ]]
then
  MAIN_CLASS=edu.mit.csail.sdg.alloy4whole.SimpleGUI
elif [[ $1 == "parse" ]]
then
  MAIN_CLASS=cloudnet.Parse
elif [[ "$1" == "execute" ]]
then
  MAIN_CLASS=cloudnet.Execute
elif [[ "$1" == "benchmark" ]]
then
  MAIN_CLASS=cloudnet.BenchmarkSolver
else
  echo "alloy.sh (gui|parse|execute|benchmark) ..."
  # According to what was decided return a program crash error code 2
  # Remember : 
  #    0 : OK
  #    1 : INFO, WARNING or ERROR
  #    2 : program crash or unexpected error
  exit 2
fi

shift
#java -cp $DIR:$DIR/Alloy-5.0.0.1.jar $MAIN_CLASS $@
java -Xmx3G -cp "$DIR":"$DIR"/org.alloytools.alloy.dist.jar:"$DIR"/commons-cli-1.4.jar "$MAIN_CLASS" "$@"
