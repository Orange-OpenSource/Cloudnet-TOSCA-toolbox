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
# Author: Jean-Luc Coulin <jeanluc.coulin@orange.com>
# Software description: Use case for TOSCA to Cloudnet Translator
######################################################################

################################################################################
# Help                                                                         #
################################################################################
Help()
{
   # Display Help
   echo
   echo "                TOSCA Toolbox"
   echo "  This script demonstrate how to use the TOSCA toolbox tools."
   echo
   echo "  Launched without parameter, it opens a MENU."
   echo
   echo "  With the -b option, it launches the whole process and store "
   echo "  the result in a log file located in logs/ directory"
   echo
   echo "     Syntax: run.sh -[b|h|s]"
   echo "     options:"
   echo "     b     Global execution (translate, diagrams generation, Alloy syntax checking)"
   echo "     h     Print this Help."
   echo "     s     launch a TOSCA syntax checking on the file provided on the command line."
   echo "           run.sh -s filename"
   echo
}

################################################################################
# TOSCA syntax checking
################################################################################
TOSCA_SyntaxCheck()
{
   # Configure a log file
   _LOG=$(basename "${PWD}")-$(date +%F_%H-%M-%S).log
   mkdir -p logs 2>/dev/null

   # All description files translation
   echo -e "\n${normal}${magenta}*** Descriptor files syntax checking ***${reset}" | tee -a logs/"${_LOG}"
   for filename in $(grep -r --include=*.{yaml,yml} -l 'tosca_definitions_version:') $(find . -iname '*.csar' -o -iname '*.zip')
     do 
       echo -e "\n${normal}${magenta}    ${filename^^} ${reset}" | tee -a logs/"${_LOG}"
       translate "$filename" 2>&1 | tee -a logs/"${_LOG}"
     done
   SYNTAX_CHECK=true
}

################################################################################
# Network diagrams generation
################################################################################
NetworkDiagrams()
{
   # Verify if Syntax checking has been done
   if [ "$SYNTAX_CHECK" = true ]; then 
      echo -e "\n${normal}${magenta}*** Generating network diagrams ***${reset}" | tee -a logs/"${_LOG}"
      generate_network_diagrams "${nwdiag_target_directory}"/*.nwdiag 2>&1 |tee -a logs/"${_LOG}"
   else
      # TODO : convert in a function to use it also for TOSCA, UML2, Alloy syntax and solve
      # If not, ask if we create diagrams with older generated files if they exist 
      if [ -d "${nwdiag_target_directory}" ] && test -n "$(find "${nwdiag_target_directory}" -maxdepth 1 -name '*.nwdiag' -print -quit)"
      then
         # 'old' files found
         echo -e "${normal}${red}DEBUG${reset} :\n    NWDIAG_OPTS : ${NWDIAG_OPTS}\n    DOCKER_OPTS : ${DOCKER_OPTS}"
         echo -e "${normal}${magenta}Previous generated nwdiag files found.${reset}"
         echo -e "Would you like to Generate diagrams whith them or generate Newer ones ? [Gg|Nn]" gn
         while true; do
             read -rs -n 1 gn
             case $gn in
                 [Gg]* ) 
                     generate_network_diagrams "${nwdiag_target_directory}"/*.nwdiag 2>&1 |tee -a logs/"${_LOG}";
                     break;;
                 [Nn]* ) 
                     echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                     break;;
                 * ) echo "Please answer [Gg]enerate or [Nn]ew.";;
             esac
         done
      else
         # no files found
         echo -e "${normal}${magenta}No generated nwdiag file found.${reset}"
         echo -e "      Be sure  to run \"TOSCA syntax checking\" before generating diagrams\n"
      fi
   fi
}

################################################################################
# TOSCA diagrams generation
################################################################################
TOSCADiagrams()
{
   # Verify if Syntax checking has been done
   if [ "$SYNTAX_CHECK" = true ]; then 
       echo -e "\n${normal}${magenta}*** Generating TOSCA diagrams ***${reset}" | tee -a "logs/${_LOG}"
       generate_tosca_diagrams "${tosca_diagrams_target_directory}/*.dot" 2>&1 |tee -a "logs/${_LOG}"
   else
      # If not, ask if we create diagrams with older generated files if they exist 
      if [ -d "${tosca_diagrams_target_directory}" ] &&  test -n "$(find "${tosca_diagrams_target_directory}" -maxdepth 1 -name '*.dot' -print -quit)"
      then
         # 'old' files found
         echo -e "${normal}${magenta}Previous generated TOSCA files found.${reset}"
         echo -e "Would you like to Generate diagrams whith them or generate Newer ones ? [Gg|Nn]" gn
         while true; do
             read -rs -n 1 gn
             case $gn in
                 [Gg]* )
                     generate_tosca_diagrams "${tosca_diagrams_target_directory}"/*.dot 2>&1 |tee -a logs/"${_LOG}";
                     break;;
                 [Nn]* )
                     echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                     break;;
                 * ) echo "Please answer [Gg]enerate or [Nn]ew.";;
             esac
         done
      else
         # no files found
       echo -e "${normal}${magenta}No generated dot file found.${reset}"
       echo -e "\n      Be sure  to run \"TOSCA syntax checking\" before generating diagrams\n"
      fi
   fi
}

################################################################################
# UML2 diagrams generation
################################################################################
UML2Diagrams()
{
   # Verify if Syntax checking has been done
   if [ "$SYNTAX_CHECK" = true ]; then 
       echo -e "\n${normal}${magenta}*** Generating UML2 diagrams ***${reset}" | tee -a "logs/${_LOG}"
       generate_uml2_diagrams ${UML2_target_directory}/*.plantuml" 2>&1 |tee -a "logs/${_LOG}"
   else
      # If not, ask if we create diagrams with older generated files if they exist 
      if [ -d "${UML2_target_directory}" ] && test -n "$(find "${UML2_target_directory}" -maxdepth 1 -name '*.plantuml' -print -quit)"
      then
         # 'old' files found
         echo -e "${normal}${magenta}Previous generated plantuml files found.${reset}"
         echo -e "Would you like to Generate diagrams whith them or generate Newer ones ? [Gg|Nn]" gn
         while true; do
             read -rs -n 1 gn
             case $gn in
                 [Gg]* ) 
                     generate_uml2_diagrams "${UML2_target_directory}"/*.plantuml 2>&1 |tee -a logs/"${_LOG}";
                     break;;
                 [Nn]* ) 
                     echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                     break;;
                 * ) echo "Please answer [Gg]enerate or [Nn]ew.";;
             esac
         done
      else
         # no files found
         echo -e "${normal}${magenta}No generated plantuml file found.${reset}"
         echo -e "\n      Be sure  to run \"TOSCA syntax checking\" before generating diagrams\n"
      fi
   fi
}

################################################################################
# Alloy syntax checking
################################################################################
AlloySyntax()
{
   # Verify if Syntax checking has been done
   if [ "$SYNTAX_CHECK" = true ]; then 
       echo -e "\n${normal}${magenta}*** Checking ALLOY syntax ***${reset}" | tee -a "logs/${_LOG}"
       alloy_parse "${Alloy_target_directory}/*.als" 2>&1 |tee -a "logs/${_LOG}"
   else
      # If not, ask if we create diagrams with older generated files if they exist 
      if [ -d "${Alloy_target_directory}" ] && test -n "$(find "${Alloy_target_directory}" -maxdepth 1 -name '*.als' -print -quit)"
      then
         # 'old' files found
         echo -e "${normal}${magenta}Previous generated Alloy files found.${reset}"
         echo -e "Would you like to Generate diagrams whith them or generate Newer ones ? [Gg|Nn]" gn
         while true; do
             read -rs -n 1 gn
             case $gn in
                 [Gg]* )
                     alloy_parse "${Alloy_target_directory}"/*.als 2>&1 |tee -a logs/"${_LOG}";
                     break;;
                 [Nn]* )
                     echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                     break;;
                 * ) echo "Please answer [Gg]enerate or [Nn]ew.";;
             esac
         done
      else
         # no files found
         echo -e "${normal}${magenta}No generated Alloy file found.${reset}"
         echo "You need to run \"TOSCA syntax checking\" before launching the alloy syntax checking"
      fi
   fi
}

################################################################################
# Alloy solve
################################################################################
AlloySolve()
{
   # Verify if Syntax checking has been done
   if [ "$SYNTAX_CHECK" = true ]; then 
      echo -e "\n${normal}${magenta}*** Run the solver to verify the ability to deploy the description ***${reset}" | tee -a logs/"${_LOG}"
      /usr/bin/time -o logs/"${_LOG}" --append /bin/sh -c ". '${CLOUDNET_BINDIR}/cloudnet_rc.sh'; alloy_execute '${Alloy_target_directory}'/*.als 2>&1 |tee -a 'logs/${_LOG}'"
   else
      # If not, ask if we create diagrams with older generated files if they exist
      if [ -d "${Alloy_target_directory}" ] && test -n "$(find ${Alloy_target_directory} -maxdepth 1 -name '*.als' -print -quit)"
      then
         # 'old' files found
         echo -e "${normal}${magenta}Previous generated Alloy files found.${reset}"
         echo -e "Would you like to Generate diagrams whith them or generate Newer ones ? [Gg|Nn]" gn
         while true; do
             read -rs -n 1 gn
             case $gn in
                 [Gg]* )
                     /usr/bin/time -o logs/"${_LOG}" --append /bin/sh -c ". '${CLOUDNET_BINDIR}/cloudnet_rc.sh'; alloy_execute '${Alloy_target_directory}'/*.als 2>&1 |tee -a 'logs/${_LOG}'"
                     break;;
                 [Nn]* )
                     echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                     break;;
                 * ) echo "Please answer [Gg]enerate or [Nn]ew.";;
             esac
         done
      else
         # no files found
         echo -e "${normal}${magenta}No generated Alloy file found.${reset}"
         echo "You need to run \"TOSCA syntax checking\" before launching the alloy syntax checking"
      fi
       echo -e "${normal}${magenta}No generated als file found.${reset}"
       echo "You need to run \"TOSCA syntax checking\" before launching the alloy solver"
   fi
}

################################################################################
# Wait until enter key is pressed
################################################################################
pause(){
  echo 
  read -rp "         Press [Enter] key to continue..." fackEnterKey
}

################################################################################
# Display the MENU
################################################################################
show_menus() {
    clear
    echo "      ~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "       TOSCA Toolbox - M E N U "
    echo "      ~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "      1. TOSCA syntax checking"
    echo "      2. All diagrams generation"
    echo "      3. TOSCA syntax checking + diagrams generation"
    echo "      4. Alloy syntax checking"
    echo "      5. Alloy solve"
    echo "      c. Clean results and logs directories"
    echo "      l. Show the log file (type q to leave)"
    echo "      w. Launch the whole process"
    echo "      x. Exit"
    echo
}

################################################################################
# Read input from the keyboard and take the corresponding action defined in the
# case statement
################################################################################
read_options(){
    local choice
    read -rp "Enter choice [ 1-5 clwx ] " choice
    case $choice in
        1) # Launch TOSCA syntax checking
           echo -e "\n"
           TOSCA_SyntaxCheck
           pause
           ;;
        2) # Launch ALL diagrams generation
           echo -e "\n"
           NetworkDiagrams
           TOSCADiagrams
           UML2Diagrams
           pause
           ;;
        3) # Launch TOSCA syntax checking + ALL diagrams generation
           echo -e "\n"
           TOSCA_SyntaxCheck
           NetworkDiagrams
           TOSCADiagrams
           UML2Diagrams
           pause
           ;;
        4) # Launch Alloy Syntax checking
           echo -e "\n"
           AlloySyntax
           pause
           ;;
        5) # Launch Alloy solver
           echo -e "\n"
           AlloySolve
           pause
           ;;
        c) # Clean results and log files
           SYNTAX_CHECK=False
           echo -e "\nRemove log files"
           rm -rf logs
           rm -rf "?"
           echo -e "\nRemove generated result files"
           for var in "${dirArray[@]}"
           do
             echo " delete ${var} (${!var})"
             rm -rf "${!var}"
           done
           if [ "$DIRVARS_GENERATED" = true ]; then
             echo -e "\nRemove generated configuration file"
             rm -f "$TOSCA2CLOUDNET_CONF_FILE"
             rm -rf "$RESULT_DIR"
           fi
           pause
           ;;
        l) # Show the log file
           # If logfilname is set : show it
           # else, warn the user
           if [ -z ${_LOG+x} ]; then
             echo -e "\n\n"
             read -rp "          No log file created for this session, type any key to continue." choice
           else
             less -r "logs/${_LOG}"
           fi
           ;;
        w) # Launch the whole process
           echo -e "\n TOSCA syntax checking"
           TOSCA_SyntaxCheck
           echo -e "\n Network diagrams generation"
           NetworkDiagrams
           echo -e "\n TOSCA diagrams generation"
           TOSCADiagrams
           echo -e "\n UML2 diagrams generation"
           UML2Diagrams
           echo -e "\n ALLOY syntax checking"
           AlloySyntax
           echo -e "\n ALLOY solve execution"
           AlloySolve
           pause
           ;;
        x) # Exit with status code 0
           if [ "$DIRVARS_GENERATED" = true ]; then 
             # Remove generated configuration file
             rm -f "$TOSCA2CLOUDNET_CONF_FILE"
           fi
           echo -e "\nSee you soon ..."
           exit 0
           ;;
        *) echo -e "${bold}${red}Error${reset} Invalid menu choice..." && sleep 2
    esac
}


################################################################################
# MAINtenant le programme commence  !!!!!!!!!!!!!                              #
################################################################################
# Define colors
normal="\e[0;"
bold="\e[1;"
red="31m"
green="32m"
yellow="33m"
blue="34m"
magenta="35m"
cyan="36m"
white="37m"
reset="\e[m"
blink="5m"


# Guess where are located the software
CLOUDNET_BINDIR="$PWD/.."
Continue=1
while [ $Continue -eq 1 ]
do
  CLOUDNET_RC=$(find "$CLOUDNET_BINDIR" -name cloudnet_rc.sh)
  if [ -z "${CLOUDNET_RC}" ]
  then
    CLOUDNET_BINDIR="${CLOUDNET_BINDIR}/.."
  else
    CLOUDNET_BINDIR=$(dirname "${CLOUDNET_RC}")
    Continue=0
  fi
done

# Load cloundnet commands.
# shellcheck source=bin/cloudnet_rc.sh
source "${CLOUDNET_BINDIR}/cloudnet_rc.sh"

# Variable used to know if the Syntax checking has bee done
SYNTAX_CHECK=False

# Variable used to know if the results has been placed in generated directories
DIRVARS_GENERATED=False

################################################################################
# Get the targets directories from the tosca2cloudnet.yaml file
################################################################################
TOSCA2CLOUDNET_CONF_FILE=tosca2cloudnet.yaml

# Thanks to Jonathan Peres on github : https://github.com/jasperes/bash-yaml
if [ ! -f "${CLOUDNET_BINDIR}/yaml.sh" ]; then
  echo -e "\n\n        ${bold}${red}Error${reset}: You need to install the yaml parser script"
  echo -e "               You can find it here https://github.com/jasperes/bash-yaml ${reset}"
  echo -e "               Copy it in ${CLOUDNET_BINDIR} directory\n\n"
  pause
  exit 1
else
# shellcheck source=bin/yaml.sh
  source "${CLOUDNET_BINDIR}/yaml.sh"
fi

# if tosca2cloudnet.yaml does'nt exist, create a default one
if [ ! -f "${TOSCA2CLOUDNET_CONF_FILE}" ]; then
   #debug 
   echo "###### Default tosca2cloudnet.yaml creation." >> $TOSCA2CLOUDNET_CONF_FILE

   DIRVARS_GENERATED=true
   #create a config file which will be deleted at the exit of the script
   RESULT_DIR="RESULTS"
   {
     echo "# Configuration of the Alloy generator."
     echo "Alloy:"
     echo "  # Target directory where Alloy files are generated."
     echo "  target-directory: ${RESULT_DIR}/Alloy"
     echo ""
     echo "# Configuration of the network diagram generator."
     echo "nwdiag:"
     echo "  # Target directory where network diagrams are generated."
     echo "  target-directory: ${RESULT_DIR}/NetworkDiagrams"
     echo ""
     echo "# Configuration of the TOSCA diagram generator."
     echo "tosca_diagrams:"
     echo "  # Target directory where network diagrams are generated."
     echo "  target-directory: ${RESULT_DIR}/ToscaDiagrams"
     echo ""
     echo "# Configuration of the UML2 diagram generator."
     echo "UML2:"
     echo "  # Target directory where UML2 diagrams are generated."
     echo "  target-directory: ${RESULT_DIR}/Uml2Diagrams"
     echo ""
     echo "HOT:"
     echo "  # Target directory where HOT templates are generated."
     echo "  target-directory: ${RESULT_DIR}/HOT"
   } >> $TOSCA2CLOUDNET_CONF_FILE
   create_variables $TOSCA2CLOUDNET_CONF_FILE
fi
# Parse tosca2cloudnet.yaml and extract variables
create_variables $TOSCA2CLOUDNET_CONF_FILE

# verify if the target directories are set, if not set default ones
##### TODO : HOT_target_directory (and maybe others) can be set in the TOSCA2CLOUDNET_CONF_FILE 
#####        but are not used in this script currently, so we have to manage it
dirArray=( Alloy_target_directory nwdiag_target_directory tosca_diagrams_target_directory UML2_target_directory)
NBVARSSET=0
for var in "${dirArray[@]}"
do
  if [[ -n ${!var} ]]; then
    ((NBVARSSET+=1))
  fi
done

if (( NBVARSSET > 0 )) && (( NBVARSSET < ${#dirArray[@]} )); then
#  echo "Nombre de variables ${#dirArray[@]}"
#  echo "${NBVARSSET} positionnées"
  echo -e "All the directries are not set."
  echo -e "Would you like to continue as is or correct the $TOSCA2CLOUDNET_CONF_FILE configuration file ?\n"
  echo -e "    Values for target directories:"
  for var in "${dirArray[@]}"
  do
    echo "      ${var} : ${!var}"
  done
  read -rp "Enter choice [ O|n ] " choice
  case $choice in
        n) # exit
           exit 0
           ;;
  esac
fi

if (( NBVARSSET == 0 )); then
   DIRVARS_GENERATED=true
   #create a config file which will be deleted at the exit of the script
   RESULT_DIR="RESULTS"
   {
     echo -e "# Configuration of the Alloy generator." 
     echo -e "Alloy:" 
     echo -e "  # Target directory where Alloy files are generated." 
     echo -e "  target-directory: ${RESULT_DIR}/Alloy" 
     echo -e "" 
     echo -e "# Configuration of the network diagram generator." 
     echo -e "nwdiag:" 
     echo -e "  # Target directory where network diagrams are generated." 
     echo -e "  target-directory: ${RESULT_DIR}/NetworkDiagrams" 
     echo -e "" 
     echo -e "# Configuration of the TOSCA diagram generator." 
     echo -e "tosca_diagrams:" 
     echo -e "  # Target directory where network diagrams are generated." 
     echo -e "  target-directory: ${RESULT_DIR}/ToscaDiagrams" 
     echo -e "" 
     echo -e "# Configuration of the UML2 diagram generator." 
     echo -e "UML2:" 
     echo -e "  # Target directory where UML2 diagrams are generated." 
     echo -e "  target-directory: ${RESULT_DIR}/Uml2Diagrams" 
     echo -e "" 
     echo -e "HOT:" 
     echo -e "  # Target directory where HOT templates are generated." 
     echo -e "  target-directory: ${RESULT_DIR}/HOT" 
   } >> "$TOSCA2CLOUDNET_CONF_FILE"
   create_variables "$TOSCA2CLOUDNET_CONF_FILE"
fi

################################################################################
# Process the input options.
# When called in batch mode, it launch the whole treatement and return a code
# indicating if the statys is OK, OK with warning or KO
################################################################################
# Get the options
optstring=":h:b:s:"

while getopts ${optstring} option; do
   case ${option} in
      h) # display Help
         Help
         exit;;
      b) # change the log file name to be identified executed in batch mode
         _LOG=$(basename "$PWD")_BATCH_MODE-$(date +%F_%H-%M-%S).log
         # Launch the whole stuff process
         TOSCA_SyntaxCheck
         NetworkDiagrams
         TOSCADiagrams
         UML2Diagrams
         AlloySyntax
# take to much time and ressource, not necessary if used for regression testing in CI/CD
#         AlloySolve
         exit;;
      s) # run syntax checking on a single file
         echo -e "${normal}${magenta}  xxx  ${OPTARG^^} xxx ${reset}"
         translate "${OPTARG}"
         if [ "$DIRVARS_GENERATED" = true ]; then 
           rm -f $TOSCA2CLOUDNET_CONF_FILE
         fi
         exit;;
      ?) # incorrect option
         Help
         echo -e "\n\n        ${bold}${red}Error${reset}: Invalid option -${OPTARG} ${reset}\n\n"
         exit;;
   esac
done


################################################################################
# We enter here the interactive mode
################################################################################
# Create a _LOG variable in case we have privious results we want to reuse
_LOG=$(basename "${PWD}")-$(date +%F_%H-%M-%S).log

clear

echo -e "\n\nGenerated files will be placed in the following directories"
for var in "${dirArray[@]}"
do
  echo -e "      ${var} : ${normal}${blue}${!var}${reset}"
done
echo -e "\nA log file will be also available here ${normal}${blue}logs/${_LOG}${reset}"
pause

############################################################################
#  Trap CTRL+Z
################################################################################
trap '' SIGTSTP

################################################################################
# Main logic - infinite loop
################################################################################
while true
do
    show_menus
    read_options
 done
