"""
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2011 Cisco Systems, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Ying Liu, Cisco Systems, Inc.
#
"""
from webob import exc

from quantum.extensions import _enginetenant_view as enginetenant_view
from quantum.api import api_common as common
from quantum.common import exceptions as qexception
from quantum.common import extensions
from quantum.manager import QuantumManager
from quantum.plugins.cisco.common import cisco_faults as faults


class Enginetenant(object):
    """extension class Enginetenant"""
    def __init__(self):
        pass

    @classmethod
    def get_name(cls):
        """ Returns Ext Resource Name """
        return "Cisco Engine Tenant"

    @classmethod
    def get_alias(cls):
        """ Returns Ext Resource alias"""
        return "Cisco Engine Tenant"

    @classmethod
    def get_description(cls):
        """ Returns Ext Resource Description """
        return "enginetenant resource is used by engine side to invoke quantum api"

    @classmethod
    def get_namespace(cls):
        """ Returns Ext Resource Namespace """
        return "http://docs.ciscocloud.com/api/ext/enginetenant/v1.0"

    @classmethod
    def get_updated(cls):
        """ Returns Ext Resource Updated Time """
        return "2011-08-09T13:25:27-06:00"

    @classmethod
    def get_resources(cls):
        """ Returns Ext Resource """
        parent_resource = dict(member_name="tenant",
                               collection_name="extensions/csco/tenants")
        member_actions = {'schedule_host': "PUT",
                          'associate_port': "PUT",
                          'detach_port': "PUT"}
        controller = EnginetenantsController(QuantumManager.get_plugin())
        return [extensions.ResourceExtension('enginetenants', controller,
                                             parent=parent_resource,
                                             member_actions=member_actions)]


class EnginetenantsController(common.QuantumController):
    """ Enginetenant API controller
        based on QuantumController """

    _Enginetenant_ops_param_list = [{
        'param-name': 'enginetenant_name',
        'required': True}]

    _schedule_host_ops_param_list = [{
        'param-name': 'instance_id',
        'required': True}, {
        'param-name': 'instance_desc',
        'required': True}]

    _serialization_metadata = {
        "application/xml": {
            "attributes": {
                "enginetenant": ["id", "name"],
            },
        },
    }

    def __init__(self, plugin):
        self._resource_name = 'enginetenant'
        self._plugin = plugin

    #added for cisco's extension
    # pylint: disable-msg=E1101,W0613
    def show(self, request, tenant_id, id):
        """ Returns enginetenant details for the given enginetenant id """
        return "enginetenant is a dummy resource"

    def create(self, request, tenant_id):
        """ Creates a new enginetenant for a given tenant """
        return "enginetenant is a dummy resource"

    def update(self, request, tenant_id, id):
        """ Updates the name for the enginetenant with the given id """
        return "enginetenant is a dummy resource"

    def delete(self, request, tenant_id, id):
        """ Destroys the Enginetenant with the given id """
        return "enginetenant is a dummy resource"

    #added for cisco's extension
    def schedule_host(self, request, tenant_id, id):
        content_type = request.best_match_content_type()

        try:
            req_params = \
                self._parse_request_params(request,
                                           self._schedule_host_ops_param_list)
        except exc.HTTPError as exp:
            return faults.Fault(exp)
        instance_id = req_params['instance_id']
        instance_desc = req_params['instance_desc']
        try:
            host = self._plugin.\
            schedule_host(tenant_id, instance_id, instance_desc)
            builder = enginetenant_view.get_view_builder(request)
            result = builder.build_host(host)
            return result
        except qexception.PortNotFound as exp:
            return faults.Fault(faults.PortNotFound(exp))

    def associate_port(self, request, tenant_id, id):
        content_type = request.best_match_content_type()
        try:
            req_params = \
                self._parse_request_params(request,
                                           self._schedule_host_ops_param_list)
        except exc.HTTPError as exp:
            return faults.Fault(exp)
        instance_id = req_params['instance_id']
        instance_desc = req_params['instance_desc']
        try:
            vif = self._plugin. \
            associate_port(tenant_id, instance_id, instance_desc)
            builder = enginetenant_view.get_view_builder(request)
            result = builder.build_vif(vif)
            return result
        except qexception.PortNotFound as exp:
            return faults.Fault(faults.PortNotFound(exp))

    def detach_port(self, request, tenant_id, id):
        content_type = request.best_match_content_type()
        try:
            req_params = \
                self._parse_request_params(request,
                                           self._schedule_host_ops_param_list)
        except exc.HTTPError as exp:
            return faults.Fault(exp)

        instance_id = req_params['instance_id']
        instance_desc = req_params['instance_desc']

        try:
            vif = self._plugin. \
            detach_port(tenant_id, instance_id, instance_desc)
            builder = enginetenant_view.get_view_builder(request)
            result = builder.build_result(True)
            return result
        except qexception.PortNotFound as exp:
            return faults.Fault(faults.PortNotFound(exp))
