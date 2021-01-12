Cloudnet-TOSCA-toolbox Openstack example
=
This example show the Openstack components dependency graph written in TOSCA 1.2

You can experiment the TOSCA-toolbox with these yaml files.  

## Table of contents
1. [Manual procedure](#manual-procedure)
2. [Usefull run.sh script](#A-Usefull-run.sh-script)
    - [Batch or cli mode](#batch-or-cli-mode)
    - [Using the interactive mode](#using-the-interactive-mode)

## Manual procedure 
```sh
cd examples/  
mkdir my_example  
cp some_place/my_tosca_template_A.yaml my_example/  
...  
```

Load Cloudnet commands:  
```sh
CLOUDNET_BINDIR=../../bin  
. ${CLOUDNET_BINDIR}/cloudnet_rc.sh  
```	

Now, launching the command  
```sh
translate my_tosca_template_A.yaml  
```

will :  
 - check the file yaml,  
 - check the TOSCA syntax and types correction,  
 - translate it into the MIT Alloy language,  
 - generate .dot, .nwdiag and .plantuml templates.  

Then to generate network diagrams, type:  
```sh
generate_network_diagrams nwdiag/*.nwdiag  
```

To get TOSCA diagrams, use the command:  
```sh
generate_tosca_diagrams tosca_diagrams/*.dot  
```

And to generate UML diagrams:  
```sh
generate_uml2_diagrams uml2/*.plantuml  
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#table-of-contents)

## A Usefull run.sh script

This script is located int the bin directory of the repository

### Batch or cli mode

-  The trace result  is in a log file located in logs/ directory
-  The resulting files are located in a RESULTS/ directory where
  you will find the following diretories 
  Alloy : alloy translation of yaml files
  NetworkDiagrams : nwdiag and png files
  ToscaDiagrams : dot and png files
  Uml2Diagrams : platuml and png files

```sh
cd examples/OpenStack 

## Run all the tools (TOSCA syntax checking, diagrams generation, Alloy syntax checking)
../../bin -b

## Run TOSCA syntax checking on one file
../../bin -s filename

```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#table-of-contents)

### Using the interactive mode
```sh
cd examples/OpenStack 
../../bin/run.sh
```
It will say you where the results files will be located :
```
Generated files will be placed in the following directories
      Alloy_target_directory : RESULTS/Alloy
      nwdiag_target_directory : RESULTS/NetworkDiagrams
      tosca_diagrams_target_directory : RESULTS/ToscaDiagrams
      UML2_target_directory : RESULTS/Uml2Diagrams

A log file will be also available here logs/

         Press [Enter] key to continue...
```

and display the following menu
```
      ~~~~~~~~~~~~~~~~~~~~~~~~~
       TOSCA Toolbox - M E N U 
      ~~~~~~~~~~~~~~~~~~~~~~~~~
      1. TOSCA syntax checking
      2. All diagrams generation
      3. TOSCA syntax checking + diagrams generation
      4. Alloy syntax checking
      5. Alloy solve
      c. Clean results and logs directories
      l. Show the log file (type q to leave)
      w. Launch the whole process
      x. Exit

Enter choice [ 1-5 clwx ] 
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#table-of-contents)
