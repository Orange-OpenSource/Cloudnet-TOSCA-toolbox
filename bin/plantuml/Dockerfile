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

FROM docker.io/alpine:3

MAINTAINER Philippe Merle <Philippe.Merle@inria.fr>

ENV PLANTUML_VERSION 1.2021.13
ENV LANG en_US.UTF-8

RUN apk add --update --no-cache \
         openjdk8-jre \
         graphviz \
         ttf-freefont ttf-droid ttf-droid-nonlatin \
         curl \
    && apk del curl

#TODO: following doesn't work!
# curl -L https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar -o /plantuml.jar

COPY plantuml.jar .

# ENTRYPOINT [ "java", "-DPLANTUML_LIMIT_SIZE=50000", "-Xmx1024m", "-jar", "/plantuml.jar" ]
CMD [ "-h" ]
