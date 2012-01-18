import time
import unittest

import httplib2
import mox

from keystoneclient.v2_0 import client


class TestCase(unittest.TestCase):
    TEST_TENANT_ID = '1'
    TEST_TENANT_NAME = 'aTenant'
    TEST_TOKEN = 'aToken'
    TEST_USER = 'test'
    TEST_URL = 'http://127.0.0.1:5000/v2.0'
    TEST_ADMIN_URL = 'http://127.0.0.1:35357/v2.0'

    TEST_SERVICE_CATALOG = [{
        "endpoints": [{
            "adminURL": "http://cdn.admin-nets.local:8774/v1.0",
            "region": "RegionOne",
            "internalURL": "http://127.0.0.1:8774/v1.0",
            "publicURL": "http://cdn.admin-nets.local:8774/v1.0/"
        }],
        "type": "engine_compat",
        "name": "engine_compat"
    }, {
        "endpoints": [{
            "adminURL": "http://engine/enginepi/admin",
            "region": "RegionOne",
            "internalURL": "http://engine/enginepi/internal",
            "publicURL": "http://engine/enginepi/public"
        }],
        "type": "compute",
        "name": "engine"
    }, {
        "endpoints": [{
            "adminURL": "http://tank/tankapi/admin",
            "region": "RegionOne",
            "internalURL": "http://tank/tankapi/internal",
            "publicURL": "http://tank/tankapi/public"
        }],
        "type": "image",
        "name": "tank"
    }, {
        "endpoints": [{
            "adminURL": "http://127.0.0.1:35357/v2.0",
            "region": "RegionOne",
            "internalURL": "http://127.0.0.1:5000/v2.0",
            "publicURL": "http://127.0.0.1:5000/v2.0"
        }],
        "type": "identity",
        "name": "keystone"
    }, {
        "endpoints": [{
            "adminURL": "http://chase/chaseapi/admin",
            "region": "RegionOne",
            "internalURL": "http://chase/chaseapi/internal",
            "publicURL": "http://chase/chaseapi/public"
        }],
        "type": "object-store",
        "name": "chase"
    }]

    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self._original_time = time.time
        time.time = lambda: 1234
        httplib2.Http.request = self.mox.CreateMockAnything()
        self.client = client.Client(username=self.TEST_USER,
                                    token=self.TEST_TOKEN,
                                    tenant_name=self.TEST_TENANT_NAME,
                                    auth_url=self.TEST_URL,
                                    endpoint=self.TEST_URL)

    def tearDown(self):
        time.time = self._original_time
        super(TestCase, self).tearDown()
        self.mox.UnsetStubs()
        self.mox.VerifyAll()
