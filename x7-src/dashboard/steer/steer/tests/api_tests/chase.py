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

import cloudfiles
from django import http
from mox import IsA

from steer.tests.api_tests.utils import *


class ChaseApiTests(APITestCase):
    def setUp(self):
        super(ChaseApiTests, self).setUp()
        self.request = http.HttpRequest()
        self.request.session = dict()
        self.request.session['token'] = TEST_TOKEN

    def stub_chase_api(self, count=1):
        self.mox.StubOutWithMock(api.chase, 'chase_api')
        chase_api = self.mox.CreateMock(cloudfiles.connection.Connection)
        for i in range(count):
            api.chase.chase_api(IsA(http.HttpRequest)).AndReturn(chase_api)
        return chase_api

    def test_chase_get_containers(self):
        containers = (TEST_RETURN, TEST_RETURN + '2')

        chase_api = self.stub_chase_api()

        chase_api.get_all_containers(limit=10001,
                                     marker=None).AndReturn(containers)

        self.mox.ReplayAll()

        (conts, more) = api.chase_get_containers(self.request)

        self.assertEqual(len(conts), len(containers))
        self.assertFalse(more)

        for container in conts:
            self.assertIsInstance(container, api.Container)
            self.assertIn(container._apiresource, containers)

    def test_chase_create_container(self):
        NAME = 'containerName'

        chase_api = self.stub_chase_api()
        self.mox.StubOutWithMock(api.chase, 'chase_container_exists')

        api.chase.chase_container_exists(self.request,
                                   NAME).AndReturn(False)
        chase_api.create_container(NAME).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.chase_create_container(self.request, NAME)

        self.assertIsInstance(ret_val, api.Container)
        self.assertEqual(ret_val._apiresource, TEST_RETURN)

    def test_chase_delete_container(self):
        NAME = 'containerName'

        chase_api = self.stub_chase_api()

        chase_api.delete_container(NAME).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.chase_delete_container(self.request, NAME)

        self.assertIsNone(ret_val)

    def test_chase_get_objects(self):
        NAME = 'containerName'

        chase_objects = (TEST_RETURN, TEST_RETURN + '2')
        container = self.mox.CreateMock(cloudfiles.container.Container)
        container.get_objects(limit=10000 + 1,
                              marker=None,
                              prefix=None).AndReturn(chase_objects)

        chase_api = self.stub_chase_api()

        chase_api.get_container(NAME).AndReturn(container)

        self.mox.ReplayAll()

        (objects, more) = api.chase_get_objects(self.request, NAME)

        self.assertEqual(len(objects), len(chase_objects))
        self.assertFalse(more)

        for chase_object in objects:
            self.assertIsInstance(chase_object, api.ChaseObject)
            self.assertIn(chase_object._apiresource, chase_objects)

    def test_chase_get_objects_with_prefix(self):
        NAME = 'containerName'
        PREFIX = 'prefacedWith'

        chase_objects = (TEST_RETURN, TEST_RETURN + '2')
        container = self.mox.CreateMock(cloudfiles.container.Container)
        container.get_objects(limit=10000 + 1,
                              marker=None,
                              prefix=PREFIX).AndReturn(chase_objects)

        chase_api = self.stub_chase_api()

        chase_api.get_container(NAME).AndReturn(container)

        self.mox.ReplayAll()

        (objects, more) = api.chase_get_objects(self.request,
                                        NAME,
                                        prefix=PREFIX)

        self.assertEqual(len(objects), len(chase_objects))
        self.assertFalse(more)

        for chase_object in objects:
            self.assertIsInstance(chase_object, api.ChaseObject)
            self.assertIn(chase_object._apiresource, chase_objects)

    def test_chase_upload_object(self):
        CONTAINER_NAME = 'containerName'
        OBJECT_NAME = 'objectName'
        OBJECT_DATA = 'someData'

        chase_api = self.stub_chase_api()
        container = self.mox.CreateMock(cloudfiles.container.Container)
        chase_object = self.mox.CreateMock(cloudfiles.storage_object.Object)

        chase_api.get_container(CONTAINER_NAME).AndReturn(container)
        container.create_object(OBJECT_NAME).AndReturn(chase_object)
        chase_object.write(OBJECT_DATA).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.chase_upload_object(self.request,
                                          CONTAINER_NAME,
                                          OBJECT_NAME,
                                          OBJECT_DATA)

        self.assertIsNone(ret_val)

    def test_chase_delete_object(self):
        CONTAINER_NAME = 'containerName'
        OBJECT_NAME = 'objectName'

        chase_api = self.stub_chase_api()
        container = self.mox.CreateMock(cloudfiles.container.Container)

        chase_api.get_container(CONTAINER_NAME).AndReturn(container)
        container.delete_object(OBJECT_NAME).AndReturn(TEST_RETURN)

        self.mox.ReplayAll()

        ret_val = api.chase_delete_object(self.request,
                                          CONTAINER_NAME,
                                          OBJECT_NAME)

        self.assertIsNone(ret_val)

    def test_chase_get_object_data(self):
        CONTAINER_NAME = 'containerName'
        OBJECT_NAME = 'objectName'
        OBJECT_DATA = 'objectData'

        chase_api = self.stub_chase_api()
        container = self.mox.CreateMock(cloudfiles.container.Container)
        chase_object = self.mox.CreateMock(cloudfiles.storage_object.Object)

        chase_api.get_container(CONTAINER_NAME).AndReturn(container)
        container.get_object(OBJECT_NAME).AndReturn(chase_object)
        chase_object.stream().AndReturn(OBJECT_DATA)

        self.mox.ReplayAll()

        ret_val = api.chase_get_object_data(self.request,
                                            CONTAINER_NAME,
                                            OBJECT_NAME)

        self.assertEqual(ret_val, OBJECT_DATA)

    def test_chase_object_exists(self):
        CONTAINER_NAME = 'containerName'
        OBJECT_NAME = 'objectName'

        chase_api = self.stub_chase_api()
        container = self.mox.CreateMock(cloudfiles.container.Container)
        chase_object = self.mox.CreateMock(cloudfiles.Object)

        chase_api.get_container(CONTAINER_NAME).AndReturn(container)
        container.get_object(OBJECT_NAME).AndReturn(chase_object)

        self.mox.ReplayAll()

        ret_val = api.chase_object_exists(self.request,
                                          CONTAINER_NAME,
                                          OBJECT_NAME)
        self.assertTrue(ret_val)

    def test_chase_copy_object(self):
        CONTAINER_NAME = 'containerName'
        OBJECT_NAME = 'objectName'

        chase_api = self.stub_chase_api()
        container = self.mox.CreateMock(cloudfiles.container.Container)
        self.mox.StubOutWithMock(api.chase, 'chase_object_exists')

        chase_object = self.mox.CreateMock(cloudfiles.Object)

        chase_api.get_container(CONTAINER_NAME).AndReturn(container)
        api.chase.chase_object_exists(self.request,
                                CONTAINER_NAME,
                                OBJECT_NAME).AndReturn(False)

        container.get_object(OBJECT_NAME).AndReturn(chase_object)
        chase_object.copy_to(CONTAINER_NAME, OBJECT_NAME)

        self.mox.ReplayAll()

        ret_val = api.chase_copy_object(self.request, CONTAINER_NAME,
                                        OBJECT_NAME, CONTAINER_NAME,
                                        OBJECT_NAME)

        self.assertIsNone(ret_val)
