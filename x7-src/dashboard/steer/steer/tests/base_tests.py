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

import copy

from django.core.urlresolvers import NoReverseMatch

import steer
from steer import base
from steer import exceptions
from steer import test
from steer.base import Steer
from steer.users import User


class MyDash(steer.Dashboard):
    name = "My Dashboard"
    slug = "mydash"


class MyPanel(steer.Panel):
    name = "My Panel"
    slug = "myslug"


class SteerTests(test.TestCase):
    def setUp(self):
        super(SteerTests, self).setUp()
        self._orig_steer = copy.deepcopy(base.Steer)

    def tearDown(self):
        super(SteerTests, self).tearDown()
        base.Steer = self._orig_steer

    def test_registry(self):
        """ Verify registration and autodiscovery work correctly.

        Please note that this implicitly tests that autodiscovery works
        by virtue of the fact that the dashboards listed in
        ``settings.INSTALLED_APPS`` are loaded from the start.
        """

        # Registration
        self.assertEqual(len(Steer._registry), 3)
        steer.register(MyDash)
        self.assertEqual(len(Steer._registry), 4)
        with self.assertRaises(ValueError):
            steer.register(MyPanel)
        with self.assertRaises(ValueError):
            steer.register("MyPanel")

        # Retrieval
        my_dash_instance_by_name = steer.get_dashboard("mydash")
        self.assertTrue(isinstance(my_dash_instance_by_name, MyDash))
        my_dash_instance_by_class = steer.get_dashboard(MyDash)
        self.assertEqual(my_dash_instance_by_name, my_dash_instance_by_class)
        with self.assertRaises(base.NotRegistered):
            steer.get_dashboard("fake")
        self.assertQuerysetEqual(steer.get_dashboards(),
                                 ['<Dashboard: Project>',
                                  '<Dashboard: Admin>',
                                  '<Dashboard: Settings>',
                                  '<Dashboard: My Dashboard>'])

        # Removal
        self.assertEqual(len(Steer._registry), 4)
        steer.unregister(MyDash)
        self.assertEqual(len(Steer._registry), 3)
        with self.assertRaises(base.NotRegistered):
            steer.get_dashboard(MyDash)

    def test_site(self):
        self.assertEqual(unicode(Steer), "Steer")
        self.assertEqual(repr(Steer), "<Site: Steer>")
        dash = Steer.get_dashboard('engine')
        self.assertEqual(Steer.get_default_dashboard(), dash)
        user = User()
        self.assertEqual(Steer.get_user_home(user), dash.get_absolute_url())

    def test_dashboard(self):
        syspanel = steer.get_dashboard("syspanel")
        self.assertEqual(syspanel._registered_with, Steer)
        self.assertQuerysetEqual(syspanel.get_panels()['System Panel'],
                                 ['<Panel: Overview>',
                                 '<Panel: Instances>',
                                 '<Panel: Services>',
                                 '<Panel: Flavors>',
                                 '<Panel: Images>',
                                 '<Panel: Tenants>',
                                 '<Panel: Users>',
                                 '<Panel: Quotas>'])
        self.assertEqual(syspanel.get_absolute_url(), "/syspanel/")
        # Test registering a module with a dashboard that defines panels
        # as a dictionary.
        syspanel.register(MyPanel)
        self.assertQuerysetEqual(syspanel.get_panels()['Other'],
                                 ['<Panel: My Panel>'])

        # Test registering a module with a dashboard that defines panels
        # as a tuple.
        settings_dash = steer.get_dashboard("settings")
        settings_dash.register(MyPanel)
        self.assertQuerysetEqual(settings_dash.get_panels(),
                                 ['<Panel: User Settings>',
                                  '<Panel: Tenant Settings>',
                                  '<Panel: My Panel>'])

    def test_panels(self):
        syspanel = steer.get_dashboard("syspanel")
        instances = syspanel.get_panel("instances")
        self.assertEqual(instances._registered_with, syspanel)
        self.assertEqual(instances.get_absolute_url(), "/syspanel/instances/")

    def test_index_url_name(self):
        syspanel = steer.get_dashboard("syspanel")
        instances = syspanel.get_panel("instances")
        instances.index_url_name = "does_not_exist"
        with self.assertRaises(NoReverseMatch):
            instances.get_absolute_url()
        instances.index_url_name = "index"
        self.assertEqual(instances.get_absolute_url(), "/syspanel/instances/")

    def test_lazy_urls(self):
        urlpatterns = steer.urls[0]
        self.assertTrue(isinstance(urlpatterns, base.LazyURLPattern))
        # The following two methods simply should not raise any exceptions
        iter(urlpatterns)
        reversed(urlpatterns)
