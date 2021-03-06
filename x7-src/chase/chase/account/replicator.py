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

from chase.account import server as account_server
from chase.common import db, db_replicator


class AccountReplicator(db_replicator.Replicator):
    server_type = 'account'
    ring_file = 'account.ring.gz'
    brokerclass = db.AccountBroker
    datadir = account_server.DATADIR
    default_port = 6002
