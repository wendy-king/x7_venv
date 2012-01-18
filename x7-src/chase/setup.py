#!/usr/bin/python
# Copyright (c) 2010-2011 X7, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

from chase import __canonical_version__ as version


name = 'chase'


setup(
    name=name,
    version=version,
    description='Chase',
    license='Apache License (2.0)',
    author='X7, LLC.',
    author_email='x7-admins@lists.launchpad.net',
    url='https://launchpad.net/chase',
    packages=find_packages(exclude=['test', 'bin']),
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Environment :: No Input/Output (Daemon)',
        ],
    install_requires=[],  # removed for better compat
    scripts=[
        'bin/chase', 'bin/chase-account-auditor',
        'bin/chase-account-audit', 'bin/chase-account-reaper',
        'bin/chase-account-replicator', 'bin/chase-account-server',
        'bin/chase-container-auditor',
        'bin/chase-container-replicator', 'bin/chase-container-sync',
        'bin/chase-container-server', 'bin/chase-container-updater',
        'bin/chase-drive-audit', 'bin/chase-get-nodes',
        'bin/chase-init', 'bin/chase-object-auditor',
        'bin/chase-object-expirer', 'bin/chase-object-info',
        'bin/chase-object-replicator',
        'bin/chase-object-server',
        'bin/chase-object-updater', 'bin/chase-proxy-server',
        'bin/chase-ring-builder', 'bin/chase-stats-populate',
        'bin/chase-stats-report',
        'bin/chase-dispersion-populate', 'bin/chase-dispersion-report',
        'bin/chase-bench',
        'bin/chase-recon', 'bin/chase-recon-cron', 'bin/chase-orphans',
        'bin/chase-oldies'
        ],
    entry_points={
        'paste.app_factory': [
            'proxy=chase.proxy.server:app_factory',
            'object=chase.obj.server:app_factory',
            'container=chase.container.server:app_factory',
            'account=chase.account.server:app_factory',
            ],
        'paste.filter_factory': [
            'healthcheck=chase.common.middleware.healthcheck:filter_factory',
            'memcache=chase.common.middleware.memcache:filter_factory',
            'ratelimit=chase.common.middleware.ratelimit:filter_factory',
            'cname_lookup=chase.common.middleware.cname_lookup:filter_factory',
            'catch_errors=chase.common.middleware.catch_errors:filter_factory',
            'domain_remap=chase.common.middleware.domain_remap:filter_factory',
            'chase3=chase.common.middleware.chase3:filter_factory',
            'staticweb=chase.common.middleware.staticweb:filter_factory',
            'tempauth=chase.common.middleware.tempauth:filter_factory',
            'recon=chase.common.middleware.recon:filter_factory',
            ],
        },
    )
