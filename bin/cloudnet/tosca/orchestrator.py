######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-22 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <jeanluc.coulin@orange.com>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import logging  # for logging purposes.

import cloudnet.tosca.configuration as configuration
from cloudnet.tosca.processors import Generator


ORCHESTRATION = 'Orchestration'
configuration.DEFAULT_CONFIGURATION[ORCHESTRATION] = {
    # Target directory where rollout manifest will be writen.
    Generator.TARGET_DIRECTORY: "Results/" + ORCHESTRATION,
    # Do I need to run
    "do_i_need_to_execute": ["NO"],
}

configuration.DEFAULT_CONFIGURATION["logging"]["loggers"][__name__] = {
    "level": "INFO",
}
class Orchestrator(Generator):

    def generation(self):
        self.info("Orchestrator template generation")
        self.info("Verifions que l'on doit s'executer")
        if not self.configuration.get(ORCHESTRATION, "do_i_need_to_execute"):
            self.info(" >>>> On ne fait rien <<<<")
            return 0
        self.info("on fait le traiement")
