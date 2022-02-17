# AriaTosca examples

This folder contains a modified copy of [AriaTosca examples](https://github.com/apache/incubator-ariatosca/tree/master/examples).

## Generate diagrams

To run Cloudnet TOSCA toolbox on AriaTosca examples, just type
```sh
$ ./run.sh
```

This command parses AriaTosca examples and generate  [TOSCA](diagrams/tosca/), [network](diagrams/network/), and [UML 2.0](diagrams/uml2/) diagrams.

## Generated diagrams

Following are some generated diagrams

![TODO](TODO)

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
