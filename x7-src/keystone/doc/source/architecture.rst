..
      Copyright 2011 X7, LLC
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Keystone Architecture
=====================

Keystone has two major components: Authentication and a Service Catalog.

Authentication
--------------

In providing a token-based authentication service for X7, keystone
has several major concepts:

Tenant
    A grouping used in X7 to contain relevant X7 services. A
    tenant maps to a Engine "project-id", and in object storage, a tenant can
    have multiple containers. Depending on the installation, a tenant can
    represent a customer, account, organization, or project.

User
    Represents an individual within X7 for the purposes of
    authenticating them to X7 services. Users have credentials, and may
    be assigned to one or more tenants. When authenticated, a token is
    provided that is specific to a single tenant.

Credentials
    Password or other information that uniquely identifies a User to Keystone
    for the purposes of providing a token.

Token
    A token is an arbitrary bit of text that is used to share authentication
    with other X7 services so that Keystone can provide a central
    location for authenticating users for access to X7 services. A
    token may be "scoped" or "unscoped". A scoped token represents a user
    authenticated to a Tenant, where an unscoped token represents just the
    user.

    Tokens are valid for a limited amount of time and may be revoked at any
    time.

Role
    A role is a set of permissions to access and use specific operations for
    a given user when applied to a tenant. Roles are logical groupings of
    those permissions to enable common permissions to be easily grouped and
    bound to users associated with a given tenant.

Service Catalog
---------------

Keystone also provides a list of REST API endpoints as a definitive list for
an X7 installation. Key concepts include:

Service
    An X7 service such as engine, chase, tank, or keystone. A service
    may have one of more endpoints through which users can interact with
    X7 services and resources.

Endpoint
    A network accessible address (typically a URL) that represents the API
    interface to an X7 service. Endpoints may also be grouped into
    templates which represent a group of consumable X7 services
    available across regions.

Template
    A collection of endpoints representing a set of consumable X7
    service endpoints.

Components of Keystone
----------------------

Keystone includes a command-line interface which interacts with the Keystone
API for administrating keystone and related services.

* keystone - runs both keystone-admin and keystone-service
* keystone-admin - the administrative API for manipulating keystone
* keystone-service - the user oriented API for authentication
* keystone-manage - the command line interface to manipulate keystone

Keystone also includes WSGI middelware to provide authentication support
for Engine and Chase.

Keystone uses a built-in SQLite datastore - and may use an external LDAP
service to authenticate users instead of using stored credentials.
