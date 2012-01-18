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
Views for managing Chase containers.
"""
import logging

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import shortcuts

from steer import api
from steer.dashboards.engine.containers.forms import (DeleteContainer,
        CreateContainer, FilterObjects, DeleteObject, UploadObject, CopyObject)


LOG = logging.getLogger(__name__)


@login_required
def index(request):
    marker = request.GET.get('marker', None)

    delete_form, handled = DeleteContainer.maybe_handle(request)
    if handled:
        return handled

    try:
        containers, more = api.chase_get_containers(request, marker=marker)
    except Exception, e:
        containers, more = None, None
        msg = _('Error retrieving container list: %s') % e
        LOG.exception(msg)
        messages.error(request, msg)

    return shortcuts.render(request,
                            'engine/containers/index.html',
                            {'containers': containers,
                             'delete_form': delete_form,
                             'more': more})


@login_required
def create(request):
    form, handled = CreateContainer.maybe_handle(request)
    if handled:
        return handled

    return shortcuts.render(request,
                            'engine/containers/create.html',
                            {'create_form': form})


@login_required
def object_index(request, container_name):
    marker = request.GET.get('marker', None)

    delete_form, handled = DeleteObject.maybe_handle(request)
    if handled:
        return handled

    filter_form, paged_objects = FilterObjects.maybe_handle(request)

    if paged_objects is None:
        filter_form.fields['container_name'].initial = container_name
        objects, more = api.chase_get_objects(request,
                                              container_name,
                                              marker=marker)
    else:
        objects, more = paged_objects

    delete_form.fields['container_name'].initial = container_name
    return shortcuts.render(request,
                            'engine/objects/index.html',
                            {'container_name': container_name,
                             'objects': objects,
                             'more': more,
                             'delete_form': delete_form,
                             'filter_form': filter_form})


@login_required
def object_upload(request, container_name):
    form, handled = UploadObject.maybe_handle(request)
    if handled:
        return handled

    form.fields['container_name'].initial = container_name
    return shortcuts.render(request,
                            'engine/objects/upload.html',
                            {'container_name': container_name,
                             'upload_form': form})


@login_required
def object_download(request, container_name, object_name):
    object_data = api.chase_get_object_data(
            request, container_name, object_name)

    response = http.HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % \
            object_name
    for data in object_data:
        response.write(data)
    return response


@login_required
def object_copy(request, container_name, object_name):
    containers = \
            [(c.name, c.name) for c in api.chase_get_containers(
                    request)[0]]
    form, handled = CopyObject.maybe_handle(request,
            containers=containers)

    if handled:
        return handled

    form.fields['new_container_name'].initial = container_name
    form.fields['orig_container_name'].initial = container_name
    form.fields['orig_object_name'].initial = object_name

    return shortcuts.render(request,
                            'engine/objects/copy.html',
                            {'container_name': container_name,
                             'object_name': object_name,
                             'copy_form': form})
