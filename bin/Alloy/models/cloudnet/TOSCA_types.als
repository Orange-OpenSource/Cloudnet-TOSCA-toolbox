/******************************************************************************
 *
 * Software Name : Cloudnet TOSCA toolbox 
 * Version: 1.0
 * SPDX-FileCopyrightText: Copyright (c) 2020 Orange
 * SPDX-License-Identifier: Apache-2.0
 *
 * This software is distributed under the Apache License 2.0
 * the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
 * or see the "LICENSE-2.0.txt" file for more details.
 *
 * Author: Philippe Merle (INRIA) <philippe.merle@inria.fr>
 *
 * A formal specification of TOSCA in Alloy with Location Graphs.
 *
*******************************************************************************/

/*******************************************************************************
 * This is an encoding of Capability, Relationship, and Node Types defined in
 * https://github.com/oasis-open/tosca-test-assertions/blob/master/Normative-types/normative-types.yml
 *
 * Let's note that this specification was written in a systematic way,
 * i.e., this specification could be generated automatically from normative-types.yml
 * by applying systematic rules only.
 *
 *******************************************************************************/

module TOSCA_types

open TOSCA

/*******************************************************************************
 * Data Types.
 *******************************************************************************/
/*
  tosca.datatypes.Root:
    description: The TOSCA root Data Type all other TOSCA base Data Types derive from.
  tosca.datatypes.Credential:
    derived_from: tosca.datatypes.Root
    description: The Credential type is a complex TOSCA data Type used when describing authorization credentials used to access network accessible resources.
    properties:
      protocol:
        type: string
        description: The optional protocol name.
        required: false
      token_type:
        type: string
        description: The required token type.
        default: password
      token:
        type: string
        description: The required token used as a credential for authorization or access to a networked resource.
      keys:
        type: map
        description: The optional list of protocol-specific keys or assertions.
        required: false
        entry_schema:
          type: string
      user:
        type: string
        description: The optional user (name or ID) used for non-token based credentials.
        required: false
  tosca.datatypes.network.NetworkInfo:
    derived_from: tosca.datatypes.Root
    properties:
      network_name:
        type: string
      network_id:
        type: string
      addresses:
        type: list
        entry_schema:
          type: string
  tosca.datatypes.network.PortInfo:
    derived_from: tosca.datatypes.Root
    properties:
      port_name:
        type: string
      port_id:
        type: string
      network_id:
        type: string
      mac_address:
        type: string
      addresses:
        type: list
        entry_schema:
          type: string
  tosca.datatypes.network.PortDef:
    derived_from: integer
    constraints:
      - in_range: [ 1, 65535 ]
  tosca.datatypes.network.PortSpec:
    derived_from: tosca.datatypes.Root
    properties:
      protocol:
        type: string
        required: true
        default: tcp
        constraints:
          - valid_values: [ udp, tcp, igmp ]
      target:
        type: PortDef
      target_range:
        type: range
        constraints:
          - in_range: [ 1, 65535 ]
      source:
        type: PortDef
      source_range:
        type: range
        constraints:
          - in_range: [ 1, 65535 ]
*/

/*******************************************************************************
 * Artifact Types.
 *******************************************************************************/
/*
  tosca.artifacts.Root:
    description: The TOSCA Artifact Type all other TOSCA Artifact Types derive from
  tosca.artifacts.File:
    derived_from: tosca.artifacts.Root
    description: >
      This artifact type is used when an artifact definition needs to have its associated file simply treated as a file and no special handling/handlers are invoked.
  tosca.artifacts.Deployment:
    derived_from: tosca.artifacts.Root
    description: TOSCA base type for deployment artifacts
  tosca.artifacts.Deployment.Image:
    derived_from: tosca.artifacts.Deployment
    description: >
      This artifact type represents a parent type for any “image” which is an opaque packaging of a TOSCA Node’s deployment (whether real or virtual)
      whose contents are typically already installed and pre-configured (i.e., “stateful”) and prepared to be run on a known target container.
  tosca.artifacts.Deployment.Image.VM:
    derived_from: tosca.artifacts.Deployment.Image
    description: >
      This artifact represents the parent type for all Virtual Machine (VM) image and container formatted deployment artifacts.
      These images contain a stateful capture of a machine (e.g., server) including operating system and installed software along with any
      configurations and can be run on another machine using a hypervisor which virtualizes typical server (i.e., hardware) resources.
      Virtual Machine (VM) Image
  tosca.artifacts.Implementation:
    derived_from: tosca.artifacts.Root
    description: TOSCA base type for implementation artifacts
  tosca.artifacts.Implementation.Bash:
    derived_from: tosca.artifacts.Implementation
    description: Script artifact for the Unix Bash shell
    mime_type: application/x-sh
    file_ext: [ sh ]
  tosca.artifacts.Implementation.Python:
    derived_from: tosca.artifacts.Implementation
    description: Artifact for the interpreted Python language
    mime_type: application/x-python
    file_ext: [ py ]
*/

/*******************************************************************************
 * Capability Types.
 *******************************************************************************/
/*
  tosca.capabilities.Root:
    description: This is the default (root) TOSCA Capability Type definition that all other TOSCA Capability Types derive from.
*/
sig Capability_Root extends Capability {}

/*
  tosca.capabilities.Node:
    derived_from: tosca.capabilities.Root
    description: The Node capability indicates the base capabilities of a TOSCA Node Type.
*/
sig Capability_Node extends Capability_Root {}

/*
  tosca.capabilities.Container:
    derived_from: tosca.capabilities.Root
    description: >
      The Container capability, when included on a Node Type or Template definition, indicates that the node can act as a container for (or a host for)
      one or more other declared Node Types.
    properties:
      num_cpus:
        type: integer
        description: Number of (actual or virtual) CPUs associated with the Compute node.
        required: false
        constraints:
          - greater_or_equal: 1
      cpu_frequency:
        type: scalar-unit.frequency
        description: >
          Specifies the operating frequency of CPU's core.  This property expresses the expected frequency of one (1) CPU as provided by the property
          “num_cpus”.
        required: false
        constraints:
          - greater_or_equal: 0.1 GHz
      disk_size:
        type: scalar-unit.size
        description: Size of the local disk available to applications running on the Compute node (default unit is MB).
        required: false
        constraints:
          - greater_or_equal: 0 MB
      mem_size:
        type: scalar-unit.size
        description: Size of memory available to applications running on the Compute node (default unit is MB).
        required: false
        constraints:
          - greater_or_equal: 0 MB
*/
sig Container extends Capability_Root {}

/*
  tosca.capabilities.Endpoint:
    derived_from: tosca.capabilities.Root
    description: >
      This is the default TOSCA type that should be used or extended to define a network endpoint capability.
      This includes the information to express a basic endpoint with a single port or a complex endpoint with multiple ports.
      By default the Endpoint is assumed to represent an address on a private network unless otherwise specified.
    properties:
      protocol:
        type: string
        description: >
          The name of the protocol (i.e., the protocol prefix) that the endpoint accepts (any OSI Layer 4-7 protocols)
          Examples: http, https, ftp, tcp, udp, etc.
        default: tcp
      port:
        type: tosca.datatypes.network.PortDef
        description: The optional port of the endpoint.
        required: false
        constraints:
          - in_range: [ 1, 65535 ]
      secure:
        type: boolean
        description: Requests for the endpoint to be secure and use credentials supplied on the ConnectsTo relationship.
        required: false
        default: false
      url_path:
        type: string
        description: The optional URL path of the endpoint’s address if applicable for the protocol.
        required: false
      port_name:
        type: string
        description: The optional name (or ID) of the network port this endpoint should be bound to.
        required: false
      network_name:
        type: string
        description: >
          The optional name (or ID) of the network this endpoint should be bound to.
          network_name: PRIVATE | PUBLIC |<network_name> | <network_id>
        required: false
        default: PRIVATE
      initiator:
        type: string
        description: The optional indicator of the direction of the connection.
        required: false
        default: source
        constraints:
          - valid_values: [ source, target, peer ]
      ports:
        type: map
        description: The optional map of ports the Endpoint supports (if more than one).
        required: false
        constraints:
          - min_length: 1
        entry_schema:
          type: tosca.datatypes.network.PortSpec
    attributes:
      ip_address:
        type: string
        description: This is the IP address as propagated up by the associated node’s host (Compute) container.
*/
sig Endpoint extends Capability_Root {}

/*
  tosca.capabilities.Endpoint.Public:
    derived_from: tosca.capabilities.Endpoint
    description: >
      This capability represents a public endpoint which is accessible to the general internet (and its public IP address ranges).
      This public endpoint capability also can be used to create a floating (IP) address that the underlying network assigns from a pool allocated from
      the application’s underlying public network.  This floating address is managed by the underlying network such that can be routed an application’s
      private address and remains reliable to internet clients.
    properties:
      # Change the default network_name to use the first public network found
      network_name:
        type: string
        default: PUBLIC
        constraints:
          - equal: PUBLIC
      floating:
        description: >
          Indicates that the public address should be allocated from a pool of floating IPs that are associated with the network.
        type: boolean
        default: false
        status: experimental
      dns_name:
        description: The optional name to register with DNS
        type: string
        required: false
        status: experimental
*/
sig Endpoint_Public extends Endpoint {}

/*
  tosca.capabilities.Endpoint.Admin:
    derived_from: tosca.capabilities.Endpoint
    description: This is the default TOSCA type that should be used or extended to define a specialized administrator endpoint capability.
    properties:
      # Change Endpoint secure indicator to true from its default of false
      secure:
        type: boolean
        default: true
        constraints:
          - equal: true
*/
sig Endpoint_Admin extends Endpoint {}

/*
  tosca.capabilities.Endpoint.Database:
    derived_from: tosca.capabilities.Endpoint
    description: This is the default TOSCA type that should be used or extended to define a specialized database endpoint capability.
*/
sig Endpoint_Database extends Endpoint {}

/*
  tosca.capabilities.Attachment:
    derived_from: tosca.capabilities.Root
    description: >
      This is the default TOSCA type that should be used or extended to define an attachment capability of a (logical) infrastructure device node
      (e.g., BlockStorage node).
*/
sig Attachment extends Capability_Root {}

/*
  tosca.capabilities.OperatingSystem:
    derived_from: tosca.capabilities.Root
    description: This is the default TOSCA type that should be used to express an Operating System capability for a node.
    properties:
      architecture:
        type: string
        description: >
          The Operating System (OS) architecture.
          Examples of valid values include:
          x86_32, x86_64, etc.
        required: false
      type:
        type: string
        description: >
          The Operating System (OS) type.
          Examples of valid values include:
          linux, aix, mac, windows, etc.
        required: false
      distribution:
        type: string
        description: >
          The Operating System (OS) distribution.
          Examples of valid values for an “type” of “Linux” would include:  debian, fedora, rhel and ubuntu.
        required: false
      version:
        type: version
        description: >
          The Operating System version.
        required: false
*/
sig OperatingSystem extends Capability_Root {}

/*
  tosca.capabilities.Scalable:
    derived_from: tosca.capabilities.Root
    description: This is the default TOSCA type that should be used to express a scalability capability for a node.
    properties:
      min_instances:
        type: integer
        description: >
          This property is used to indicate the minimum number of instances that should be created for the associated TOSCA Node Template by a
          TOSCA orchestrator.
        default: 1
      max_instances:
        type: integer
        description: >
          This property is used to indicate the maximum number of instances that should be created for the associated TOSCA Node Template by a
          TOSCA orchestrator.
        default: 1
      default_instances:
        type: integer
        required: false
        description: >
          An optional property that indicates the requested default number of instances that should be the starting number of instances a TOSCA orchestrator
          should attempt to allocate.
          Note: The value for this property MUST be in the range between the values set for ‘min_instances’ and ‘max_instances’ properties.
        default: 1
*/
sig Scalable extends Capability_Root {}

/*
  tosca.capabilities.network.Bindable:
    derived_from: tosca.capabilities.Node
*/
sig Bindable extends Capability_Node {}

/*
  tosca.capabilities.network.Linkable:
    derived_from: tosca.capabilities.Node
*/
sig Linkable extends Capability_Node {}

/*******************************************************************************
 * Interface Types.
 *******************************************************************************/
/*
  tosca.interfaces.Root:
    description: The TOSCA root Interface Type all other TOSCA base Interface Types derive from.

  tosca.interfaces.node.lifecycle.Standard:
    derived_from: tosca.interfaces.Root
    create:
      description: Standard lifecycle create operation.
    configure:
      description: Standard lifecycle configure operation.
    start:
      description: Standard lifecycle start operation.
    stop:
      description: Standard lifecycle stop operation.
    delete:
      description: Standard lifecycle delete operation.

  tosca.interfaces.relationship.Configure:
    derived_from: tosca.interfaces.Root
    pre_configure_source:
      description: Operation to pre-configure the source endpoint.
    pre_configure_target:
      description: Operation to pre-configure the target endpoint.
    post_configure_source:
      description: Operation to post-configure the source endpoint.
    post_configure_target:
      description: Operation to post-configure the target endpoint.
    add_target:
      description: Operation to notify the source node of a target node being added via a relationship.
    add_source:
      description: Operation to notify the target node of a source node which is now available via a relationship.
      description:
    target_changed:
      description: Operation to notify source some property or attribute of the target changed
    remove_target:
      description: Operation to remove a target node.
*/

/*******************************************************************************
 * Relationship Types.
 *******************************************************************************/
/*
  tosca.relationships.Root:
    description: The TOSCA root Relationship Type all other TOSCA base Relationship Types derive from
    attributes:
      tosca_id:
        type: string
        description: A unique identifier of the realized instance of a Relationship Template that derives from any TOSCA normative type.
      tosca_name:
        type: string
        description: >
          This attribute reflects the name of the Relationship Template as defined in the TOSCA service template.
          This name is not unique to the realized instance model of corresponding deployed application as each template in the model can result in one or
          more instances (e.g., scaled) when orchestrated to a provider environment.
      state:
        type: string
        description: The state of the relationship instance.
        default: initial
    interfaces:
      Configure:
        type: tosca.interfaces.relationship.Configure
*/
sig Relationship_Root extends Relationship {}

/*
  tosca.relationships.DependsOn:
    derived_from: tosca.relationships.Root
    description: This type represents a general dependency relationship between two nodes.
    valid_target_types: [ tosca.capabilities.Node ]
*/
sig DependsOn extends Relationship_Root {
} {
  target in Capability_Node
}

/*
  tosca.relationships.HostedOn:
    derived_from: tosca.relationships.Root
    description: This type represents a hosting relationship between two nodes.
    valid_target_types: [ tosca.capabilities.Container ]
*/
sig HostedOn extends Relationship_Root {
} {
  target in Container
}

/*
  tosca.relationships.ConnectsTo:
    derived_from: tosca.relationships.Root
    description: This type represents a network connection relationship between two nodes.
    valid_target_types: [ tosca.capabilities.Endpoint ]
    properties:
      credential:
        type: tosca.datatypes.Credential
        description: The security credential to use to present to the target endpoint to for either authentication or authorization purposes.
        required: false
*/
sig ConnectsTo extends Relationship_Root {
} {
  target in Endpoint
}

/*
  tosca.relationships.AttachTo:                                  // BUG -> OASIS: Is AttachesTo, see page 156
    derived_from: tosca.relationships.Root
    valid_target_types: [ tosca.capabilities.Attachment ]
    properties:
      location:
        type: string
        constraints:
          - min_length: 1
      device:
        type: string
        required: false
*/
sig AttachesTo extends Relationship_Root {
} {
  target in Attachment
}

/*
  tosca.relationships.RoutesTo:
    derived_from: tosca.relationships.ConnectsTo
    description: This type represents an intentional network routing between two Endpoints in different networks.
// OASIS: Following seems useless as ConnectsTo already restricts valid target types to Endpoint.
    valid_target_types: [ tosca.capabilities.Endpoint ]
*/
sig RoutesTo extends ConnectsTo {
} {
// TO CHECK: Following seems useless as ConnectsTo already restricts valid target types to Endpoint.
  target in Endpoint
}

/*
  tosca.relationships.network.LinksTo:
    derived_from: tosca.relationships.DependsOn
    valid_target_types: [ tosca.capabilities.network.Linkable ]
*/
sig LinksTo extends DependsOn {
} {
  target in Linkable
}

/*
  tosca.relationships.network.BindsTo:
    derived_from: tosca.relationships.DependsOn
    valid_target_types: [ tosca.capabilities.network.Bindable ]
*/
sig BindsTo extends DependsOn {
} {
  target in Bindable
}

/*******************************************************************************
 * Node Types.
 *******************************************************************************/
/*
  tosca.nodes.Root:
    description: >
      This is the default (root) TOSCA Node Type that all other TOSCA nodes should extends.
      This allows all TOSCA nodes to have a consistent set of features for modeling and management
      (e.g, consistent definitions for requirements, capabilities, and lifecycle interfaces).
    attributes:
      tosca_id:
        type: string
        description: A unique identifier of the realized instance of a Node Template that derives from any TOSCA normative type.
      tosca_name:
        type: string
        description: >
          This attribute reflects the name of the Node Template as defined in the TOSCA service template.
          This name is not unique to the realized instance model of corresponding deployed application as each template in the model can result in one
          or more instances (e.g., scaled) when orchestrated to a provider environment.
      state:
        type: string
        description: The state of the node instance. See section “Node States” for allowed values.
        default: initial
    capabilities:
      feature:
        type: tosca.capabilities.Node
    requirements:
      - dependency:
          capability: tosca.capabilities.Node                         // OASIS: Is it useless as already defined in DependsOn?
          node: tosca.nodes.Root
          relationship: tosca.relationships.DependsOn
          occurrences: [ 0, UNBOUNDED ]
    interfaces:
      Standard:
        type: tosca.interfaces.node.lifecycle.Standard
*/
sig Node_Root extends Node
{
  feature : one Capability_Node,
  /* - dependency: occurrences: [ 0, UNBOUNDED ] */
  dependency: set Requirement
} {
  feature in capabilities
  dependency in requirements
  /* - dependency: capability: tosca.capabilities.Node */
  dependency.capability[Capability_Node] // TO CHECK: This constraint is useless as already defined in DependsOn.
  /* - dependency:  node: tosca.nodes.Root */
  dependency.node[Node_Root]
  /* - dependency: relationship: tosca.relationships.DependsOn */
  dependency.relationship in DependsOn
}

/*
  tosca.nodes.Compute:
    derived_from: tosca.nodes.Root
    description: >
      The TOSCA Compute node represents one or more real or virtual processors of software applications or services along with other essential local resources.
      Collectively, the resources the compute node represents can logically be viewed as a (real or virtual) “server”.
    attributes:
      private_address:
        type: string
        description: The primary private IP address assigned by the cloud provider that applications may use to access the Compute node.
        required: false
      public_address:
        type: string
        description: The primary public IP address assigned by the cloud provider that applications may use to access the Compute node.
        required: false
      networks:
        type: map
        entry_schema:
          type: tosca.datatypes.network.NetworkInfo
        required: false
      ports:
        type: map
        entry_schema:
          type: tosca.datatypes.network.PortInfo
        required: false
    requirements:
      - local_storage:
          capability: tosca.capabilities.Attachment                    // OASIS: Is it useless as already defined in AttachesTo?
          node: tosca.nodes.BlockStorage
          relationship: tosca.relationships.AttachesTo
          occurrences: [0, UNBOUNDED]
    capabilities:
      host:
        type: tosca.capabilities.Container
        valid_source_types: [tosca.nodes.SoftwareComponent]
      os:
        type: tosca.capabilities.OperatingSystem
      endpoint:
        type: tosca.capabilities.Endpoint.Admin
      scalable:
        type: tosca.capabilities.Scalable
      binding:
        type: tosca.capabilities.network.Bindable
*/
sig Compute extends Node_Root
{
  /* - local_storage: occurrences: [ 0, UNBOUNDED ] */
  local_storage: set Requirement,
  host: one Container,
  os: one OperatingSystem,
  endpoint: one Endpoint_Admin,
  scalable: one Scalable,
  binding: one Bindable
} {
  local_storage in requirements
  /* - local_storage: capability: tosca.capabilities.Attachment */

  local_storage.capability[Attachment] // TO CHECK: This constraint is useless as already defined in AttachesTo.
  /* - local_storage: node: tosca.nodes.BlockStorage */
  local_storage.node[BlockStorage]
  /* - local_storage: relationship: tosca.relationships.AttachesTo */
  local_storage.relationship in AttachesTo

  host in capabilities
  // host:  valid_source_types: [tosca.nodes.SoftwareComponent]
  host.valid_source_types[SoftwareComponent]
  os in capabilities
  endpoint in capabilities
  scalable in capabilities
  binding in capabilities
}

/*
  tosca.nodes.SoftwareComponent:
    derived_from: tosca.nodes.Root
    description: The TOSCA SoftwareComponent node represents a generic software component that can be managed and run by a TOSCA Compute Node Type.
    properties:
      # domain-specific software component version
      component_version:
        type: version
        description: The optional software component’s version.
        required: false
      admin_credential:
        type: tosca.datatypes.Credential
        description: The optional credential that can be used to authenticate to the software component.
        required: false
    requirements:
      - host:
          capability: tosca.capabilities.Container                         // OASIS: Is it useless as already defined in HostedOn?
          node: tosca.nodes.Compute
          relationship: tosca.relationships.HostedOn
*/
sig SoftwareComponent extends Node_Root {
  host: one Requirement
} {
  host in requirements

  /* - host: capability: tosca.capabilities.Container */
  host.capability[Container]                          // TO CHECK: This constraint is useless as already defined in HostedOn.
  /* - host: node: tosca.nodes.Compute */
  host.node[Compute]
  /* - host: relationship: tosca.relationships.HostedOn */
  host.relationship in HostedOn
}

/*
  tosca.nodes.WebServer:
    derived_from: tosca.nodes.SoftwareComponent
    description: >
      This TOSCA WebServer Node Type represents an abstract software component or service that is capable of hosting and providing management operations
      for one or more WebApplication nodes.
    capabilities:
      # Private, layer 4 endpoints
      data_endpoint: tosca.capabilities.Endpoint
      admin_endpoint: tosca.capabilities.Endpoint.Admin
      host:
        type: tosca.capabilities.Container
        valid_source_types: [ tosca.nodes.WebApplication ]
*/
sig WebServer extends SoftwareComponent {
  data_endpoint: one Endpoint,
  admin_endpoint: one Endpoint_Admin,
  // host: one Container // host is already a field of sig SofwareComponent.
  chost: one Container
} {
  data_endpoint in capabilities
  admin_endpoint in capabilities
  chost in capabilities
  /* host: valid_source_types: [ tosca.nodes.WebApplication ] */
  chost.valid_source_types[WebApplication]
}

/*
  tosca.nodes.WebApplication:
    derived_from: tosca.nodes.Root
    description: >
      The TOSCA WebApplication node represents a software application that can be managed and run by a TOSCA WebServer node.
      Specific types of web applications such as Java, etc. could be derived from this type.
    properties:
      context_root:
        type: string
        required: false
        description: The web application’s context root which designates the application’s URL path within the web server it is hosted on.
    capabilities:
      app_endpoint:
        type: tosca.capabilities.Endpoint
    requirements:
      - host:
          capability: tosca.capabilities.Container                         // OASIS: Is it useless as already defined in HostedOn?
          node: tosca.nodes.WebServer
          relationship: tosca.relationships.HostedOn
*/
sig WebApplication extends Node_Root {
  app_endpoint: one Endpoint,
  host: one Requirement
} {
  app_endpoint in capabilities
  host in requirements
  /* - host: capability: tosca.capabilities.Container */
  host.capability[Container]                                             // TO CHECK: This constraint is useless as already defined in HostedOn.
  /* - host: node: tosca.nodes.WebServer */
  host.node[WebServer]
  /* - host: relationship: tosca.relationships.HostedOn */
  host.relationship in HostedOn
}

/*
  tosca.nodes.DBMS:
    derived_from: tosca.nodes.SoftwareComponent
    description: "The TOSCA DBMS node represents a typical relational, SQL Database Management System software component or service."
    tags:
      icon: /images/relational_db.png
    properties:
      root_password:
        type: string
        required: false
        description: the optional root password for the DBMS service
      port:
        type: integer
        required: false
        description: the port the DBMS service will listen to for data and requests
    capabilities:
      host:
        type: tosca.capabilities.Container
        valid_source_types: [ tosca.nodes.Database ]
*/
sig DBMS extends SoftwareComponent {
  // host: one Container // host is already a field of sig SofwareComponent.
  chost: one Container
} {
  chost in capabilities
  /* host: valid_source_types: [ tosca.nodes.Database ] */
  chost.valid_source_types[Database]
}

/*
  tosca.nodes.Database:
    derived_from: tosca.nodes.Root
    description: The TOSCA Database node represents a logical database that can be managed and hosted by a TOSCA DBMS node.
    properties:
      name:
        type: string
        description: the logical name of the database
        required: true
      port:
        type: integer
        description: the port the underlying database service will listen to for data
        required: false
      user:
        type: string
        description: the optional user account name for DB administration
        required: false
      password:
        type: string
        description: the optional password for the DB user account
        required: false
    requirements:
      - host: tosca.capabilities.Container                       // OASIS: Is it useless as already defined in HostedOn?
        # node: tosca.nodes.DBMS                                   // OASIS: Why is it commented?
        relationship: tosca.relationships.HostedOn
    capabilities:
      database_endpoint:
        type: tosca.capabilities.Endpoint.Database
*/
sig Database extends Node_Root {
  host: one Requirement,
  database_endpoint: one Endpoint_Database
} {
  host in requirements
  /* - host: tosca.capabilities.Container */
  host.capability[Container]                      // TO CHECK: This constraint is useless as already defined in HostedOn.
  /* - host:  # node: tosca.nodes.DBMS */
  host.node[DBMS]
  /* - host:  relationship: tosca.relationships.HostedOn */
  host.relationship in HostedOn

  database_endpoint in capabilities
}

/*
  tosca.nodes.ObjectStorage:
    derived_from: tosca.nodes.Root
    properties:
      name:
        type: string
        required: true
      size:
        type: scalar-unit.size
        constraints:
          - greater_or_equal: 0 GB
        required: false
      maxsize:
        type: scalar-unit.size
        constraints:
          - greater_or_equal: 0 GB
        required: false
    capabilities:
      storage_endpoint:
        type: tosca.capabilities.Endpoint
*/
sig ObjectStorage extends Node_Root {
  storage_endpoint: one Endpoint
} {
  storage_endpoint in capabilities
}

/*
  tosca.nodes.BlockStorage:
    abstract: true
    derived_from: tosca.nodes.Root
    description: >
      The TOSCA BlockStorage node currently represents a server-local block storage device (i.e., not shared)
      offering evenly sized blocks of data from which raw storage volumes can be created.
    tags:
      icon: /images/volume.png
    properties:
      size:
        type: scalar-unit.size
        description: >
          The requested storage size (default unit is MB).
          Note:
          - Required when an existing volume (i.e., volume_id) is not available.
          - If volume_id is provided, size is ignored.  Resize of existing volumes is not considered at this time.
        constraints:
          - greater_or_equal: 1 MB
      volume_id:
        type: string
        description: ID of an existing volume (that is in the accessible scope of the requesting application).
        required: false
      snapshot_id:
        type: string
        description: Some identifier that represents an existing snapshot that should be used when creating the block storage (volume).
        required: false
    capabilities:
      attachment:
        type: tosca.capabilities.Attachment
*/
abstract sig BlockStorage extends Node_Root {
  attachment: one Attachment
} {
  attachment in capabilities
}

/*
  tosca.nodes.Container.Runtime:
    derived_from: tosca.nodes.SoftwareComponent
    description: >
      The TOSCA Container Runtime node represents operating system-level virtualization technology used to run multiple application services on a
      single Compute host.
    capabilities:
      host:
        type: tosca.capabilities.Container
      scalable:
        type: tosca.capabilities.Scalable
*/
sig Container_Runtime extends SoftwareComponent {
  // host: one Container // host is already a field of sig SofwareComponent.
  chost: one Container,
  scalable: one Scalable
} {
  chost in capabilities
  scalable in capabilities
}

/*
  tosca.nodes.Container.Application:
    derived_from: tosca.nodes.Root
    description: >
      The TOSCA Container Application node represents an application that requires Container-level virtualization technology.
    requirements:
      - host:
          capability: tosca.capabilities.Container             // OASIS: Is it useless as already defined in HostedOn?
          node: tosca.nodes.Container                             // BUG -> OASIS: Container.Runtime instead of Container? page 173
          relationship: tosca.relationships.HostedOn
*/
sig Container_Application extends Node_Root {
  host: one Requirement
} {
  host in requirements
  /* - host: capability: tosca.capabilities.Container */
  host.capability[Container]                                    // TO CHECK: It is useless as already defined in HostedOn.
  /* - host: node: tosca.nodes.Container */
  host.node[Container_Runtime]                              // Correction: Container_Runtime instead of Container.
 /* - host: relationship: tosca.relationships.HostedOn */
  host.relationship in HostedOn
}

/*
  tosca.nodes.LoadBalancer:
    derived_from: tosca.nodes.Root
    description: >
      The TOSCA Load Balancer node represents logical function that be used in conjunction with a Floating Address to distribute an application’s
      traffic (load) across a number of instances of the application (e.g., for a clustered or scaled application).
    properties:
      algorithm:
        type: string
        required: false
        status: experimental
    capabilities:
      client:
        type: tosca.capabilities.Endpoint.Public
        occurrences: [0, UNBOUNDED]
        description: the Floating (IP) client’s on the public network can connect to
    requirements:
      - application:
          capability: tosca.capabilities.Endpoint                          // OASIS: Is it useless as already defined in RoutesTo?
          relationship: tosca.relationships.RoutesTo
          occurrences: [0, UNBOUNDED]
          description: Connection to one or more load balanced applications
*/
sig LoadBalancer extends Node_Root {
  client: set Endpoint_Public,
  application: set Requirement
} {
  client in capabilities
  application in requirements
  /* - application: capability: tosca.capabilities.Endpoint */
  application.capability[Endpoint]                                    // TO CHECK: This constraint is useless as already defined in RoutesTo.
  /* - application: relationship: tosca.relationships.RoutesTo */
  application.relationship in RoutesTo
}

/*
  tosca.nodes.network.Network:
    derived_from: tosca.nodes.Root
    properties:
      ip_version:
        type: integer
        required: false
        default: 4
        constraints:
          - valid_values: [ 4, 6 ]
      cidr:
        type: string
        required: false
      start_ip:
        type: string
        required: false
      end_ip:
        type: string
        required: false
      gateway_ip:
        type: string
        required: false
      network_name:
        type: string
        required: false
      network_id:
        type: string
        required: false
      segmentation_id:
        type: string
        required: false
      network_type:
        type: string
        required: false
      physical_network:
        type: string
        required: false
    capabilities:
      link:
        type: tosca.capabilities.network.Linkable
*/
sig Network extends Node_Root {
  link: one Linkable
} {
  link in capabilities
}

/*
  tosca.nodes.network.Port:
    derived_from: tosca.nodes.Root
    properties:
      ip_address:
        type: string
        required: false
      order:
        type: integer
        required: true
        default: 0
        constraints:
          - greater_or_equal: 0
      is_default:
        type: boolean
        required: false
        default: false
      ip_range_start:
        type: string
        required: false
      ip_range_end:
        type: string
        required: false
      requirements:
        - link:
           capability: tosca.capabilities.network.Linkable
          relationship: tosca.relationships.network.LinksTo
       - binding:
          capability: tosca.capabilities.network.Bindable
          relationship: tosca.relationships.network.BindsTo
*/
sig Port extends Node_Root {
  link: one Requirement,
  binding: one Requirement
} {
  link in requirements
  /* - link: capability: tosca.capabilities.network.Linkable */
  link.capability[Linkable]                                        // TO CHECK: This constraint is useless as already defined in LinksTo.
  /* - link: relationship: tosca.relationships.network.LinksTo */
  link.relationship in LinksTo

  binding in requirements
  /* - binding: capability: tosca.capabilities.network.Bindable */
  binding.capability[Bindable]                                  // TO CHECK: This constraint is useless as already defined in BindsTo.
  /* - binding: relationship: tosca.relationships.network.BindsTo */
  binding.relationship in BindsTo
}

/*******************************************************************************
 * Group Types.
 *******************************************************************************/
/*
 group_types:
  tosca.groups.Root:
    description: The TOSCA Group Type all other TOSCA Group Types derive from
    interfaces:
      Standard:
        type: tosca.interfaces.node.lifecycle.Standard
*/

/*******************************************************************************
 * Policy Types.
 *******************************************************************************/
/*
  tosca.policies.Root:
    description: The TOSCA Policy Type all other TOSCA Policy Types derive from
  tosca.policies.Placement:
    derived_from: tosca.policies.Root
    description: The TOSCA Policy Type definition that is used to govern placement of TOSCA nodes or groups of nodes.
  tosca.policies.Scaling:
    derived_from: tosca.policies.Root
    description: The TOSCA Policy Type definition that is used to govern scaling of TOSCA nodes or groups of nodes.
  tosca.policies.Update:
    derived_from: tosca.policies.Root
    description: The TOSCA Policy Type definition that is used to govern update of TOSCA nodes or groups of nodes.
  tosca.policies.Performance:
    derived_from: tosca.policies.Root
description: The TOSCA Policy Type definition that is used to declare performance requirements for TOSCA nodes or groups of nodes.
*/

/*******************************************************************************
 * Consistency Property.
 *******************************************************************************/

/** Consistency means that there exists some TOSCA topology. */
run Model {} for 10

run OneTopologyWithTwoNodeOneRelationship {
  Node in Topology.nodes
  Relationship in Topology.relationships
} for 10 but exactly 1 Topology, exactly 2 Node, exactly 1 Relationship

/** TOSCA Simple Profile YAML v1.0 cs01 page 12 */
run TOSCA_Example_2_1 {
  Topology.nodes = Compute
} for 10 but exactly 1 Topology, exactly 1 Compute, exactly 5 Capability

/** TOSCA Simple Profile YAML v1.0 cs01 page 16 */
run TOSCA_Example_2_2 {
  Topology.nodes = Compute + DBMS
  Topology.relationships = HostedOn
} for 20 but exactly 1 Topology, exactly 1 Compute, exactly 1 DBMS, exactly 1 HostedOn, exactly 7 Capability

/** TOSCA Simple Profile YAML v1.0 cs01 page 19 */
run TOSCA_Example_2_4 {
  Topology.nodes = Compute + DBMS + Database
  Topology.relationships = HostedOn
} for 20 but exactly 1 Topology, exactly 1 Compute, exactly 1 DBMS, exactly 1 Database, exactly 2 HostedOn, exactly 9 Capability

/** TOSCA Simple Profile YAML v1.0 cs01 page 19 */
run TOSCA_Example_2_5 {
  Topology.nodes = Compute + DBMS + Database + WebServer + WebApplication
  Topology.relationships = HostedOn
} for 40 but exactly 1 Topology, exactly 2 Compute, exactly 1 DBMS, exactly 1 Database, exactly 1 WebServer, exactly 1 WebApplication, exactly 4 HostedOn, exactly 20 Capability, exactly 24 Role

/** TOSCA Simple Profile YAML v1.0 cs01 page 178 */
run TOSCA_Example_7_2 {
  Topology.nodes = Compute + Network + Port
  Topology.relationships = LinksTo + BindsTo
} for 20 but exactly 1 Topology, exactly 1 Compute, exactly 1 Port, exactly 1 Network, exactly 1 BindsTo, exactly 1 LinksTo, exactly 7 Capability
