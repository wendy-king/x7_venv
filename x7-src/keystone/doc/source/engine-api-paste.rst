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

engine-api-paste example
======================
::

    #######
    # EC2 #
    #######

    [composite:ec2]
    use = egg:Paste#urlmap
    /: ec2versions
    /services/Cloud: ec2cloud
    /services/Admin: ec2admin
    /latest: ec2metadata
    /2007-01-19: ec2metadata
    /2007-03-01: ec2metadata
    /2007-08-29: ec2metadata
    /2007-10-10: ec2metadata
    /2007-12-15: ec2metadata
    /2008-02-01: ec2metadata
    /2008-09-01: ec2metadata
    /2009-04-04: ec2metadata
    /1.0: ec2metadata

    [pipeline:ec2cloud]
    pipeline = logrequest totoken authtoken keystonecontext cloudrequest authorizer ec2executor

    [pipeline:ec2admin]
    pipeline = logrequest totoken authtoken keystonecontext adminrequest authorizer ec2executor

    [pipeline:ec2metadata]
    pipeline = logrequest ec2md

    [pipeline:ec2versions]
    pipeline = logrequest ec2ver

    [filter:logrequest]
    paste.filter_factory = engine.api.ec2:RequestLogging.factory

    [filter:ec2lockout]
    paste.filter_factory = engine.api.ec2:Lockout.factory

    [filter:totoken]
    paste.filter_factory = keystone.middleware.ec2_token:EC2Token.factory

    [filter:ec2noauth]
    paste.filter_factory = engine.api.ec2:NoAuth.factory

    [filter:authenticate]
    paste.filter_factory = engine.api.ec2:Authenticate.factory

    [filter:cloudrequest]
    controller = engine.api.ec2.cloud.CloudController
    paste.filter_factory = engine.api.ec2:Requestify.factory

    [filter:adminrequest]
    controller = engine.api.ec2.admin.AdminController
    paste.filter_factory = engine.api.ec2:Requestify.factory

    [filter:authorizer]
    paste.filter_factory = engine.api.ec2:Authorizer.factory

    [app:ec2executor]
    paste.app_factory = engine.api.ec2:Executor.factory

    [app:ec2ver]
    paste.app_factory = engine.api.ec2:Versions.factory

    [app:ec2md]
    paste.app_factory = engine.api.ec2.metadatarequesthandler:MetadataRequestHandler.factory

    #############
    # X7 #
    #############

    [composite:osapi]
    use = egg:Paste#urlmap
    /: osversions
    /v1.0: x7api10
    /v1.1: x7api11

    [pipeline:x7api10]
    pipeline = faultwrap authtoken keystonecontext ratelimit osapiapp10

    [pipeline:x7api11]
    pipeline = faultwrap authtoken keystonecontext ratelimit extensions osapiapp11

    [filter:faultwrap]
    paste.filter_factory = engine.api.x7:FaultWrapper.factory

    [filter:auth]
    paste.filter_factory = engine.api.x7.auth:AuthMiddleware.factory

    [filter:noauth]
    paste.filter_factory = engine.api.x7.auth:NoAuthMiddleware.factory

    [filter:ratelimit]
    paste.filter_factory = engine.api.x7.limits:RateLimitingMiddleware.factory

    [filter:extensions]
    paste.filter_factory = engine.api.x7.extensions:ExtensionMiddleware.factory

    [app:osapiapp10]
    paste.app_factory = engine.api.x7:APIRouterV10.factory

    [app:osapiapp11]
    paste.app_factory = engine.api.x7:APIRouterV11.factory

    [pipeline:osversions]
    pipeline = faultwrap osversionapp

    [app:osversionapp]
    paste.app_factory = engine.api.x7.versions:Versions.factory

    ##########
    # Shared #
    ##########

    [filter:keystonecontext]
    paste.filter_factory = keystone.middleware.engine_keystone_context:EngineKeystoneContext.factory

    [filter:authtoken]
    paste.filter_factory = keystone.middleware.auth_token:filter_factory
    service_protocol = http
    service_host = 127.0.0.1
    service_port = 5000
    auth_host = 127.0.0.1
    auth_port = 35357
    auth_protocol = http
    auth_uri = http://127.0.0.1:5000/
    admin_token = 999888777666

