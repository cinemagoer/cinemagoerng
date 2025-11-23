# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

from types import MappingProxyType
from typing import Mapping


ARTICLES: Mapping[str, frozenset[str]] = MappingProxyType({
    "DE": frozenset({"das", "der", "die"}),
    "EN": frozenset({"a", "an", "the"}),
    "ES": frozenset({"el", "la", "las", "los"}),
    "FR": frozenset({"l'", "la", "le", "les"}),
    "IT": frozenset({"gli", "i", "il", "l'", "la", "le", "lo"}),
    "PT": frozenset({"a", "as", "o", "os"}),
    "SV": frozenset({"de", "den", "det"}),
})
