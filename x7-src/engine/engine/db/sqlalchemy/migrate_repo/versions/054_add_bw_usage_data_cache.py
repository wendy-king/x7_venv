# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 MORITA Kazutaka.
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
#    under the License.

from sqlalchemy import Column, Table, MetaData
from sqlalchemy import Integer, BigInteger, DateTime, Boolean, String

from engine import log as logging

meta = MetaData()

bw_cache = Table('bw_usage_cache', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime(timezone=False)),
        Column('deleted', Boolean(create_constraint=True, name=None)),
        Column('id', Integer(), primary_key=True, nullable=False),
        Column('instance_id', Integer(), nullable=False),
        Column('network_label',
               String(length=255, convert_unicode=False, assert_unicode=None,
                      unicode_error=None, _warn_on_bytestring=False)),
        Column('start_period', DateTime(timezone=False), nullable=False),
        Column('last_refreshed', DateTime(timezone=False)),
        Column('bw_in', BigInteger()),
        Column('bw_out', BigInteger()))


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine;
    # bind migrate_engine to your metadata
    meta.bind = migrate_engine

    try:
        bw_cache.create()
    except Exception:
        logging.info(repr(bw_cache))
        logging.exception('Exception while creating table')
        meta.drop_all(tables=[bw_cache])
        raise


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    # Operations to reverse the above upgrade go here.
    bw_cache.drop()
