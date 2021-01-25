# Cloudnet-TOSCA-toolbox OASIS TOSCA example

These examples are an extraction from section 2 of the [OASIS TOSCA-Simple-Profile-YAML v1.2](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.2/os/TOSCA-Simple-Profile-YAML-v1.2-os.html#_Toc528072909).

They show how to model applications with TOSCA Simple Profile using YAML by example starting <br />
with a simple  template up through examples that show complex composition modeling

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

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Back to top](#cloudnet-tosca-toolbox-oasis-tosca-example)

## A Usefull run.sh script

This script is located int the bin directory of the repository

### Batch or cli mode

- The trace result  is in a log file located in logs/ directory
- The resulting files are located in a RESULTS/ directory where<br />
  you will find the following diretories<br />
  Alloy : alloy translation of yaml files<br />
  NetworkDiagrams : nwdiag and png files<br />
  ToscaDiagrams : dot and png files<br />
  Uml2Diagrams : platuml and png files
  
```sh
cd examples/OpenStack 

## Run all the tools (TOSCA syntax checking, diagrams generation, Alloy syntax checking)
../../bin -b

## Run TOSCA syntax checking on one file
../../bin -s filename

```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Back to top](#cloudnet-tosca-toolbox-oasis-tosca-example)

### Using the interactive mode

```sh
cd examples/OpenStack 
../../bin/run.sh
```

It will say you where the results files will be located :

```sh
Generated files will be placed in the following directories
      Alloy_target_directory : RESULTS/Alloy
      nwdiag_target_directory : RESULTS/NetworkDiagrams
      tosca_diagrams_target_directory : RESULTS/ToscaDiagrams
      UML2_target_directory : RESULTS/Uml2Diagrams

A log file will be also available here logs/

         Press [Enter] key to continue...
```

and display the following menu

```sh
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

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Back to top](#cloudnet-tosca-toolbox-oasis-tosca-example)

## Examples description

| Example file name  | Description                                         |
|--------------------|-----------------------------------------------------|
|BlockStorage-1.yaml | TOSCA simple profile with server and attached block storage using the normative AttachesTo Relationship Type.|
|BlockStorage-2.yaml | TOSCA simple profile with server and attached block storage using a custom AttachesTo Relationship Type.|
|BlockStorage-3.yaml | TOSCA simple profile with server and attached block storage using a named Relationship Template for the storage attachment.|
|BlockStorage-4.yaml | TOSCA simple profile with a Single Block Storage node shared by 2-Tier Application with custom AttachesTo Type and implied relationships.|
|BlockStorage-5.yaml | TOSCA simple profile with a single Block Storage node shared by 2-Tier Application with custom AttachesTo Type and explicit Relationship Templates.|
|BlockStorage-6.yaml | TOSCA simple profile with 2 servers each with different attached block storage.|
|Compute.yaml | TOSCA simple profile that just defines a single compute instance and selects a (guest) host Operating System from the Compute node’s properties. Note, this example does not include default values on inputs properties.|
|Container-1.yaml | TOSCA simple profile with wordpress, web server and mysql on the same server.|
|example-2-1.yaml | a single server with predefined properties.|
|example-2-2.yaml | a single server with predefined properties.|
|example-2-3.yaml | a single server with MySQL software on top.|
|example-2-4.yaml | a single server with MySQL software on top.|
|example-2-5.yaml | MySQL and database content.|
|example-2-6.yaml | a two-tier application servers on two|
|example-2-7.yaml | a two-tier application on two servers.|
|example-2-8.yaml | a two-tier application on two servers.|
|example-2-9.yaml | Definition of custom WordpressDbConnection relationship type|
|example-2-10.yaml | a generic dependency between two nodes.|
|example-2-14.yaml | a TOSCA Orchestrator selectable database using node template.|
|example-2-20.yaml | a scaling web server.|
|example-2-21.yaml | hosting requirements and placement policy.|
|example-2-22.yaml | TOSCA simple profile that just defines a YAML macro for commonly reused Compute properties.|
|example-8.6.1.yaml | Specifying a network outside the application’s Service Template|
|example-8.6.2.yaml | Specifying network requirements within the application’s Service Template|
|Network-1.yaml | TOSCA simple profile with 1 server bound to a new network|
|Network-2.yaml | TOSCA simple profile with 1 server bound to an existing network|
|Network-3.yaml | TOSCA simple profile with 2 servers bound to the 1 network|
|Network-4.yaml | TOSCA simple profile with 1 server bound to 3 networks|
|ObjectStorage-1.yaml | Tosca template for creating an object storage service.|
|SoftwareComponent-1.yaml | TOSCA Simple Profile with a SoftwareComponent node with a declared Virtual machine (VM) deployment artifact that automatically deploys to its host Compute node.|
|WebServer-DBMS-1.yaml | TOSCA simple profile with WordPress, a web server, a MySQL DBMS hosting the application’s database content on the same server. Does not have input defaults or constraints.|
|WebServer-DBMS-2.yaml | TOSCA simple profile with a nodejs web server hosting a PayPal sample application which connects to a mongodb database.|

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[Back to top](#cloudnet-tosca-toolbox-oasis-tosca-example)
