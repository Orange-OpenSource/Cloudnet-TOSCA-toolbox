# TosKer examples

This folder contains visual diagrams generated from [TosKer examples](https://github.com/di-unipi-socc/TosKer/tree/master/data/examples).

## Generate visual diagrams

Type
```sh
$ ./run.sh
```

This script
* clones [TosKer GitHub repository](https://github.com/di-unipi-socc/TosKer),
* modifies `tosker-types.yaml` files,
* parses TosKer examples, and
* generates both [TOSCA](diagrams/tosca/) and [UML 2.0](diagrams/uml2/) diagrams.

## Generated diagrams

### TosKer Types

![TosKer types](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/tosker-types-uml2-class-diagram.png)

### Node Mongo Example

#### TOSCA Diagram

![Node Mongo - TOSCA Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/tosca/node-mongo.csar/node-mongo.png)

#### UML Deployment Diagram

![Node Mongo - UML Deployment Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/node-mongo.csar/node-mongo-uml2-deployment-diagram.png)

#### UML Component Diagrams

![Node Mongo - UML Component Diagram 1](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/node-mongo.csar/node-mongo-uml2-component-diagram1.png)

![Node Mongo - UML Component Diagram 2](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/node-mongo.csar/node-mongo-uml2-component-diagram2.png)

### Sockshop Example

#### TOSCA Diagram

![Sockshop - TOSCA Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/tosca/sockshop.csar/sockshop.png)

#### UML Deployment Diagram

![Sockshop - UML Deployment Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/sockshop.csar/sockshop-uml2-deployment-diagram.png)

#### UML Component Diagrams

![Sockshop - UML Component Diagram 1](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/sockshop.csar/sockshop-uml2-component-diagram1.png)

![Sockshop - UML Component Diagram 2](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/sockshop.csar/sockshop-uml2-component-diagram2.png)

### Thinking Example

#### TOSCA Diagram

![Thinking - TOSCA Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/tosca/thinking.csar/thinking.png)

#### UML Deployment Diagram

![Thinking - UML Deployment Diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/thinking.csar/thinking-uml2-deployment-diagram.png)

#### UML Component Diagrams

![Thinking - UML Component Diagram 1](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/thinking.csar/thinking-uml2-component-diagram1.png)

![Thinking - UML Component Diagram 2](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/TosKer/diagrams/uml2/thinking.csar/thinking-uml2-component-diagram2.png)

### All generated diagrams

All generated diagrams are available at
* [diagrams/tosca/](diagrams/tosca/)
* [diagrams/uml2/](diagrams/uml2/)

## Modifications

TosKer examples contain some typing errors.
The main errors are located into the [TosKer profile](https://github.com/di-unipi-socc/TosKer/blob/master/data/tosker-types.yaml), a set of TOSCA types dedicated to TosKer.
The corrections of these errors are available into the [updated-tosker-types.yaml](updated-tosker-types.yaml) file (see tags `#ISSUE`).
