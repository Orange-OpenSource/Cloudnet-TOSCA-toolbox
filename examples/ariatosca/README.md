# AriaTosca examples

This folder contains a modified copy of [AriaTosca examples](https://github.com/apache/incubator-ariatosca/tree/master/examples).

## Generate diagrams

To run Cloudnet TOSCA toolbox on AriaTosca examples, just type
```sh
$ ./run.sh
```

This script
* parses AriaTosca examples and
* generate [TOSCA](diagrams/tosca/), [network](diagrams/network/), and [UML 2.0](diagrams/uml2/) diagrams.

## Generated diagrams

### Clearwater example

#### TOSCA Diagram

![clearwater TOSCA diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/clearwater-single-existing-1.0.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/clearwater-single-existing-1.0.svg).

#### UML Component Diagram

![clearwater UML component diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-single-existing-1.0-uml2-component-diagram1.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-single-existing-1.0-uml2-component-diagram1.svg).

#### UML Deployment Diagram

![clearwater UML deployment diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-single-existing-1.0-uml2-deployment-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-single-existing-1.0-uml2-deployment-diagram.svg).

#### UML Class Diagram

![clearwater UML class diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-uml2-class-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/clearwater-uml2-class-diagram.svg).

### Multi-Tier-1 example

#### TOSCA Diagram

![Multi-Tier-1 TOSCA diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/multi-tier-1-1.0.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/multi-tier-1-1.0.svg).

#### UML Component Diagram

![Multi-Tier-1 UML component diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/multi-tier-1-1.0-uml2-component-diagram1.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/multi-tier-1-1.0-uml2-component-diagram1.svg).

#### UML Deployment Diagram

![Multi-Tier-1 UML deployment diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/multi-tier-1-1.0-uml2-deployment-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/multi-tier-1-1.0-uml2-deployment-diagram.svg).

#### UML Class Diagram

![Multi-Tier-1 UML class diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/non-normative-types-uml2-class-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/non-normative-types-uml2-class-diagram.svg).

### Network-4 example

#### TOSCA Diagram

![Network-4 tosca diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/network-4-1.0.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/tosca/network-4-1.0.svg).

#### UML Deployment Diagram

![Network-4 UML deployment diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/network-4-1.0-uml2-deployment-diagram.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/uml2/network-4-1.0-uml2-deployment-diagram.svg).

#### Network Diagram

![Network-4 network diagram](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/network/network-4-1.0.png)

A SVG version is available [here](https://raw.githubusercontent.com/Orange-OpenSource/Cloudnet-TOSCA-toolbox/master/examples/ariatosca/diagrams/network/network-4-1.0.svg).

### All generated diagrams

All generated diagrams are available in
* [diagrams/tosca/](diagrams/tosca/)
* [diagrams/network/](diagrams/network/)
* [diagrams/uml2/](diagrams/uml2/)

## Modifications

The modifications in AriaTosca files are tagged by the `#ISSUE:` string and are mainly related to:
* the absence of the `tosca_definitions_version` keyname
* a node template name is expected instead of a node type name in requirement assignments
* `policies` shall be a list of policies instead of a map
* `dependencies` shall be a list of artifacts
* `_extensions` keyname replaced by `metadata` keyname
* missed definitions such as `aria.Plugin` policy type, required `hostname` property, `occurrences`
