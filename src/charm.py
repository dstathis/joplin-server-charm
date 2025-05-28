#!/usr/bin/env python3
# Joplin Server Charmed Operator
# Copyright (C) 2024 Dylan Stephano-Shachter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import logging
import socket

import ops
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.loki_k8s.v1.loki_push_api import LogForwarder
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer

logger = logging.getLogger(__name__)


DB_NAME = "joplin_db"


class BlockedError(Exception):
    pass


class WaitingError(Exception):
    pass


class JoplinServerCharm(ops.CharmBase):

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)

        self.log_forwarder = LogForwarder(self)
        self.ingress = IngressPerAppRequirer(self, port=22300, strip_prefix=True)
        self.database = DatabaseRequires(self, relation_name='database', database_name=DB_NAME)

        framework.observe(self.on['joplin-server'].pebble_ready, self.configure)
        framework.observe(self.on['ingress'].relation_changed, self.configure)
        framework.observe(self.database.on.database_created, self.configure)
        framework.observe(self.database.on.endpoints_changed, self.configure)

    def configure(self, event: ops.PebbleReadyEvent):
        try:
            self.unit.open_port(protocol='tcp', port=22300)

            container = self.unit.get_container('joplin-server')
            if not container.can_connect():
                raise WaitingError('Waiting for container to start')

            container.add_layer('joplin-server', self.joplin_server_layer(), combine=True)
            container.autostart()
            container.replan()
            self.unit.set_ports(22300)

            self.unit.status = ops.ActiveStatus()
        except BlockedError as e:
            self.unit.status = ops.BlockedStatus(str(e))
        except WaitingError as e:
            self.unit.status = ops.WaitingStatus(str(e))

    def joplin_server_layer(self):
        env = {
            'APP_BASE_URL': self.config.get("external-url") or self.ingress.url or socket.getfqdn(),
            'APP_PORT': '22300',
            'DB_CLIENT': 'pg',
        }
        env.update(self.postgres_data())
        return {
            'summary': 'Joplin Server Layer',
            'description': 'Pebble layer for Joplin Server',
            'services': {
                'joplin-server': {
                    'override': 'replace',
                    'command': self.command(),
                    'startup': 'enabled',
                    'environment': env,
                }
            }
        }

    def command(self):
        return 'tini -- yarn start-prod'

    def postgres_data(self):
        '''Fetch postgres relation data.'''

        relations = self.database.fetch_relation_data().values()
        if len(relations) < 1:
            raise BlockedError('Postgres relation required')
        if len(relations) > 1:
            raise Exception('Multiple charms related over the database relation but limit is one')
        data = list(relations)[0]
        if not data:
            raise WaitingError('Waiting for DB info.')
        host, port = data['endpoints'].split(':')
        return {
            'POSTGRES_DATABASE': DB_NAME,
            'POSTGRES_HOST': host,
            'POSTGRES_PORT': port,
            'POSTGRES_USER': data['username'],
            'POSTGRES_PASSWORD': data['password'],
        }


if __name__ == '__main__':
    ops.main(JoplinServerCharm)
