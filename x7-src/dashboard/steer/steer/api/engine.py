# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2011 Nebula, Inc.
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

from __future__ import absolute_import

import logging

from django.contrib import messages
from engineclient.v1_1 import client as engine_client
from engineclient.v1_1.servers import REBOOT_HARD

from steer.api.base import *
from steer.api.deprecated import admin_api
from steer.api.deprecated import check_x7x
from steer.api.deprecated import extras_api

LOG = logging.getLogger(__name__)


class Console(APIResourceWrapper):
    """Simple wrapper around x7x.extras.consoles.Console"""
    _attrs = ['id', 'output', 'type']


class Flavor(APIResourceWrapper):
    """Simple wrapper around x7x.admin.flavors.Flavor"""
    _attrs = ['disk', 'id', 'links', 'name', 'ram', 'vcpus']


class FloatingIp(APIResourceWrapper):
    """Simple wrapper for floating ips"""
    _attrs = ['ip', 'fixed_ip', 'instance_id', 'id']


class KeyPair(APIResourceWrapper):
    """Simple wrapper around x7x.extras.keypairs.Keypair"""
    _attrs = ['fingerprint', 'name', 'private_key']


class VirtualInterface(APIResourceWrapper):
    _attrs = ['id', 'mac_address']


class Volume(APIResourceWrapper):
    """Engine Volume representation"""
    _attrs = ['id', 'status', 'displayName', 'size', 'volumeType', 'createdAt',
              'attachments', 'displayDescription']


class Quota(object):
    """ Basic wrapper for individual limits in a quota. """
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit

    def __repr__(self):
        return "<Quota: (%s, %s)>" % (self.name, self.limit)


class Server(APIResourceWrapper):
    """Simple wrapper around x7x.extras.server.Server

       Preserves the request info so image name can later be retrieved
    """
    _attrs = ['addresses', 'attrs', 'hostId', 'id', 'image', 'links',
             'metadata', 'name', 'private_ip', 'public_ip', 'status', 'uuid',
             'image_name', 'VirtualInterfaces', 'flavor', 'key_name']

    def __init__(self, apiresource, request):
        super(Server, self).__init__(apiresource)
        self.request = request

    def __getattr__(self, attr):
        if attr == "attrs":
            return ServerAttributes(super(Server, self).__getattr__(attr))
        else:
            return super(Server, self).__getattr__(attr)

    @property
    def image_name(self):
        from tank.common import exception as tank_exceptions
        from steer.api import tank
        try:
            image = tank.image_get_meta(self.request, self.image['id'])
            return image.name
        except tank_exceptions.NotFound:
            return "(not found)"

    def reboot(self, hardness=REBOOT_HARD):
        engineclient(self.request).servers.reboot(self.id, hardness)


class ServerAttributes(APIDictWrapper):
    """Simple wrapper around x7x.extras.server.Server attributes

       Preserves the request info so image name can later be retrieved
    """
    _attrs = ['disk_gb', 'host', 'image_ref', 'kernel_id',
              'key_name', 'launched_at', 'mac_address', 'memory_mb', 'name',
              'os_type', 'tenant_id', 'ramdisk_id', 'scheduled_at',
              'terminated_at', 'user_data', 'user_id', 'vcpus', 'hostname',
              'security_groups']


class Usage(APIResourceWrapper):
    """Simple wrapper around x7x.extras.usage.Usage"""
    _attrs = ['begin', 'instances', 'stop', 'tenant_id',
             'total_active_disk_size', 'total_active_instances',
             'total_active_ram_size', 'total_active_vcpus', 'total_cpu_usage',
             'total_disk_usage', 'total_hours', 'total_ram_usage']


class SecurityGroup(APIResourceWrapper):
    """Simple wrapper around x7x.extras.security_groups.SecurityGroup"""
    _attrs = ['id', 'name', 'description', 'tenant_id', 'rules']


class SecurityGroupRule(APIDictWrapper):
    """ Simple wrapper for individual rules in a SecurityGroup. """
    _attrs = ['ip_protocol', 'from_port', 'to_port', 'ip_range']


def engineclient(request):
    LOG.debug('engineclient connection created using token "%s" and url "%s"' %
              (request.user.token, url_for(request, 'compute')))
    c = engine_client.Client(request.user.username,
                           request.user.token,
                           project_id=request.user.tenant_id,
                           auth_url=url_for(request, 'compute'))
    c.client.auth_token = request.user.token
    c.client.management_url = url_for(request, 'compute')
    return c


def console_create(request, instance_id, kind='text'):
    return Console(extras_api(request).consoles.create(instance_id, kind))


def flavor_create(request, name, memory, vcpu, disk, flavor_id):
    # TODO -- convert to engineclient when engineclient adds create support
    return Flavor(admin_api(request).flavors.create(
            name, int(memory), int(vcpu), int(disk), flavor_id))


def flavor_delete(request, flavor_id, purge=False):
    # TODO -- convert to engineclient when engineclient adds delete support
    admin_api(request).flavors.delete(flavor_id, purge)


def flavor_get(request, flavor_id):
    return Flavor(engineclient(request).flavors.get(flavor_id))


def flavor_list(request):
    return [Flavor(f) for f in engineclient(request).flavors.list()]


def tenant_floating_ip_list(request):
    """
    Fetches a list of all floating ips.
    """
    return [FloatingIp(ip) for ip in engineclient(request).floating_ips.list()]


def tenant_floating_ip_get(request, floating_ip_id):
    """
    Fetches a floating ip.
    """
    return engineclient(request).floating_ips.get(floating_ip_id)


def tenant_floating_ip_allocate(request):
    """
    Allocates a floating ip to tenant.
    """
    return engineclient(request).floating_ips.create()


def tenant_floating_ip_release(request, floating_ip_id):
    """
    Releases floating ip from the pool of a tenant.
    """
    return engineclient(request).floating_ips.delete(floating_ip_id)


def snapshot_create(request, instance_id, name):
    return engineclient(request).servers.create_image(instance_id, name)


def keypair_create(request, name):
    return KeyPair(engineclient(request).keypairs.create(name))


def keypair_import(request, name, public_key):
    return KeyPair(engineclient(request).keypairs.create(name, public_key))


def keypair_delete(request, keypair_id):
    engineclient(request).keypairs.delete(keypair_id)


def keypair_list(request):
    return [KeyPair(key) for key in engineclient(request).keypairs.list()]


def server_create(request, name, image, flavor,
                           key_name, user_data, security_groups):
    return Server(engineclient(request).servers.create(
            name, image, flavor, userdata=user_data,
            security_groups=security_groups,
            key_name=key_name), request)


def server_delete(request, instance):
    engineclient(request).servers.delete(instance)


def server_get(request, instance_id):
    return Server(engineclient(request).servers.get(instance_id), request)


def server_list(request):
    return [Server(s, request) for s in engineclient(request).servers.list()]


def server_console_output(request, instance_id, tail_length=None):
    """Gets console output of an instance"""
    return engineclient(request).servers.get_console_output(instance_id,
                                                          length=tail_length)


@check_x7x
def admin_server_list(request):
    return [Server(s, request) for s in admin_api(request).servers.list()]


def server_reboot(request,
                  instance_id,
                  hardness=REBOOT_HARD):
    server = server_get(request, instance_id)
    server.reboot(hardness)


def server_update(request, instance_id, name):
    return engineclient(request).servers.update(instance_id, name=name)


def server_add_floating_ip(request, server, address):
    """
    Associates floating IP to server's fixed IP.
    """
    server = engineclient(request).servers.get(server)
    fip = engineclient(request).floating_ips.get(address)

    return engineclient(request).servers.add_floating_ip(server, fip)


def server_remove_floating_ip(request, server, address):
    """
    Removes relationship between floating and server's fixed ip.
    """
    fip = engineclient(request).floating_ips.get(address)
    server = engineclient(request).servers.get(fip.instance_id)

    return engineclient(request).servers.remove_floating_ip(server, fip)


def tenant_quota_get(request, tenant):
    return engineclient(request).quotas.get(tenant)


@check_x7x
def usage_get(request, tenant_id, start, end):
    return Usage(extras_api(request).usage.get(tenant_id, start, end))


@check_x7x
def usage_list(request, start, end):
    return [Usage(u) for u in extras_api(request).usage.list(start, end)]


def security_group_list(request):
    return [SecurityGroup(g) for g in engineclient(request).\
                                     security_groups.list()]


def security_group_get(request, security_group_id):
    return SecurityGroup(engineclient(request).\
                         security_groups.get(security_group_id))


def security_group_create(request, name, description):
    return SecurityGroup(engineclient(request).\
                         security_groups.create(name, description))


def security_group_delete(request, security_group_id):
    engineclient(request).security_groups.delete(security_group_id)


def security_group_rule_create(request, parent_group_id, ip_protocol=None,
                               from_port=None, to_port=None, cidr=None,
                               group_id=None):
    return SecurityGroup(engineclient(request).\
                         security_group_rules.create(parent_group_id,
                                                     ip_protocol,
                                                     from_port,
                                                     to_port,
                                                     cidr,
                                                     group_id))


def security_group_rule_delete(request, security_group_rule_id):
    engineclient(request).security_group_rules.delete(security_group_rule_id)


def volume_list(request):
    return [Volume(vol) for vol in engineclient(request).volumes.list()]


def volume_get(request, volume_id):
    return Volume(engineclient(request).volumes.get(volume_id))


def volume_instance_list(request, instance_id):
    return engineclient(request).volumes.get_server_volumes(instance_id)


def volume_create(request, size, name, description):
    return Volume(engineclient(request).volumes.create(
            size, display_name=name, display_description=description))


def volume_delete(request, volume_id):
    engineclient(request).volumes.delete(volume_id)


def volume_attach(request, volume_id, instance_id, device):
    engineclient(request).volumes.create_server_volume(
            instance_id, volume_id, device)


def volume_detach(request, instance_id, attachment_id):
    engineclient(request).volumes.delete_server_volume(
            instance_id, attachment_id)
