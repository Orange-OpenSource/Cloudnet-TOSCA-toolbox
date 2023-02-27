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
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: TOSCA to Cloudnet Translator
######################################################################

FROM python:alpine
MAINTAINER Philippe Merle <Philippe.Merle@inria.fr>

COPY requirements.txt /requirements.txt

# JLC : proxy to be added for building inside a docker in a Virtualbox VM
# RUN export http_proxy=http://172.17.0.1:3128/ && \
#     export https_proxy=http://172.17.0.1:3128/ && \

RUN pip install --upgrade pip -r /requirements.txt \
    && rm /requirements.txt

ENV PYTHONPATH /

# ENTRYPOINT [ "" , "", ""]
# CMD [ "" ]
