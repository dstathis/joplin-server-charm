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

CHARMCRAFT=charmcraft

charm: joplin-server_ubuntu-22.04-amd64.charm

format:
	ruff check --fix

check:
	ruff check
	codespell

joplin-server_ubuntu-22.04-amd64.charm: src/charm.py charmcraft.yaml requirements.txt
	$(CHARMCRAFT) pack
