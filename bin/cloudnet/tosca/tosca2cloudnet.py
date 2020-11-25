######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: TOSCA to Cloudnet Translator
######################################################################

"""
CLI entry point to show how TOSCA to Cloudnet Translator can be used.

It can be used as,
- python3 tosca2cloudnet.py --template-file=<path to the YAML template>
- python3 tosca2cloudnet.py --template-file=<path to the CSAR zip file>
- python3 tosca2cloudnet.py --template-file=<URL to the template or CSAR>

e.g.
python3 tosca2cloudnet.py --template-file=etsi_nfv_sol001_vnfd_0_8_types.yaml

python3 tosca2cloudnet.py --template-file=sunshine.vnfd.tosca.yaml
"""

import argparse
import cloudnet.tosca.importers as importers
import cloudnet.tosca.processors as processors
from cloudnet.tosca.syntax import SyntaxChecker
from cloudnet.tosca.type_system import TypeSystem, TypeChecker
from cloudnet.tosca.alloy import AlloyGenerator
from cloudnet.tosca.uml2_diagrams import PlantUMLGenerator
from cloudnet.tosca.tosca_diagrams import ToscaDiagramGenerator
from cloudnet.tosca.network_diagrams import NwdiagGenerator
from cloudnet.tosca.hot import HOTGenerator
import sys # argv and stderr.
import os

ALIASED_TOSCA_SERVICE_TEMPLATES='aliased_tosca_service_templates'
import cloudnet.tosca.configuration as configuration
configuration.DEFAULT_CONFIGURATION[ALIASED_TOSCA_SERVICE_TEMPLATES] = {
    'tosca_simple_yaml_1_0.yaml': 'file:' + os.path.dirname(__file__) + '/profiles/tosca_simple_yaml_1_0/types.yaml',
    'tosca_simple_yaml_1_1.yaml': 'file:' + os.path.dirname(__file__) + '/profiles/tosca_simple_yaml_1_1/types.yaml',
    'tosca_simple_yaml_1_2.yaml': 'file:' + os.path.dirname(__file__) + '/profiles/tosca_simple_yaml_1_2/types.yaml',
    'tosca_simple_yaml_1_3.yaml': 'file:' + os.path.dirname(__file__) + '/profiles/tosca_simple_yaml_1_3/types.yaml'
}

def main(argv):
    try:
        # Parse arguments.
        parser = argparse.ArgumentParser(prog="tosca2cloudnet")
        parser.add_argument('--template-file',
                            metavar='<filename>',
                            required=True,
                            help='YAML template or CSAR file to parse.')
        (args, extra_args) = parser.parse_known_args(argv)

        # Load configuration.
        config = configuration.load()

        # Load the TOSCA service template.
        try:
            tosca_service_template = importers.imports(args.template_file, config.get(ALIASED_TOSCA_SERVICE_TEMPLATES))
        except Exception as e:
            print(processors.CRED, '[ERROR] ', args.template_file , ': ', e, processors.CEND, sep='', file=sys.stderr)
            exit(1)

        # Syntax checking.
        syntax_checker = SyntaxChecker(tosca_service_template, config)
        if syntax_checker.check() == False or syntax_checker.nb_errors > 0:
            exit(1)

        # Create a TOSCA type system.
        type_system = TypeSystem(config)

        # Type checking.
        type_checker = TypeChecker(tosca_service_template, config, type_system)
        if type_checker.check() == False or type_checker.nb_errors > 0:
            exit(1)

        # Generate Alloy specifications, UML2, network, TOSCA diagrams and Heat templates.
        type_checker.file = None
        for generator_class in [AlloyGenerator, PlantUMLGenerator, NwdiagGenerator, ToscaDiagramGenerator, HOTGenerator]:
            generator = generator_class(generator=type_checker)
            generator.generation()
    except Exception as e:
        print(processors.CRED, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print(processors.CEND, file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])
