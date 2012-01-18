# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2011 Nebula, Inc.
# Copyright 2011 X7 LLC
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
Views for managing Images and Snapshots.
"""

import logging

from django import shortcuts
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from tank.common import exception as tank_exception
from engineclient import exceptions as engineclient_exceptions
from x7x.api import exceptions as api_exceptions

from steer import api
from steer.dashboards.engine.images_and_snapshots.images.forms import \
                                    (UpdateImageForm, LaunchForm, DeleteImage)


LOG = logging.getLogger(__name__)


@login_required
def index(request):
    for f in (DeleteImage, ):
        unused, handled = f.maybe_handle(request)
        if handled:
            return handled
    all_images = []
    snapshots = []
    try:
        all_images = api.image_list_detailed(request)
        snapshots = api.snapshot_list_detailed(request)
        if not all_images:
            messages.info(request, _("There are currently no images."))
    except tank_exception.ClientConnectionError, e:
        LOG.exception("Error connecting to tank")
        messages.error(request, _("Error connecting to tank: %s") % str(e))
    except tank_exception.Error, e:
        LOG.exception("Error retrieving image list")
        messages.error(request, _("Unable to fetch images: %s") % str(e))
    except api_exceptions.ApiException, e:
        msg = _("Unable to retrieve image info from tank: %s") % str(e)
        LOG.exception(msg)
        messages.error(request, msg)
    images = [im for im in all_images
              if im['container_format'] not in ['aki', 'ari']]

    quotas = api.tenant_quota_get(request, request.user.tenant_id)

    return shortcuts.render(request,
                            'engine/images_and_snapshots/index.html', {
                                'delete_form': DeleteImage(),
                                'quotas': quotas,
                                'images': images,
                                'snapshots': snapshots})
