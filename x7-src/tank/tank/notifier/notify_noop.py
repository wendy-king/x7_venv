# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, X7 LLC.
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


from tank.notifier import strategy


class NoopStrategy(strategy.Strategy):
    """A notifier that does nothing when called."""

    def __init__(self, conf):
        pass

    def warn(self, msg):
        pass

    def info(self, msg):
        pass

    def error(self, msg):
        pass
