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

FROM python:alpine
MAINTAINER Philippe Merle <Philippe.Merle@inria.fr>

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip -r /requirements.txt \
    && rm /requirements.txt

ENV PYTHONPATH /

# ENTRYPOINT [ "" , "", ""]
# CMD [ "" ]
