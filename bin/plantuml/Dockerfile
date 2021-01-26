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

FROM anapsix/alpine-java:latest
MAINTAINER Philippe Merle <Philippe.Merle@inria.fr>

ENV PLANTUML_VERSION 1.2021.0
ENV LANG en_US.UTF-8
RUN apk add --update --no-cache \
        graphviz \
        ttf-freefont ttf-droid ttf-droid-nonlatin \
        curl \
    && curl -L https://sourceforge.net/projects/plantuml/files/plantuml.${PLANTUML_VERSION}.jar/download -o /plantuml.jar \
    && apk del curl

# ENTRYPOINT [ "java", "-DPLANTUML_LIMIT_SIZE=50000", "-Xmx1024m", "-jar", "/plantuml.jar" ]
CMD [ "-h" ]
