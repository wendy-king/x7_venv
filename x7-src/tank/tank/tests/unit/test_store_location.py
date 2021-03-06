# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 X7, LLC
# All Rights Reserved.
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

import unittest

from tank.common import exception
import tank.store
import tank.store.location as location
import tank.store.http
import tank.store.filesystem
import tank.store.chase
import tank.store.s3
from tank.tests import utils

tank.store.create_stores(utils.TestConfigOpts({}))


class TestStoreLocation(unittest.TestCase):

    def test_get_location_from_uri_back_to_uri(self):
        """
        Test that for various URIs, the correct Location
        object can be contructed and then the original URI
        returned via the get_store_uri() method.
        """
        good_store_uris = [
            'https://user:pass@example.com:80/images/some-id',
            'http://images.oracle.com/123456',
            'chase://account:user:pass@authurl.com/container/obj-id',
            'chase+https://account:user:pass@authurl.com/container/obj-id',
            's3://accesskey:secretkey@s3.amazonaws.com/bucket/key-id',
            's3://accesskey:secretwith/aslash@s3.amazonaws.com/bucket/key-id',
            's3+http://accesskey:secret@s3.amazonaws.com/bucket/key-id',
            's3+https://accesskey:secretkey@s3.amazonaws.com/bucket/key-id',
            'file:///var/lib/tank/images/1']

        for uri in good_store_uris:
            loc = location.get_location_from_uri(uri)
            # The get_store_uri() method *should* return an identical URI
            # to the URI that is passed to get_location_from_uri()
            self.assertEqual(loc.get_store_uri(), uri)

    def test_bad_store_scheme(self):
        """
        Test that a URI with a non-existing scheme triggers exception
        """
        bad_uri = 'unknown://user:pass@example.com:80/images/some-id'

        self.assertRaises(exception.UnknownScheme,
                          location.get_location_from_uri,
                          bad_uri)

    def test_filesystem_store_location(self):
        """
        Test the specific StoreLocation for the Filesystem store
        """
        uri = 'file:///var/lib/tank/images/1'
        loc = tank.store.filesystem.StoreLocation({})
        loc.parse_uri(uri)

        self.assertEqual("file", loc.scheme)
        self.assertEqual("/var/lib/tank/images/1", loc.path)
        self.assertEqual(uri, loc.get_uri())

        bad_uri = 'fil://'
        self.assertRaises(Exception, loc.parse_uri, bad_uri)

        bad_uri = 'file://'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

    def test_http_store_location(self):
        """
        Test the specific StoreLocation for the HTTP store
        """
        uri = 'http://example.com/images/1'
        loc = tank.store.http.StoreLocation({})
        loc.parse_uri(uri)

        self.assertEqual("http", loc.scheme)
        self.assertEqual("example.com", loc.netloc)
        self.assertEqual("/images/1", loc.path)
        self.assertEqual(uri, loc.get_uri())

        uri = 'https://example.com:8080/images/container/1'
        loc.parse_uri(uri)

        self.assertEqual("https", loc.scheme)
        self.assertEqual("example.com:8080", loc.netloc)
        self.assertEqual("/images/container/1", loc.path)
        self.assertEqual(uri, loc.get_uri())

        uri = 'https://user:password@example.com:8080/images/container/1'
        loc.parse_uri(uri)

        self.assertEqual("https", loc.scheme)
        self.assertEqual("example.com:8080", loc.netloc)
        self.assertEqual("user", loc.user)
        self.assertEqual("password", loc.password)
        self.assertEqual("/images/container/1", loc.path)
        self.assertEqual(uri, loc.get_uri())

        uri = 'https://user:@example.com:8080/images/1'
        loc.parse_uri(uri)

        self.assertEqual("https", loc.scheme)
        self.assertEqual("example.com:8080", loc.netloc)
        self.assertEqual("user", loc.user)
        self.assertEqual("", loc.password)
        self.assertEqual("/images/1", loc.path)
        self.assertEqual(uri, loc.get_uri())

        bad_uri = 'htt://'
        self.assertRaises(Exception, loc.parse_uri, bad_uri)

        bad_uri = 'http://'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

        bad_uri = 'http://user@example.com:8080/images/1'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

    def test_chase_store_location(self):
        """
        Test the specific StoreLocation for the Chase store
        """
        uri = 'chase://example.com/images/1'
        loc = tank.store.chase.StoreLocation({})
        loc.parse_uri(uri)

        self.assertEqual("chase", loc.scheme)
        self.assertEqual("example.com", loc.authurl)
        self.assertEqual("https://example.com", loc.chase_auth_url)
        self.assertEqual("images", loc.container)
        self.assertEqual("1", loc.obj)
        self.assertEqual(None, loc.user)
        self.assertEqual(uri, loc.get_uri())

        uri = 'chase+https://user:pass@authurl.com/images/1'
        loc.parse_uri(uri)

        self.assertEqual("chase+https", loc.scheme)
        self.assertEqual("authurl.com", loc.authurl)
        self.assertEqual("https://authurl.com", loc.chase_auth_url)
        self.assertEqual("images", loc.container)
        self.assertEqual("1", loc.obj)
        self.assertEqual("user", loc.user)
        self.assertEqual("pass", loc.key)
        self.assertEqual(uri, loc.get_uri())

        uri = 'chase+https://user:pass@authurl.com/v1/container/12345'
        loc.parse_uri(uri)

        self.assertEqual("chase+https", loc.scheme)
        self.assertEqual("authurl.com/v1", loc.authurl)
        self.assertEqual("https://authurl.com/v1", loc.chase_auth_url)
        self.assertEqual("container", loc.container)
        self.assertEqual("12345", loc.obj)
        self.assertEqual("user", loc.user)
        self.assertEqual("pass", loc.key)
        self.assertEqual(uri, loc.get_uri())

        uri = 'chase+http://account:user:pass@authurl.com/v1/container/12345'
        loc.parse_uri(uri)

        self.assertEqual("chase+http", loc.scheme)
        self.assertEqual("authurl.com/v1", loc.authurl)
        self.assertEqual("http://authurl.com/v1", loc.chase_auth_url)
        self.assertEqual("container", loc.container)
        self.assertEqual("12345", loc.obj)
        self.assertEqual("account:user", loc.user)
        self.assertEqual("pass", loc.key)
        self.assertEqual(uri, loc.get_uri())

        bad_uri = 'swif://'
        self.assertRaises(Exception, loc.parse_uri, bad_uri)

        bad_uri = 'chase://'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

        bad_uri = 'chase://user@example.com:8080/images/1'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

        bad_uri = 'chase://user:pass@http://example.com:8080/images/1'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

    def test_s3_store_location(self):
        """
        Test the specific StoreLocation for the S3 store
        """
        uri = 's3://example.com/images/1'
        loc = tank.store.s3.StoreLocation({})
        loc.parse_uri(uri)

        self.assertEqual("s3", loc.scheme)
        self.assertEqual("example.com", loc.s3serviceurl)
        self.assertEqual("images", loc.bucket)
        self.assertEqual("1", loc.key)
        self.assertEqual(None, loc.accesskey)
        self.assertEqual(uri, loc.get_uri())

        uri = 's3+https://accesskey:pass@s3serviceurl.com/images/1'
        loc.parse_uri(uri)

        self.assertEqual("s3+https", loc.scheme)
        self.assertEqual("s3serviceurl.com", loc.s3serviceurl)
        self.assertEqual("images", loc.bucket)
        self.assertEqual("1", loc.key)
        self.assertEqual("accesskey", loc.accesskey)
        self.assertEqual("pass", loc.secretkey)
        self.assertEqual(uri, loc.get_uri())

        uri = 's3+https://accesskey:pass@s3serviceurl.com/v1/bucket/12345'
        loc.parse_uri(uri)

        self.assertEqual("s3+https", loc.scheme)
        self.assertEqual("s3serviceurl.com/v1", loc.s3serviceurl)
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("12345", loc.key)
        self.assertEqual("accesskey", loc.accesskey)
        self.assertEqual("pass", loc.secretkey)
        self.assertEqual(uri, loc.get_uri())

        uri = 's3://accesskey:pass/withslash@s3serviceurl.com/v1/bucket/12345'
        loc.parse_uri(uri)

        self.assertEqual("s3", loc.scheme)
        self.assertEqual("s3serviceurl.com/v1", loc.s3serviceurl)
        self.assertEqual("bucket", loc.bucket)
        self.assertEqual("12345", loc.key)
        self.assertEqual("accesskey", loc.accesskey)
        self.assertEqual("pass/withslash", loc.secretkey)
        self.assertEqual(uri, loc.get_uri())

        bad_uri = 's://'
        self.assertRaises(Exception, loc.parse_uri, bad_uri)

        bad_uri = 's3://'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

        bad_uri = 's3://accesskey@example.com:8080/images/1'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

        bad_uri = 's3://user:pass@http://example.com:8080/images/1'
        self.assertRaises(exception.BadStoreUri, loc.parse_uri, bad_uri)

    def test_get_store_from_scheme(self):
        """
        Test that the backend returned by tank.store.get_backend_class
        is correct or raises an appropriate error.
        """
        good_results = {
            'chase': tank.store.chase.Store,
            'chase+http': tank.store.chase.Store,
            'chase+https': tank.store.chase.Store,
            's3': tank.store.s3.Store,
            's3+http': tank.store.s3.Store,
            's3+https': tank.store.s3.Store,
            'file': tank.store.filesystem.Store,
            'filesystem': tank.store.filesystem.Store,
            'http': tank.store.http.Store,
            'https': tank.store.http.Store}

        for scheme, store in good_results.items():
            store_obj = tank.store.get_store_from_scheme(scheme)
            self.assertEqual(store_obj.__class__, store)

        bad_results = ['fil', 'chase+h', 'unknown']

        for store in bad_results:
            self.assertRaises(exception.UnknownScheme,
                              tank.store.get_store_from_scheme,
                              store)
