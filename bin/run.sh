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
   touch logs/"$_LOG"

   # All description files translation
   OLDIFS=$IFS
   IFS=$'\n'
   echo -e "\n${normal}${magenta}*** Descriptor files syntax checking ***${reset}" | tee -a logs/"${_LOG}"
# TODO: Jean-Luc following commits need to be merged.
# Next line committed by Jean-Luc in https://github.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/commit/0844e5de97c8834cd3d6b21ecb521a9cdcf8dcdc#diff-00a80c5821edea2ebf676056aa4c9a24e57379ef52cefecb2ccffaaf4cc362c9
#   for filename in $(grep -r --include=*.{yaml,yml} -l 'tosca_definitions_version:') $(find . -iname '*.csar' -o -iname '*.zip')
# Next line committed by Philippe in https://github.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/commit/ff3ee75f572e6d665d05ad89496fcbff07503f53#diff-00a80c5821edea2ebf676056aa4c9a24e57379ef52cefecb2ccffaaf4cc362c9
   for filename in $(find . -not -path "./${DeclarativeWorkflows_target_directory}/*" -iname '*.yaml' -o -iname '*.yml' | xargs grep -l 'tosca_definitions_version:') $(find . -iname '*.csar' -o -iname '*.zip')
     do
# Warning: "${filename^^}" does not work on MacOS!
#      echo -e "\n${normal}${magenta}    ${filename^^} ${reset}" | tee -a logs/"${_LOG}"
       echo -e "\n${normal}${magenta}    `echo $filename | tr [a-z] [A-Z]` ${reset}" | tee -a logs/${_LOG}
       translate "$filename" 2>&1 | tee -a logs/"${_LOG}"
     done
   IFS=$OLDIFS
   SYNTAX_CHECK=true
}

################################################################################
# Diagrams generation
################################################################################
DiagramsGen()
{
   # get arguments
   local DIAGRAM_TYPE="$1"
   local TARGET_DIRECTORY="$2"

   # set the files types to search for according to diagram type
   case $DIAGRAM_TYPE in
      network)
           FILE_TYPE="*.nwdiag"
           ;;
      TOSCA)
           FILE_TYPE="*.dot"
           ;;
      UML2)
           FILE_TYPE="*.plantuml"
           ;;
       * ) echo -e "ERROR argument $DIAGRAM_TYPE not expected";;
   esac

   # A tiltle of process ongoing
   echo -e "\n${normal}${magenta}*** Generating $DIAGRAM_TYPE diagrams ***${reset}" | tee -a logs/"${_LOG}"

   local GENERATE=false
   # Verify that we have diagrams to generate
   if [ -d "$TARGET_DIRECTORY" ];
   then
      # Is there some files ?
      if test -n "$(find "${TARGET_DIRECTORY}" -maxdepth 1 -name $FILE_TYPE -print -quit)"
      then
         # Were these files just generated ?
         if [ "$SYNTAX_CHECK" = true ];
         then
            GENERATE=true
         else
            # Ask if we generate the diagrams with old files
            echo -e "${normal}${magenta}Previous generated $DIAGRAM_TYPE files found.${reset}"
            echo -e "Would you like to Generate diagrams whith them or generate newer ones ? [Gg|Nn]" gn
            while true; do
               read -rs -n 1 gn
               case $gn in
                  [Gg]* )
                        GENERATE=true
                        break;;
                  [Nn]* )
                        echo -e "\n         So run \"TOSCA syntax checking\" option before generating diagrams.\n"
                        break;;
                  * ) echo "Please answer [Gg]enerate or [Nn]o.";;
               esac
            done
         fi
         # Generate diagams
         if [ $GENERATE ];
         then
            case $DIAGRAM_TYPE in
               network)
                     # generate_network_diagrams "$TARGET_DIRECTORY/$FILE_TYPE" 2>&1 |tee -a logs/"${_LOG}"
                     generate_network_diagrams "$TARGET_DIRECTORY"/*.nwdiag 2>&1 |tee -a logs/"${_LOG}"
                     ;;
               TOSCA)
                     generate_tosca_diagrams "$TARGET_DIRECTORY"/*.dot 2>&1 |tee -a "logs/${_LOG}"
                     ;;
               UML2)
                     generate_uml2_diagrams "$TARGET_DIRECTORY"/*.plantuml 2>&1 |tee -a "logs/${_LOG}"
                     ;;
                * )  echo -e "ERROR argument $DIAGRAM_TYPE not expected";;
            esac
         fi
      fi
   else
      echo -e "\n         The target directory was not found."
      echo -e "         Be sure to run \"TOSCA syntax checking\" option before generating diagrams.\n"
   fi
}

################################################################################
# Alloy syntax checking
################################################################################
AlloySyntax()
{
   # Verify if Syntax checking has been done
   if [ -d "${Alloy_target_directory}" ];
   then
      if [ "$SYNTAX_CHECK" = true ]; then
          echo -e "\n${normal}${magenta}*** Checking ALLOY syntax ***${reset}" | tee -a "logs/${_LOG}"
          alloy_parse "${Alloy_target_directory}/*.als" 2>&1 |tee -a "logs/${_LOG}"
      else
         # If not, ask if we create diagrams with older generated files if they exist
         if test -n "$(find "${Alloy_target_directory}" -maxdepth 1 -name '*.als' -print -quit)"
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
   else
      echo -e "\n${normal}${magenta}*** No Alloy (*.als) files found ***${reset}" | tee -a logs/"${_LOG}"
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
      # if [ -d "${Alloy_target_directory}" ] && test -n "$(find ${Alloy_target_directory} -maxdepth 1 -name '*.als' -print -quit)"
      if [ -d "${Alloy_target_directory}" ] && find "${Alloy_target_directory}" -maxdepth 1 -name '*.als' -print -quit
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
  read -rp "         Press [Enter] key to continue..."
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
    echo "      D. Show the diagnostic (errors with line and column numbers) file (type q to leave)"
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
    read -rp "Enter choice [ 1-5 cDlwx ] " choice
    case $choice in
        1) # Launch TOSCA syntax checking
           echo -e "\n"
           time TOSCA_SyntaxCheck
           pause
           ;;
        2) # Launch ALL diagrams generation
           echo -e "\n"
           time ( time DiagramsGen network "$nwdiag_target_directory";
           time DiagramsGen TOSCA "$tosca_diagrams_target_directory";
           time DiagramsGen UML2 "$UML2_target_directory";
           )
           pause
           ;;
        3) # Launch TOSCA syntax checking + ALL diagrams generation
           echo -e "\n"
           TOSCA_SyntaxCheck
           DiagramsGen network "$nwdiag_target_directory"
           DiagramsGen TOSCA "$tosca_diagrams_target_directory"
           DiagramsGen UML2 "$UML2_target_directory"
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
           echo -e "\nRemove generated result directory"
           rm -rf "${RESULT_DIR}"
           pause
           ;;
        D) # Show the diagnostic file formated
           # If logfilname is not set warn the user
           if [ "$SYNTAX_CHECK" = true ]; then
               if [ -z ${_TRANSLATE_LOG+x} ]; then
                  echo -e "\n\n"
                  read -rp "          No diagnostic file created for this session. type any key to continue." choice
               else
                  # Test if file already generated
                  if ! [ -f "logs/${_FORMATTED_TRANSLATE_LOG}" ]; then
                     echo -e "\nFormatting diagnostic log file ... please wait ... "
                     diagnosticFormat "${_TRANSLATE_LOG}"
                  fi
                  less -r "logs/${_FORMATTED_TRANSLATE_LOG}"
               fi
            else
               echo "You need to run \"TOSCA syntax checking\" before launching the alloy syntax checking"
               pause
            fi
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
           DiagramsGen network "$nwdiag_target_directory"
           echo -e "\n TOSCA diagrams generation"
           DiagramsGen TOSCA "$tosca_diagrams_target_directory"
           echo -e "\n UML2 diagrams generation"
           DiagramsGen UML2 "$UML2_target_directory"
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
# Print a string ($3 parameter) on a column of $1 width, after printing the
# first text ($2 parameter named keyname)
# Is it clear ? I doubt ;-)
################################################################################
columnize2 () {
    indent=$1;
    collen=$(($(tput cols)-indent));
    keyname="$2";
    value=$3;
    while [ -n "$value" ] ; do
        printf "%-26s  %-${indent}s\n" "$keyname" "${value:0:$collen}";
        keyname="";
        value=${value:$collen};
    done
}

################################################################################
# Define which jq version to use
################################################################################
myJQ () {
   # Test the linux version
   case $(arch) in
      x86_64)
         # Linux 64 bits architecture
         "${CLOUDNET_BINDIR}"/jq-linux64 '.file, .gravity, .message, .line, .column' "${_SORTED_FILENAME}"
         ;;
      i386)
         # Linux 32 bits architecture
         "${CLOUDNET_BINDIR}"/jq-linux64 '.file, .gravity, .message, .line, .column' "${_SORTED_FILENAME}"
         ;;
      *)
         # Unknown linux architecture
         echo -e "${bold}${red}Error${reset} Unknown architecture to run diagnostic menu..."
         pause
   esac
}
################################################################################
# Display diagnostic file which is given in $1 parameter
#     errors level, line and column numbers, and associated message
################################################################################
diagnosticFormat () {
   # The translate file
   _FILENAME=$1
   _SORTED_FILENAME="${_FILENAME}_SORTED"

   # Reinit output in case of multiple run
   echo "" > logs/"${_FORMATTED_TRANSLATE_LOG}"

   # Verify if there are errors in the diagnostic file
   if [ "$(wc -l <${_FILENAME})" == "0" ]; then
      echo -e "\n\n${bold}${magenta}**** No errors found in diagnostic file ${_FILENAME} ****${reset}\n\n\n" > "logs/${_FORMATTED_TRANSLATE_LOG}"
   fi

   # Sort file on files names in case
   sort -k 4 -o "${_SORTED_FILENAME}" "${_FILENAME}"

   _OLDFILENAME=""
   _INDEX=1
   _SEVERITY=""
   _MESSAGE=""
   _LINE=""
   _NB_ERROR=0
   _NB_WARNING=0
   _NB_INFO=0
   _NB_OTHER=0

   # Loop on the error log file
   while read -r LREAD
   do
       printf "."
       # remove double quotes in string
       LREAD=$(echo $LREAD | tr -d \" )
       case $_INDEX in
           1) # Filename
                  if [ "$_OLDFILENAME" != "${LREAD}" ]; then
                  # If we are not at the begining of the treatement
                  # ie the variable _OLDFILENAME is empty,
                  # We print the numbers of errors found
                  if  [ ! -z "$_OLDFILENAME" ]; then
                        echo -e "\n\011 ----------- Results -----------" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
                        echo -e "\011 ${_NB_ERROR}${bold}${red} ERROR${reset}" >> "logs/${_FORMATTED_TRANSLATE_LOG}" \
                                "  ${_NB_WARNING}${bold}${yellow} WARNING${reset}" >> "logs/${_FORMATTED_TRANSLATE_LOG}" \
                                "  ${_NB_INFO}${bold}${white} INFO${reset}" >> "logs/${_FORMATTED_TRANSLATE_LOG}" \
                                "  ${_NB_OTHER}${bold}${white} UNKNOW${reset}" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
                  fi

                  # print the new filename
                  echo -e "\n== ${bold}${magenta}${LREAD^^}${reset} =============" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
                  # and store it
                  _OLDFILENAME="${LREAD}"
                  _NB_ERROR=0
                  _NB_WARNING=0
                  _NB_INFO=0
                  _NB_OTHER=0
              fi
              ;;
           2) # Gravity
              # Set the color
              _SEVERITY=${LREAD}
              case ${LREAD} in
                 "error")
                     _COLOR="${bold}${red}"
                     ((_NB_ERROR+=1))
                     ;;
                 "warning")
                     _COLOR="${bold}${yellow}"
                     ((_NB_WARNING+=1))
                     ;;
                 "info")
                     _COLOR="${bold}$"
                     ((_NB_INFO+=1))
                     ;;
                  * )
                     echo -e "${bold}${red}Unexpected error ${_LOGSTRING[gravity]}${reset}" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
                     ((_NB_OTHER+=1))
                     ;;
              esac
              ;;
           3) # Get the message
              _MESSAGE=${LREAD}
              ;;
           4) #  Get the Line
              _LINE=${LREAD}
              ;;
           5) #  Get the Column
              echo -e "\011 [${_COLOR}${_SEVERITY^^}${reset}] line ${_LINE} column ${LREAD}" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
              columnize2 45 "                 $(tput setaf 4)MESSAGE$(tput sgr0) :" "${_MESSAGE}" >> "logs/${_FORMATTED_TRANSLATE_LOG}"
              _INDEX=0
              ;;
       esac
       _INDEX=$((_INDEX+1))

   done < <(myJQ)
}

################################################################################
# MAINtenant le programme commence  !!!!!!!!!!!!!                              #
################################################################################
# Define colors
normal="\033[0;"
bold="\033[1;"
red="31m"
green="32m"
yellow="33m"
blue="34m"
magenta="35m"
cyan="36m"
white="37m"
reset="\033[m"
blink="5m"

# Guess where is located the software
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
   RESULT_DIR="RESULTS-$(date +%F_%H-%M-%S)"
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
dirArray=( DeclarativeWorkflows_target_directory Alloy_target_directory nwdiag_target_directory tosca_diagrams_target_directory UML2_target_directory)
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

################################################################################
# Process the input options.
# When called in batch mode, it launch the whole treatement and return a code
# indicating if the statys is OK, OK with warning or KO
################################################################################
# Get the options
optstring=":hbs"

while getopts ${optstring} option; do
   case ${option} in
      h) # display Help
         Help
         exit;;
      b) # change the log file name to be identified executed in batch mode
         _LOG=$(basename "$PWD")_BATCH_MODE-$(date +%F_%H-%M-%S).log
         # Launch the whole stuff process
         TOSCA_SyntaxCheck
         DiagramsGen network "$nwdiag_target_directory"
         DiagramsGen TOSCA "$tosca_diagrams_target_directory"
         DiagramsGen UML2 "$UML2_target_directory"
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
_TRANSLATE_LOG="Translate_diagnostics-"$(date +%F_%H-%M-%S).log
_FORMATTED_TRANSLATE_LOG="FORMATTED_${_TRANSLATE_LOG}"
_TRANSLATE_LOG="logs/"${_TRANSLATE_LOG}

mkdir -p logs 2>/dev/null
clear

# SET environment variables to configure process execution
# Network diagram generation
export NWDIAG_OPTS=""
export TOSCAWARE_OPTS="--diagnostics-file ${_TRANSLATE_LOG}"

echo -e "\n\nGenerated files will be placed in the following directories"
for var in "${dirArray[@]}"
do
  echo -e "      ${var} : ${normal}${blue}${!var}${reset}"
done
echo -e "\nA log file will be also available here ${normal}${blue}logs/${_LOG}${reset}"
if [[ -n ${TOSCAWARE_OPTS} ]]; then
   echo -e "\nA diagnostic error log file will be also available here ${normal}${blue}${_TRANSLATE_LOG}${reset}"
   touch "$_TRANSLATE_LOG"
fi
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
