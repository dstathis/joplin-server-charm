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
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer

logger = logging.getLogger(__name__)


class JoplinServerCharm(ops.CharmBase):

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.ingress = IngressPerAppRequirer(self, port=22300, strip_prefix=True)
        framework.observe(self.on['joplin-server'].pebble_ready, self.configure)
        framework.observe(self.on['ingress'].relation_changed, self.configure)

    def configure(self, event: ops.PebbleReadyEvent):
        self.unit.open_port(protocol='tcp', port=22300)

        container = self.unit.get_container('joplin-server')
        if not container.can_connect():
            return

        container.add_layer("joplin-server", self.joplin_server_layer(), combine=True)
        container.autostart()
        container.replan()
        self.unit.set_ports(22300)

        self.unit.status = ops.ActiveStatus()

    def joplin_server_layer(self):
        return {
            'summary': 'Joplin Server Layer',
            'description': 'Pebble layer for Joplin Server',
            'services': {
                'joplin-server': {
                    'override': 'replace',
                    'command': self.command(),
                    'startup': 'enabled',
                    'environment': {
                        'APP_BASE_URL': self.ingress.url or socket.getfqdn(),
                        'APP_PORT': '22300',
                    },
                }
            }
        }

    def command(self):
        return 'tini -- yarn start-prod'


if __name__ == '__main__':
    ops.main(JoplinServerCharm)
