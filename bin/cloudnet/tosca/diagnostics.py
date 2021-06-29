######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-21 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Xavier-Frédéric Moulet <xavier-frederic.moulet@orange.com>
# Software description: TOSCA to Cloudnet Translator
######################################################################


# simple structured logging
import json
import os
import sys

from cloudnet.tosca.yaml_line_numbering import Coord

outfile = None  # file object to output to
template = ""  # name of the template file
return_code = 0  # all OK by default


def configure(template_filename, log_filename):
    global outfile, template
    template = template_filename
    if log_filename:
        outfile = open(log_filename, "a")


def diagnostic(gravity, file, message, cls, value=None, **kwargs):
    global return_code, outfile, template
    if gravity == "info" or outfile is None:
        return
    return_code = 1
    if file == "":
        file = template
    if isinstance(value, Coord):
        kwargs.update(
            gravity=gravity,
            file=file,
            message=message,
            cls=cls,
            value=str(value),
            line=value.line,
            column=value.column,
        )
    else:
        kwargs.update(
            gravity=gravity,
            file=file,
            message=message,
            cls=cls,
            value=str(value),
            line=0,
            column=0,
        )
    json.dump(kwargs, outfile, skipkeys=True)
    outfile.write("\n")
