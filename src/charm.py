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

import ops

logger = logging.getLogger(__name__)


class JoplinServerCharm(ops.CharmBase):

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on['joplin-server'].pebble_ready, self.configure)

    def on_pebble_ready(self, event: ops.PebbleReadyEvent):
        self.unit.status = ops.ActiveStatus()


if __name__ == '__main__':
    ops.main(JoplinServerCharm)
