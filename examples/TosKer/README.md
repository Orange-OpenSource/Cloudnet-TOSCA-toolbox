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

Following are some generated diagrams

TODO

All generated diagrams are available in
* [diagrams/tosca/](diagrams/tosca/)
* [diagrams/uml2/](diagrams/uml2/)

## Modifications

TosKer examples contain some typing errors.
The main errors are located into the [TosKer profile](https://github.com/di-unipi-socc/TosKer/blob/master/data/tosker-types.yaml), a set of TOSCA types dedicated to TosKer.
The corrections of these errors are available into the (updated-tosker-types.yaml) file (see tags `#ISSUE`).
