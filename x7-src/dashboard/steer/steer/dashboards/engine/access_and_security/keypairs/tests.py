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

from django import http
from django.contrib import messages
from django.core.urlresolvers import reverse
from mox import IsA
from engineclient import exceptions as engineclient_exceptions

from steer import api
from steer import test


INDEX_VIEW_URL = reverse('steer:engine:access_and_security:index')


class KeyPairViewTests(test.BaseViewTests):
    def setUp(self):
        super(KeyPairViewTests, self).setUp()
        keypair = api.KeyPair(None)
        keypair.name = 'keyName'
        self.keypairs = (keypair,)

    def test_delete_keypair(self):
        KEYPAIR_ID = self.keypairs[0].name
        formData = {'action': 'keypairs__delete__%s' % KEYPAIR_ID}

        self.mox.StubOutWithMock(api.engine, 'keypair_list')
        self.mox.StubOutWithMock(api.engine, 'keypair_delete')

        api.engine.keypair_list(IsA(http.HttpRequest)).AndReturn(self.keypairs)
        api.engine.keypair_delete(IsA(http.HttpRequest), unicode(KEYPAIR_ID))

        self.mox.ReplayAll()

        res = self.client.post(INDEX_VIEW_URL, formData)

        self.assertRedirectsNoFollow(res, INDEX_VIEW_URL)

    def test_delete_keypair_exception(self):
        KEYPAIR_ID = self.keypairs[0].name
        formData = {'action': 'keypairs__delete__%s' % KEYPAIR_ID}

        self.mox.StubOutWithMock(api.engine, 'keypair_list')
        self.mox.StubOutWithMock(api.engine, 'keypair_delete')

        api.engine.keypair_list(IsA(http.HttpRequest)).AndReturn(self.keypairs)
        exception = engineclient_exceptions.ClientException('clientException',
                                                message='clientException')
        api.engine.keypair_delete(IsA(http.HttpRequest), unicode(KEYPAIR_ID)) \
                .AndRaise(exception)

        self.mox.ReplayAll()

        res = self.client.post(INDEX_VIEW_URL, formData)

        self.assertRedirectsNoFollow(res, INDEX_VIEW_URL)

    def test_create_keypair_get(self):
        res = self.client.get(
                reverse('steer:engine:access_and_security:keypairs:create'))

        self.assertTemplateUsed(res,
                               'engine/access_and_security/keypairs/create.html')

    def test_create_keypair_post(self):
        KEYPAIR_NAME = 'newKeypair'
        PRIVATE_KEY = 'privateKey'

        newKeyPair = self.mox.CreateMock(api.KeyPair)
        newKeyPair.name = KEYPAIR_NAME
        newKeyPair.private_key = PRIVATE_KEY

        formData = {'method': 'CreateKeypair',
                    'name': KEYPAIR_NAME,
                    }

        self.mox.StubOutWithMock(api, 'keypair_create')
        api.keypair_create(IsA(http.HttpRequest),
                           KEYPAIR_NAME).AndReturn(newKeyPair)

        self.mox.ReplayAll()

        res = self.client.post(
                   reverse('steer:engine:access_and_security:keypairs:create'),
                           formData)

        self.assertTrue(res.has_header('Content-Disposition'))

    def test_create_keypair_exception(self):
        KEYPAIR_NAME = 'newKeypair'

        formData = {'method': 'CreateKeypair',
                    'name': KEYPAIR_NAME,
                    }

        exception = engineclient_exceptions.ClientException('clientException',
                                                message='clientException')
        self.mox.StubOutWithMock(api, 'keypair_create')
        api.keypair_create(IsA(http.HttpRequest),
                           KEYPAIR_NAME).AndRaise(exception)

        self.mox.ReplayAll()

        res = self.client.post(
                   reverse('steer:engine:access_and_security:keypairs:create'),
                           formData)

        self.assertRedirectsNoFollow(res,
                 reverse('steer:engine:access_and_security:keypairs:create'))
