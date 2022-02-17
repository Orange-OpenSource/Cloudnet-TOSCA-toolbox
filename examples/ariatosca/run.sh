#! /bin/bash
######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2022 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: Cloudnet TOSCA toolbox
######################################################################

# Load cloudnet commands.
CLOUDNET_BINDIR="../../bin"
. "${CLOUDNET_BINDIR}/cloudnet_rc.sh"

# Compile AriaTosca service templates.
translate aria-service-proxy-plugin/plugin.yaml
translate clearwater/types/cassandra.yaml
translate clearwater/types/clearwater.yaml
translate clearwater/types/ims.yaml
translate clearwater/types/smtp.yaml
translate clearwater/clearwater-live-test-existing.yaml
translate clearwater/clearwater-single-existing.yaml
translate hello-world/hello-world.yaml
translate tosca-simple-1.0/use-cases/block-storage-1/block-storage-1.yaml
translate tosca-simple-1.0/use-cases/block-storage-2/block-storage-2.yaml
translate tosca-simple-1.0/use-cases/block-storage-3/block-storage-3.yaml
translate tosca-simple-1.0/use-cases/block-storage-4/block-storage-4.yaml
translate tosca-simple-1.0/use-cases/block-storage-5/block-storage-5.yaml
translate tosca-simple-1.0/use-cases/block-storage-6/block-storage-6.yaml
translate tosca-simple-1.0/use-cases/compute-1/compute-1.yaml
translate tosca-simple-1.0/use-cases/container-1/container-1.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/custom_types/collectd.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/custom_types/elasticsearch.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/custom_types/kibana.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/custom_types/logstash.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/custom_types/rsyslog.yaml
translate tosca-simple-1.0/use-cases/multi-tier-1/multi-tier-1.yaml
translate tosca-simple-1.0/use-cases/network-1/network-1.yaml
translate tosca-simple-1.0/use-cases/network-2/network-2.yaml
translate tosca-simple-1.0/use-cases/network-3/network-3.yaml
translate tosca-simple-1.0/use-cases/network-4/network-4.yaml
translate tosca-simple-1.0/use-cases/non-normative-types.yaml
translate tosca-simple-1.0/use-cases/object-storage-1/object-storage-1.yaml
translate tosca-simple-1.0/use-cases/software-component-1/software-component-1.yaml
translate tosca-simple-1.0/use-cases/webserver-dbms-1/webserver-dbms-1.yaml
translate tosca-simple-1.0/use-cases/webserver-dbms-2/custom_types/paypalpizzastore_nodejs_app.yaml
translate tosca-simple-1.0/use-cases/webserver-dbms-2/webserver-dbms-2.yaml

# Remove generated workflow diagrams.
rm diagrams/uml2/*-workflow-diagram.plantuml

# Generate TOSCA diagrams.
generate_tosca_diagrams diagrams/tosca/*.dot

# Generate network diagrams.
generate_network_diagrams diagrams/network/*.nwdiag

# Generate UML2 diagrams.
generate_uml2_diagrams diagrams/uml2/*.plantuml

# Remove useless generated files.
rm -rf diagrams/tosca/*.dot \
       diagrams/network/*.nwdiag \
       diagrams/uml2/*.plantuml
