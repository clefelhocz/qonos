# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2013 Rackspace
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

from sqlalchemy.schema import Column
from sqlalchemy.schema import MetaData
from sqlalchemy.schema import Table

from qonos.db.sqlalchemy.migrate_repo.schema import String

meta = MetaData()

version = Column('version_id', String(36))


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    jobs = Table('jobs', meta, autoload=True)
    jobs.create_column(version)


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    jobs = Table('jobs', meta, autoload=True)
    jobs.drop_column(version)
