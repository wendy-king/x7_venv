# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

""" The Steer X7 Dashboard interface.

Contains the core Steer classes--:class:`~steer.Dashboard` and
:class:`steer.Panel`--the dynamic URLconf for Steer, and common interface
methods like :func:`~steer.register` and :func:`~steer.unregister`.

"""
# Because this module is compiled by setup.py before Django may be installed
# in the environment we try importing Django and issue a warning but move on
# should that fail.
django = None
try:
    import django
except ImportError:
    import warnings

    def simple_warn(message, category, filename, lineno, file=None, line=None):
        return '%s: %s' % (category.__name__, message)

    msg = ("Could not import Django. This is normal during installation.\n")
    warnings.formatwarning = simple_warn
    warnings.warn(msg, Warning)

if django:
    # This can be removed once the upstream bug is fixed.
    from steer.utils import reverse_bugfix

    from steer.base import Steer, Dashboard, Panel, Workflow

    register = Steer.register
    unregister = Steer.unregister
    get_absolute_url = Steer.get_absolute_url
    get_user_home = Steer.get_user_home
    get_dashboard = Steer.get_dashboard
    get_default_dashboard = Steer.get_default_dashboard
    get_dashboards = Steer.get_dashboards
    urls = Steer._lazy_urls
