What is Cloudnet-TOSCA-toolbox?
=
This is a set of tools for TOSCA deployment descriptors (a web portal is available to use the Cloudnet-TOSCA-toolbox at this url: https://toscatoolbox.noprod-b.kmt.orange.com).  

It can be used for syntax and type checking of specifications or resources configuration deployment/update descriptors written in TOSCA.  
It also allow to visualize the associated architecture in different ways (UML, TOSCA, network diagrams).

Prerequisites:  
-
To use this toolset, you'll need Docker, Python, PlantUML, nwdiag and dot.  
However, provided you have Docker, the others are available as containers as follows.  
You can build the Docker images by:  
    $ cd bin/  
    $ ./build.sh

How to use it?  
- 
If you get some TOSCA 1.0, 1.1 or 1.2 templates to check, once you've clone the repository, you can create a directory in the 'examples' directory, and copy your yaml files inside.  
    $ cd examples/  
	$ mkdir my_example  
	$ cp some_place/my_tosca_template_A.yaml my_example/  
	$ ...  

Load Cloudnet commands:  
    $ CLOUDNET_BINDIR=../../bin  
    $ . ${CLOUDNET_BINDIR}/cloudnet_rc.sh  
	
Now, launching the command  
    $ translate my_tosca_template_A.yaml  
will :  
 - check the file yaml,  
 - check the TOSCA syntax and types correction,  
 - translate it into the MIT Alloy language,  
 - generate .dot, .nwdiag and .plantuml templates.  

Then to generate network diagrams, type:  
    $ generate_network_diagrams nwdiag/*.nwdiag  
To get TOSCA diagrams, use the command:  
    $ generate_tosca_diagrams tosca_diagrams/*.dot  
And to generate UML diagrams:  
    $ generate_uml2_diagrams uml2/*.plantuml  
