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

from django import http
from django.conf import settings
from mox import IsA
from x7x import admin as OSAdmin
from x7x import auth as OSAuth
from x7x import extras as OSExtras
from engineclient.v1_1 import servers


from steer.tests.api_tests.utils import *


class Server(object):
    """ More or less fakes what the api is looking for """
    def __init__(self, id, image, attrs=None):
        self.id = id

        self.image = image
        if attrs is not None:
            self.attrs = attrs

    def __eq__(self, other):
        if self.id != other.id or \
            self.image['id'] != other.image['id']:
                return False

        for k in self.attrs:
            if other.attrs.__getattr__(k) != v:
                return False

        return True

    def __ne__(self, other):
        return not self == other


class ServerWrapperTests(test.TestCase):
    HOST = 'hostname'
    ID = '1'
    IMAGE_NAME = 'imageName'
    IMAGE_OBJ = {'id': '3', 'links': [{'href': '3', u'rel': u'bookmark'}]}

    def setUp(self):
        super(ServerWrapperTests, self).setUp()

        # these are all objects "fetched" from the api
        self.inner_attrs = {'host': self.HOST}

        self.inner_server = Server(self.ID, self.IMAGE_OBJ, self.inner_attrs)
        self.inner_server_no_attrs = Server(self.ID, self.IMAGE_OBJ)

        #self.request = self.mox.CreateMock(http.HttpRequest)

    def test_get_attrs(self):
        server = api.Server(self.inner_server, self.request)
        attrs = server.attrs
        # for every attribute in the "inner" object passed to the api wrapper,
        # see if it can be accessed through the api.ServerAttribute instance
        for k in self.inner_attrs:
            self.assertEqual(attrs.__getattr__(k), self.inner_attrs[k])

    def test_get_other(self):
        server = api.Server(self.inner_server, self.request)
        self.assertEqual(server.id, self.ID)

    def test_get_attrs_missing(self):
        server = api.Server(self.inner_server_no_attrs, self.request)
        with self.assertRaises(AttributeError):
            server.attrs

    def test_get_other_missing(self):
        server = api.Server(self.inner_server, self.request)
        with self.assertRaises(AttributeError):
            self.assertNotIn('missing', server._attrs,
                msg="Test assumption broken.  Find new missing attribute")
            server.missing

    def test_image_name(self):
        image = api.Image({'name': self.IMAGE_NAME})
        self.mox.StubOutWithMock(api.tank, 'image_get_meta')
        api.tank.image_get_meta(IsA(http.HttpRequest),
                      self.IMAGE_OBJ['id']).AndReturn(image)

        server = api.Server(self.inner_server, self.request)

        self.mox.ReplayAll()

        image_name = server.image_name

        self.assertEqual(image_name, self.IMAGE_NAME)


class EngineAdminApiTests(APITestCase):
    def stub_admin_api(self, count=1):
        self.mox.StubOutWithMock(api.engine, 'admin_api')
        admin_api = self.mox.CreateMock(OSAdmin.Admin)
        for i in range(count):
            api.engine.admin_api(IsA(http.HttpRequest)) \
                    .AndReturn(admin_api)
        return admin_api

    def test_get_admin_api(self):
        self.mox.StubOutClassWithMocks(OSAdmin, 'Admin')
        OSAdmin.Admin(auth_token=TEST_TOKEN, management_url=TEST_URL)

        self.mox.StubOutWithMock(api.deprecated, 'url_for')
        api.deprecated.url_for(IsA(http.HttpRequest),
                               'compute', True).AndReturn(TEST_URL)

        self.mox.ReplayAll()

        self.assertIsNotNone(api.engine.admin_api(self.request))

    def test_flavor_create(self):
        FLAVOR_DISK = 1000
        FLAVOR_ID = 6
        FLAVOR_MEMORY = 1024
        FLAVOR_NAME = 'newFlavor'
        FLAVOR_VCPU = 2

        admin_api = self.stub_admin_api()

        admin_api.flavors = self.mox.CreateMockAnything()
        admin_api.flavors.create(FLAVOR_NAME, FLAVOR_MEMORY, FLAVOR_VCPU,
                                 FLAVOR_DISK, FLAVOR_ID).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.flavor_create(self.request, FLAVOR_NAME,
                                    str(FLAVOR_MEMORY), str(FLAVOR_VCPU),
                                    str(FLAVOR_DISK), FLAVOR_ID)

        self.assertIsInstance(ret_val, api.Flavor)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)

    def test_flavor_delete(self):
        FLAVOR_ID = 6

        admin_api = self.stub_admin_api(count=2)

        admin_api.flavors = self.mox.CreateMockAnything()
        admin_api.flavors.delete(FLAVOR_ID, False).AndReturn(TEST_RETURN)
        admin_api.flavors.delete(FLAVOR_ID, True).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.flavor_delete(self.request, FLAVOR_ID)
        self.assertIsNone(ret_val)

        ret_val = api.flavor_delete(self.request, FLAVOR_ID, purge=True)
        self.assertIsNone(ret_val)


class ComputeApiTests(APITestCase):

    def test_flavor_get(self):
        FLAVOR_ID = 6

        engineclient = self.stub_engineclient()

        engineclient.flavors = self.mox.CreateMockAnything()
        engineclient.flavors.get(FLAVOR_ID).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.flavor_get(self.request, FLAVOR_ID)
        self.assertIsInstance(ret_val, api.Flavor)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)

    def test_server_delete(self):
        INSTANCE = 'anInstance'

        engineclient = self.stub_engineclient()
        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.servers.delete(INSTANCE).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.server_delete(self.request, INSTANCE)

        self.assertIsNone(ret_val)

    def test_server_reboot(self):
        INSTANCE_ID = '2'
        HARDNESS = servers.REBOOT_HARD

        server = self.mox.CreateMock(servers.Server)
        server.reboot(HARDNESS)

        self.mox.StubOutWithMock(api.engine, 'server_get')

        api.engine.server_get(IsA(http.HttpRequest),
                            INSTANCE_ID).AndReturn(server)

        self.mox.ReplayAll()

        ret_val = api.server_reboot(self.request, INSTANCE_ID)
        self.assertIsNone(ret_val)

    def test_server_create(self):
        NAME = 'server'
        IMAGE = 'anImage'
        FLAVOR = 'cherry'
        USER_DATA = {'nuts': 'berries'}
        KEY = 'user'
        SECGROUP = self.mox.CreateMock(api.SecurityGroup)

        engineclient = self.stub_engineclient()
        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.servers.create(NAME, IMAGE, FLAVOR, userdata=USER_DATA,
                                  security_groups=[SECGROUP], key_name=KEY)\
                                  .AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.server_create(self.request, NAME, IMAGE, FLAVOR,
                                    KEY, USER_DATA, [SECGROUP])

        self.assertIsInstance(ret_val, api.Server)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)


class ExtrasApiTests(APITestCase):

    def stub_extras_api(self, count=1):
        self.mox.StubOutWithMock(api.engine, 'extras_api')
        extras_api = self.mox.CreateMock(OSExtras.Extras)
        for i in range(count):
            api.engine.extras_api(IsA(http.HttpRequest)) \
                    .AndReturn(extras_api)
        return extras_api

    def test_get_extras_api(self):
        self.mox.StubOutClassWithMocks(OSExtras, 'Extras')
        OSExtras.Extras(auth_token=TEST_TOKEN, management_url=TEST_URL)

        self.mox.StubOutWithMock(api.deprecated, 'url_for')
        api.deprecated.url_for(IsA(http.HttpRequest),
                               'compute').AndReturn(TEST_URL)

        self.mox.ReplayAll()

        self.assertIsNotNone(api.engine.extras_api(self.request))

    def test_console_create(self):
        extras_api = self.stub_extras_api(count=2)
        extras_api.consoles = self.mox.CreateMockAnything()
        extras_api.consoles.create(
                TEST_INSTANCE_ID, TEST_CONSOLE_KIND).AndReturn(TEST_RETURN)
        extras_api.consoles.create(
                TEST_INSTANCE_ID, 'text').AndReturn(TEST_RETURN + '2')

        self.mox.ReplayAll()

        ret_val = api.console_create(self.request,
                                     TEST_INSTANCE_ID,
                                     TEST_CONSOLE_KIND)
        self.assertIsInstance(ret_val, api.Console)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)

        ret_val = api.console_create(self.request, TEST_INSTANCE_ID)
        self.assertIsInstance(ret_val, api.Console)
        self.assertEqual(ret_val._apiresource, TEST_RETURN + '2')

    def test_flavor_list(self):
        flavors = (TEST_RETURN, TEST_RETURN + '2')
        engineclient = self.stub_engineclient()
        engineclient.flavors = self.mox.CreateMockAnything()
        engineclient.flavors.list().AndReturn(flavors)

        self.mox.ReplayAll()

        ret_val = api.flavor_list(self.request)

        self.assertEqual(len(ret_val), len(flavors))
        for flavor in ret_val:
            self.assertIsInstance(flavor, api.Flavor)
            self.assertIn(flavor._apiresource, flavors)

    def test_server_list(self):
        servers = (TEST_RETURN, TEST_RETURN + '2')

        engineclient = self.stub_engineclient()

        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.servers.list().AndReturn(servers)

        self.mox.ReplayAll()

        ret_val = api.server_list(self.request)

        self.assertEqual(len(ret_val), len(servers))
        for server in ret_val:
            self.assertIsInstance(server, api.Server)
            self.assertIn(server._apiresource, servers)

    def test_usage_get(self):
        extras_api = self.stub_extras_api()

        extras_api.usage = self.mox.CreateMockAnything()
        extras_api.usage.get(TEST_TENANT_ID, 'start',
                             'end').AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.usage_get(self.request, TEST_TENANT_ID, 'start', 'end')

        self.assertIsInstance(ret_val, api.Usage)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)

    def test_usage_list(self):
        usages = (TEST_RETURN, TEST_RETURN + '2')

        extras_api = self.stub_extras_api()

        extras_api.usage = self.mox.CreateMockAnything()
        extras_api.usage.list('start', 'end').AndReturn(usages)

        self.mox.ReplayAll()

        ret_val = api.usage_list(self.request, 'start', 'end')

        self.assertEqual(len(ret_val), len(usages))
        for usage in ret_val:
            self.assertIsInstance(usage, api.Usage)
            self.assertIn(usage._apiresource, usages)

    def test_server_get(self):
        INSTANCE_ID = '2'

        engineclient = self.stub_engineclient()
        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.servers.get(INSTANCE_ID).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.server_get(self.request, INSTANCE_ID)

        self.assertIsInstance(ret_val, api.Server)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)


class APIExtensionTests(APITestCase):

    def setUp(self):
        super(APIExtensionTests, self).setUp()
        keypair = api.KeyPair(APIResource.get_instance())
        keypair.id = 1
        keypair.name = TEST_RETURN

        self.keypair = keypair
        self.keypairs = [keypair, ]

        floating_ip = api.FloatingIp(APIResource.get_instance())
        floating_ip.id = 1
        floating_ip.fixed_ip = '10.0.0.4'
        floating_ip.instance_id = 1
        floating_ip.ip = '58.58.58.58'

        self.floating_ip = floating_ip
        self.floating_ips = [floating_ip, ]

        server = api.Server(APIResource.get_instance(), self.request)
        server.id = 1

        self.server = server
        self.servers = [server, ]

    def test_server_snapshot_create(self):
        engineclient = self.stub_engineclient()

        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.servers.create_image(IsA(int), IsA(str)).\
                                                        AndReturn(self.server)
        self.mox.ReplayAll()

        server = api.snapshot_create(self.request, 1, 'test-snapshot')

        self.assertIsInstance(server, api.Server)

    def test_tenant_floating_ip_list(self):
        engineclient = self.stub_engineclient()

        engineclient.floating_ips = self.mox.CreateMockAnything()
        engineclient.floating_ips.list().AndReturn(self.floating_ips)
        self.mox.ReplayAll()

        floating_ips = api.tenant_floating_ip_list(self.request)

        self.assertEqual(len(floating_ips), len(self.floating_ips))
        self.assertIsInstance(floating_ips[0], api.FloatingIp)

    def test_tenant_floating_ip_get(self):
        engineclient = self.stub_engineclient()

        engineclient.floating_ips = self.mox.CreateMockAnything()
        engineclient.floating_ips.get(IsA(int)).AndReturn(self.floating_ip)
        self.mox.ReplayAll()

        floating_ip = api.tenant_floating_ip_get(self.request, 1)

        self.assertIsInstance(floating_ip, api.FloatingIp)

    def test_tenant_floating_ip_allocate(self):
        engineclient = self.stub_engineclient()

        engineclient.floating_ips = self.mox.CreateMockAnything()
        engineclient.floating_ips.create().AndReturn(self.floating_ip)
        self.mox.ReplayAll()

        floating_ip = api.tenant_floating_ip_allocate(self.request)

        self.assertIsInstance(floating_ip, api.FloatingIp)

    def test_tenant_floating_ip_release(self):
        engineclient = self.stub_engineclient()

        engineclient.floating_ips = self.mox.CreateMockAnything()
        engineclient.floating_ips.delete(1).AndReturn(self.floating_ip)
        self.mox.ReplayAll()

        floating_ip = api.tenant_floating_ip_release(self.request, 1)

        self.assertIsInstance(floating_ip, api.FloatingIp)

    def test_server_remove_floating_ip(self):
        engineclient = self.stub_engineclient()

        engineclient.servers = self.mox.CreateMockAnything()
        engineclient.floating_ips = self.mox.CreateMockAnything()

        engineclient.servers.get(IsA(int)).AndReturn(self.server)
        engineclient.floating_ips.get(IsA(int)).AndReturn(self.floating_ip)
        engineclient.servers.remove_floating_ip(IsA(self.server.__class__),
                                           IsA(self.floating_ip.__class__)) \
                                           .AndReturn(self.server)
        self.mox.ReplayAll()

        server = api.server_remove_floating_ip(self.request, 1, 1)

        self.assertIsInstance(server, api.Server)

    def test_server_add_floating_ip(self):
        engineclient = self.stub_engineclient()

        engineclient.floating_ips = self.mox.CreateMockAnything()
        engineclient.servers = self.mox.CreateMockAnything()

        engineclient.servers.get(IsA(int)).AndReturn(self.server)
        engineclient.floating_ips.get(IsA(int)).AndReturn(self.floating_ip)
        engineclient.servers.add_floating_ip(IsA(self.server.__class__),
                                           IsA(self.floating_ip.__class__)) \
                                           .AndReturn(self.server)
        self.mox.ReplayAll()

        server = api.server_add_floating_ip(self.request, 1, 1)

        self.assertIsInstance(server, api.Server)

    def test_keypair_create(self):
        engineclient = self.stub_engineclient()

        engineclient.keypairs = self.mox.CreateMockAnything()
        engineclient.keypairs.create(IsA(str)).AndReturn(self.keypair)
        self.mox.ReplayAll()

        ret_val = api.keypair_create(self.request, TEST_RETURN)
        self.assertIsInstance(ret_val, api.KeyPair)
        self.assertEqual(ret_val.name, self.keypair.name)

    def test_keypair_import(self):
        engineclient = self.stub_engineclient()

        engineclient.keypairs = self.mox.CreateMockAnything()
        engineclient.keypairs.create(IsA(str), IsA(str)).AndReturn(self.keypair)
        self.mox.ReplayAll()

        ret_val = api.keypair_import(self.request, TEST_RETURN, TEST_RETURN)
        self.assertIsInstance(ret_val, api.KeyPair)
        self.assertEqual(ret_val.name, self.keypair.name)

    def test_keypair_delete(self):
        engineclient = self.stub_engineclient()

        engineclient.keypairs = self.mox.CreateMockAnything()
        engineclient.keypairs.delete(IsA(int))

        self.mox.ReplayAll()

        ret_val = api.keypair_delete(self.request, self.keypair.id)
        self.assertIsNone(ret_val)

    def test_keypair_list(self):
        engineclient = self.stub_engineclient()

        engineclient.keypairs = self.mox.CreateMockAnything()
        engineclient.keypairs.list().AndReturn(self.keypairs)

        self.mox.ReplayAll()

        ret_val = api.keypair_list(self.request)

        self.assertEqual(len(ret_val), len(self.keypairs))
        for keypair in ret_val:
            self.assertIsInstance(keypair, api.KeyPair)


class VolumeTests(APITestCase):
    def setUp(self):
        super(VolumeTests, self).setUp()
        volume = api.Volume(APIResource.get_instance())
        volume.id = 1
        volume.displayName = "displayName"
        volume.attachments = [{"device": "/dev/vdb",
                               "serverId": 1,
                               "id": 1,
                               "volumeId": 1}]
        self.volume = volume
        self.volumes = [volume, ]

        self.engineclient = self.stub_engineclient()
        self.engineclient.volumes = self.mox.CreateMockAnything()

    def test_volume_list(self):
        self.engineclient.volumes.list().AndReturn(self.volumes)
        self.mox.ReplayAll()

        volumes = api.volume_list(self.request)

        self.assertIsInstance(volumes[0], api.Volume)

    def test_volume_get(self):
        self.engineclient.volumes.get(IsA(int)).AndReturn(self.volume)
        self.mox.ReplayAll()

        volume = api.volume_get(self.request, 1)

        self.assertIsInstance(volume, api.Volume)

    def test_volume_instance_list(self):
        self.engineclient.volumes.get_server_volumes(IsA(int)).AndReturn(
                self.volume.attachments)
        self.mox.ReplayAll()

        attachments = api.volume_instance_list(self.request, 1)

        self.assertEqual(attachments, self.volume.attachments)

    def test_volume_create(self):
        self.engineclient.volumes.create(IsA(int),
                                       display_name=IsA(str),
                                       display_description=IsA(str)) \
                                       .AndReturn(self.volume)
        self.mox.ReplayAll()

        new_volume = api.volume_create(self.request,
                                       10,
                                       "new volume",
                                       "new description")

        self.assertIsInstance(new_volume, api.Volume)

    def test_volume_delete(self):
        self.engineclient.volumes.delete(IsA(int))
        self.mox.ReplayAll()

        ret_val = api.volume_delete(self.request, 1)

        self.assertIsNone(ret_val)

    def test_volume_attach(self):
        self.engineclient.volumes.create_server_volume(
                IsA(int), IsA(int), IsA(str))
        self.mox.ReplayAll()

        ret_val = api.volume_attach(self.request, 1, 1, "/dev/vdb")

        self.assertIsNone(ret_val)

    def test_volume_detach(self):
        self.engineclient.volumes.delete_server_volume(IsA(int), IsA(int))
        self.mox.ReplayAll()

        ret_val = api.volume_detach(self.request, 1, 1)

        self.assertIsNone(ret_val)
