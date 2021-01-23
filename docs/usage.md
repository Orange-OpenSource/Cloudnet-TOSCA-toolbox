# Cloudnet TOSCA Toolbox Usage
=

## Commands

Cloudnet TOSCA Toolbox commands are defined in the ```bin/cloudnet_rc.sh``` file.

Type:

```sh
$ . bin/cloudnet_rc.sh
```

to access the following Cloudnet TOSCA Toolbox commands.

### ```translate```

```translate``` parses one or several TOSCA files, type checks them, and generates related TOSCA/network/UML2 diagrams and Alloy specifications.

For instance, type:

```sh
$ translate tosca_file.yaml
```

### ```alloy_parse```

```alloy_parse``` parses one or several generated Alloy specifications.

For instance, type:

```sh
$ alloy_parse <filename>.als
```

### ```alloy_execute```

```alloy_execute``` analyses one or several generated Alloy specifications, i.e. execute generated Alloy commands.

For instance, type:

```sh
$ alloy_execute <filename>.als
```

### ```generate_tosca_diagrams```

```generate_tosca_diagrams``` generates one or several TOSCA diagrams.

For instance, type:

```sh
$ generate_tosca_diagrams <filename>.dot
```

### ```generate_network_diagrams```

```generate_network_diagrams``` generates one or several network diagrams.

For instance, type:

```sh
$ generate_network_diagrams <filename>.nwdiag
```

### ```generate_uml2_diagrams```

```generate_uml2_diagrams``` generates one or several UML2 diagrams.

For instance, type:

```sh
$ generate_uml2_diagrams <filename>.plantuml
```

## Environment variables
-

Following environment variables are used to configure default command line options of Cloudnet TOSCA Toolbox tools.

### ```ALLOY_PARSE_OPTS```

TBC

### ```ALLOY_EXECUTE_OPTS```

TBC

### ```CLOUDNET_BINDIR```

```CLOUDNET_BINDIR``` is for defining the directory where Cloudnet TOSCA Toolbox binaries are.

For instance, type:
```sh
$ export CLOUDNET_BINDIR=/path_where_Cloudnet_TOSCA_Toolbox_is/bin
```

### ```DOCKER_OPTS```

```DOCKER_OPTS``` is for defining default command line options passed to the ```docker```command.

For instance, type:
```sh
$ export DOCKER_OPTS="--debug --log-level debug"
```
to run Docker containers in debug mode and set the log level to debug.

See https://docs.docker.com/engine/reference/commandline/cli/ for more details.

### ```DOT_OPTS```

```DOT_OPTS``` is for defining default command line options passed to the ```dot```command used by ```generate_tosca_diagrams```.

For instance, type:
```sh
$ export DOT_OPTS="-Tpng"
```

to set the output format to PNG format.

See
http://graphviz.org/doc/info/command.html for more details.

### ```JAVA_OPTS```

```JAVA_OPTS``` is for defining default command line options passed to both ```java``` and ```plantuml``` commands used by
 ```alloy_execute```, ```alloy_parse```, and ```generate_uml2_diagrams```.

For instance, type:
```sh
$ export JAVA_OPTS="-Xms4g -XshowSettings:vm"
```
to set the maximum size of the memory allocation pool of launched JVMs to 4 Gb.

See
https://docs.oracle.com/javase/8/docs/technotes/tools/unix/java.html for more details.

### ```NWDIAG_OPTS```

```NWDIAG_OPTS``` is for defining default command line options passed to the ```nwdiag```command used by ```generate_network_diagrams```.

For instance, type:
```sh
$ export NWDIAG_OPTS="-Tsvg"
```

to set the output format to SVG format.

See
http://blockdiag.com/en/nwdiag/introduction.html#usage for more details.

### ```PLANTUML_OPTS```

```PLANTUML_OPTS``` is for defining default command line options passed to the ```plantuml```command used by ```generate_uml2_diagrams```.

For instance, type:
```sh
export PLANTUML_OPTS="-DPLANTUML_LIMIT_SIZE=50000"
```

to set the limit size of generated PlantUML diagrams.

See
https://plantuml.com for more details.

### ```PYTHON_OPTS```

```PYTHON_OPTS``` is for defining default command line options passed to the ```python```command used by ```translate```.

For instance, type:
```sh
export PYTHON_OPTS=" TBC "
```

TBC

See https://docs.python.org/3/using/cmdline.html for more details.

### ```TOSCAWARE_OPTS```

```TOSCAWARE_OPTS``` is for defining default command line options passed to the ```toscaware```command used by ```translate```.

For instance, type:
```sh
export TOSCAWARE_OPTS=" TBC "
```

TBC

# External used software tools

Cloudnet TOSCA Toolbox reuses the following set of external software tools:

* [Alloy](https://alloytools.org)

* [Docker](https://www.docker.com)

* [Graphviz](http://graphviz.org)

* [Java](https://www.java.com)

* [nwdiag](http://blockdiag.com/en/nwdiag/)

* [PlantUML](https://plantuml.com)

* [Python](https://www.python.org)
