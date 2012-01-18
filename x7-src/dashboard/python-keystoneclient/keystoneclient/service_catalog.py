# Copyright 2011 X7 LLC.
# Copyright 2011, Piston Cloud Computing, Inc.
# Copyright 2011 Nebula, Inc.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from keystoneclient import exceptions


class ServiceCatalog(object):
    """Helper methods for dealing with a Keystone Service Catalog."""

    def __init__(self, resource_dict):
        self.catalog = resource_dict

    def get_token(self):
        return self.catalog['token']['id']

    def url_for(self, attr=None, filter_value=None,
                    service_type='identity', endpoint_type='publicURL'):
        """Fetch an endpoint from the service catalog.

        Fetch the specified endpoint from the service catalog for
        a particular endpoint attribute. If no attribute is given, return
        the first endpoint of the specified type.

        See tests for a sample service catalog.
        """
        catalog = self.catalog.get('serviceCatalog', [])

        for service in catalog:
            if service['type'] != service_type:
                continue

            endpoints = service['endpoints']
            for endpoint in endpoints:
                if not filter_value or endpoint[attr] == filter_value:
                    return endpoint[endpoint_type]

        raise exceptions.EndpointNotFound('Endpoint not found.')
