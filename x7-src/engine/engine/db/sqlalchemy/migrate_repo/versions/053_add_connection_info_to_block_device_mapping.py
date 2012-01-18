# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 X7 LLC.
# All Rights Reserved.
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
#    under the License.from sqlalchemy import *

from sqlalchemy import Column, MetaData, Table, Text


meta = MetaData()

new_column = Column('connection_info', Text())


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    table = Table('block_device_mapping', meta, autoload=True)
    table.create_column(new_column)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    table = Table('block_device_mapping', meta, autoload=True)
    table.c.connection_info.drop()