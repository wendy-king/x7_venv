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

import os
import socket

socket.setdefaulttimeout(1)

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG = True
TESTSERVER = 'http://testserver'
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/steer.db',
            'TEST_NAME': '/tmp/test_steer.db'}}

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_nose',
    'steer',
    'steer.tests',
    'steer.dashboards.engine',
    'steer.dashboards.syspanel',
    'steer.dashboards.settings')

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'steer.middleware.SteerMiddleware')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'steer.context_processors.steer')

ROOT_URLCONF = 'steer.tests.testurls'
TEMPLATE_DIRS = (os.path.join(ROOT_PATH, 'tests', 'templates'))
SITE_ID = 1
SITE_BRANDING = 'X7'
SITE_NAME = 'x7'
ENABLE_VNC = True
ENGINE_DEFAULT_ENDPOINT = None
ENGINE_DEFAULT_REGION = 'test'
ENGINE_ACCESS_KEY = 'test'
ENGINE_SECRET_KEY = 'test'

QUANTUM_URL = '127.0.0.1'
QUANTUM_PORT = '9696'
QUANTUM_TENANT = '1234'
QUANTUM_CLIENT_VERSION = '0.1'
QUANTUM_ENABLED = True

CREDENTIAL_AUTHORIZATION_DAYS = 2
CREDENTIAL_DOWNLOAD_URL = TESTSERVER + '/credentials/'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--nocapture',
             '--cover-package=steer',
             '--cover-inclusive']
# For nose-selenium integration
LIVE_SERVER_PORT = 8000

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

STEER_CONFIG = {
    'dashboards': ('engine', 'syspanel', 'settings',),
    'default_dashboard': 'engine',
}

CHASE_ACCOUNT = 'test'
CHASE_USER = 'tester'
CHASE_PASS = 'testing'
CHASE_AUTHURL = 'http://chase/chaseapi/v1.0'

X7_ADDRESS = "localhost"
X7_ADMIN_TOKEN = "x7"
X7_KEYSTONE_URL = "http://%s:5000/v2.0" % X7_ADDRESS
X7_KEYSTONE_ADMIN_URL = "http://%s:35357/v2.0" % X7_ADDRESS
X7_KEYSTONE_DEFAULT_ROLE_ID = "2"
