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

"""
Views for managing Engine instance snapshots.
"""

import logging
import re

from django import http
from django import shortcuts
from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from tank.common import exception as tank_exception
from x7x.api import exceptions as api_exceptions

from steer import api
from steer import forms
from steer.dashboards.engine.images_and_snapshots.snapshots.forms import \
                                                                CreateSnapshot


LOG = logging.getLogger(__name__)


@login_required
def index(request):
    images = []

    try:
        images = api.snapshot_list_detailed(request)
    except tank_exception.ClientConnectionError, e:
        msg = _('Error connecting to tank: %s') % str(e)
        LOG.exception(msg)
        messages.error(request, msg)
    except tank_exception.TankException, e:
        msg = _('Error retrieving image list: %s') % str(e)
        LOG.exception(msg)
        messages.error(request, msg)

    return shortcuts.render(request,
                            'engine/images_and_snapshots/snapshots/index.html',
                            {'images': images})


@login_required
def create(request, instance_id):
    tenant_id = request.user.tenant_id
    form, handled = CreateSnapshot.maybe_handle(request,
                        initial={'tenant_id': tenant_id,
                                 'instance_id': instance_id})
    if handled:
        return handled

    try:
        instance = api.server_get(request, instance_id)
    except api_exceptions.ApiException, e:
        msg = _("Unable to retrieve instance: %s") % e
        LOG.exception(msg)
        messages.error(request, msg)
        return shortcuts.redirect(
                        'steer:engine:instances_and_volumes:instances:index')

    valid_states = ['ACTIVE']
    if instance.status not in valid_states:
        messages.error(request, _("To snapshot, instance state must be\
                                  one of the following: %s") %
                                  ', '.join(valid_states))
        return shortcuts.redirect(
                        'steer:engine:instances_and_volumes:instances:index')

    return shortcuts.render(request,
                            'engine/images_and_snapshots/snapshots/create.html',
                            {'instance': instance,
                             'create_form': form})
