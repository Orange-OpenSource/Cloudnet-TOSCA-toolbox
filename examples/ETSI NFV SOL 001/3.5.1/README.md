Cloudnet-TOSCA-toolbox ETSI NFV SOL 001 example
=
These examples are ... TO BE COMPLETED ...

You can experiment the TOSCA-toolbox with these yaml files.  

## Table of contents
1. [Manual procedure](#manual-procedure)
2. [Usefull run.sh script](#A-Usefull-run.sh-script)
    - [Batch or cli mode](#batch-or-cli-mode)
    - [Using the interactive mode](#using-the-interactive-mode)
3. [Examples description](#examples-description)

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
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#cloudnet-tosca-toolbox-etsi-nfv-sol-001-example)

## A Usefull run.sh script

This script is located int the bin directory of the repository

### Batch or cli mode

- The trace result  is in a log file located in logs/ directory
- The resulting files are located in a RESULTS/ directory where
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
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#cloudnet-tosca-toolbox-etsi-nfv-sol-001-example)

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
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#cloudnet-tosca-toolbox-etsi-nfv-sol-001-example)

## Examples description
| Example file name  | Description                                         | Status (Draft, Finished, Excluded) |
|--------------------|-----------------------------------------------------|------------------------------------|
|example_A.2-01.yaml| Relational database, simple|Draft|
|example_A.2-sunshinedbcomplex.vnfd.tosca.yaml| Relational database, complex |Draft|
|example_A.2-sunshine.vnfd.tosca.yaml| Relational database, non-scalable|Draft|
|example_A.2-sunshineVNF.yaml| Relational database, non-scalable|Draft|
|example_A.3.2-01.yaml||Draft|
|example_A.3.2-02.yaml||Draft|
|example_A.3.3-01.yaml||Draft|
|example_A.4-01.yaml||Draft|
|example_A.4-02.yaml| composition of Vdu.Compute, Vdu.VirtualBlockStorage and VduCp. |Draft|
|example_A.4-03.yaml||Draft|
|example_A.5-01.yaml| Relational database, simple|Draft|
|example_A.6.1-01.yaml| Complex scaling example (uniform delta value) described with policies|Draft|
|example_A.6.2-01.yaml| Complex example (uniform and non-uniform delta value) described with policies|Draft|
|example_A.7.2-01.yaml||Draft|
|example_A.7.3-01.yaml||Draft|
|example_A.8-01.yaml| Relational database, simple|Draft|
|example_A.10-01.yaml| the service template of a PNFD|Draft|
|example_A.11-MyExampleNs_big.yaml| myExampleNs with big flavour|Draft|
|example_A.11-MyExampleNs_small.yaml| myExampleNs with small flavour|Draft|
|example_A.11-MyExampleNs_Type.yaml| type definition of tosca.MyExampleNS|Draft|
|example_A.11-MyExampleNs.yaml| my service|Draft|
|example_A.12-01.yaml| myExampleNs with small flavour|Draft|
|example_A.12-02.yaml| Example VNF4 type|Draft|
|example_A.12-MyExampleNS_2.yaml| Relational database, simple|Draft|
|example_A.12-MyExampleNs_Type.yaml| type definition of tosca.MyExampleNS|Draft|
|example_A.13-01.yaml| Relational database, simple|Draft|
|example_A.13-02.yaml| Relational database, simple|Draft|
|example_A.14-01.yaml| VNF FG Model for example_NS|Draft|
|example_A.14-etsi_nfv_example_vnf1.yaml|  VNF Descriptor for VNF1|Draft|
|example_A.14-etsi_nfv_example_vnf2.yaml| VNF Descriptor for VNF2|Draft|
|example_A.14-etsi_nfv_example_vnf3.yaml| VNF Descriptor for VNF3|Draft|
|example_A.15-01.yaml||Draft|
|example_A.16-01.yaml||Draft|
|example_A.17-01.yaml| myExampleNs with scaling aspects|Draft|
|example_A.17-CentralProcess_1_0.yaml||Draft|
|example_A.17-Database_1_0.yaml||Draft|
|example_A.17-FrontEnd_1_0.yaml||Draft|
|example_A.17-MyScalableNs.yaml||Draft|
|example_A.17-SupportFrontEndNs.yaml||Draft|

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Back to top](#cloudnet-tosca-toolbox-etsi-nfv-sol-001-example)
