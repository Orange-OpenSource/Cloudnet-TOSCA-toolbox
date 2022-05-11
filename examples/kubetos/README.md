# kubetos examples

This folder contains visual diagrams generated from [kubetos](https://github.com/Shishqa/kubetos),
a TOSCA framework for deploying Kubernetes.

## Generate visual diagrams

Type
```sh
$ ./run.sh
```

This script
* clones [kubetos GitHub repository](https://github.com/Shishqa/kubetos),
* parses kubetos service templates, and
* generates both [TOSCA](diagrams/tosca/) and [UML 2.0](diagrams/uml2/) diagrams.

## Generated diagrams

# TOSCA Diagram

![TOSCA Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/tosca/service.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/tosca/service.svg).

# UML Component Diagram

![UML Component Diagram 1](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-component-diagram1.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-component-diagram1.svg).

# UML Component Diagram including relationship nodes

![UML Component Diagram 2](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-component-diagram2.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-component-diagram2.svg).

# UML Deployment Diagram

![UML Deployment Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-deployment-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/service-uml2-deployment-diagram.svg).

# UML Class Diagrams

## Kubernetes profile

![UML Class Diagram - Kubernetes profile](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/profiles-kubernetes-types-node-uml2-class-diagram.png)

![UML Class Diagram - Kubernetes profile](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/profiles-kubernetes-types-objects-uml2-class-diagram.png)

## OpenStack profile

![UML Class Diagram - OpenStack profile](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/kubetos/diagrams/uml2/profiles-openstack-types-node-uml2-class-diagram.png)

### All generated diagrams

All generated diagrams are available at
* [diagrams/tosca/](diagrams/tosca/)
* [diagrams/uml2/](diagrams/uml2/)
