#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010 X7, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Auth Components for VNC Console."""

import os
import sys

from engine import flags
from engine import log as logging
from engine import version
from engine import wsgi
from engine.vnc import auth
from engine.vnc import proxy


LOG = logging.getLogger('engine.vncproxy')
FLAGS = flags.FLAGS
flags.DEFINE_string('vncproxy_wwwroot', '/var/lib/engine/noVNC/',
                     'Full path to noVNC directory')
flags.DEFINE_boolean('vnc_debug', False,
                     'Enable debugging features, like token bypassing')
flags.DEFINE_integer('vncproxy_port', 6080,
                     'Port that the VNC proxy should bind to')
flags.DEFINE_string('vncproxy_host', '0.0.0.0',
                     'Address that the VNC proxy should bind to')
flags.DEFINE_integer('vncproxy_flash_socket_policy_port', 843,
                     'Port that the socket policy listener should bind to')
flags.DEFINE_string('vncproxy_flash_socket_policy_host', '0.0.0.0',
                     'Address that the socket policy listener should bind to')
flags.DEFINE_integer('vnc_token_ttl', 300,
                     'How many seconds before deleting tokens')
flags.DEFINE_string('vncproxy_manager', 'engine.vnc.auth.VNCProxyAuthManager',
                    'Manager for vncproxy auth')


def get_wsgi_server():
    LOG.audit(_("Starting engine-vncproxy node (version %s)"),
              version.version_string_with_vcs())

    if not (os.path.exists(FLAGS.vncproxy_wwwroot) and
            os.path.exists(FLAGS.vncproxy_wwwroot + '/vnc_auto.html')):
        LOG.info(_("Missing vncproxy_wwwroot (version %s)"),
                    FLAGS.vncproxy_wwwroot)
        LOG.info(_("You need a slightly modified version of noVNC "
                   "to work with the engine-vnc-proxy"))
        LOG.info(_("Check out the most recent engine noVNC code: %s"),
                   "git://github.com/sleepsonthefloor/noVNC.git")
        LOG.info(_("And drop it in %s"), FLAGS.vncproxy_wwwroot)
        sys.exit(1)

    app = proxy.WebsocketVNCProxy(FLAGS.vncproxy_wwwroot)

    LOG.audit(_("Allowing access to the following files: %s"),
              app.get_whitelist())

    with_logging = auth.LoggingMiddleware(app)

    if FLAGS.vnc_debug:
        with_auth = proxy.DebugMiddleware(with_logging)
    else:
        with_auth = auth.VNCEngineAuthMiddleware(with_logging)

    wsgi_server = wsgi.Server("VNC Proxy",
                              with_auth,
                              host=FLAGS.vncproxy_host,
                              port=FLAGS.vncproxy_port)
    wsgi_server.start_tcp(handle_flash_socket_policy,
                          host=FLAGS.vncproxy_flash_socket_policy_host,
                          port=FLAGS.vncproxy_flash_socket_policy_port)
    return wsgi_server


def handle_flash_socket_policy(socket):
    LOG.info(_("Received connection on flash socket policy port"))

    fd = socket.makefile('rw')
    expected_command = "<policy-file-request/>"
    if expected_command in fd.read(len(expected_command) + 1):
        LOG.info(_("Received valid flash socket policy request"))
        fd.write('<?xml version="1.0"?><cross-domain-policy><allow-'
                 'access-from domain="*" to-ports="%d" /></cross-'
                 'domain-policy>' % (FLAGS.vncproxy_port))
        fd.flush()
    socket.close()
