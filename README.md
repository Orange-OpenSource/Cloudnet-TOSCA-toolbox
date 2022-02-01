# What is Cloudnet-TOSCA-toolbox?

Cloudnet TOSCA toolbox is an OASIS TOSCA processor for checking and adjusting TOSCA service templates.
TOSCA templates specify service structure and the procedure governing their life cycle. Services are typically application, infrastructure or network services.  
This set of tools is intended for syntax and type checking of any service templates written in TOSCA, including e.g. [NFV descriptors](https://forge.etsi.org/rep/nfv/SOL001).  
It also allows for visualizing the associated architecture in different ways (UML, TOSCA, network diagrams). Have a look to [this video](https://www.youtube.com/watch?v=6yt-mqzbos4).  
A web portal based on this code is available at this url: [https://toscatoolbox.orange.com](https://toscatoolbox.orange.com).

## Table of contents

- [Prerequisites](#prerequisites)<br />
- [How to use it?](#how-to-use-it)<br />
- [Network diagrams generation](#then-to-generate-network-diagrams-type)<br />
- [TOSCA diagrams generation](#to-get-tosca-diagrams-use-the-command)<br />
- [UML diagrams generation](#and-to-generate-uml-diagrams)<br />

## Prerequisites

To use this toolset, you'll need Docker, Python, PlantUML, nwdiag and dot.
However, provided you have Docker, the others are available as containers as follows.
You can build the Docker images by:

```sh
cd bin/  
./build.sh
```

## How to use it?

If you get some TOSCA
[1.0](http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/os/TOSCA-Simple-Profile-YAML-v1.0-os.pdf),
 [1.1](http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.1/os/TOSCA-Simple-Profile-YAML-v1.1-os.pdf),
 [1.2](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.2/os/TOSCA-Simple-Profile-YAML-v1.2-os.pdf)
 or [1.3](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/os/TOSCA-Simple-Profile-YAML-v1.3-os.pdf)
 templates to check, once you've clone the repository, you can create a
 directory in the 'examples' directory, and copy your yaml files inside.  

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

## Then to generate network diagrams, type:  

```sh
generate_network_diagrams nwdiag/*.nwdiag  
```

![Network diagram example](/docs/pictures/OASIS-TOSCA-1.3_example-8.6.1_nw.png)

## To get TOSCA diagrams, use the command:  

```sh
generate_tosca_diagrams tosca_diagrams/*.dot  
```

![TOSCA diagram example](/docs/pictures/OASIS-TOSCA-1.3_example-8.6.1_tosca.png)

## And to generate UML diagrams:  

```sh
generate_uml2_diagrams uml2/*.plantuml  
```

![UML diagram example](/docs/pictures/OASIS-TOSCA-1.3_example-8.6.1_uml2.png)
