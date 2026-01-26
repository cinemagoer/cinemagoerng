# Copyright 2024-2026 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG.  If not, see <https://www.gnu.org/licenses/>.

from collections.abc import Mapping
from types import MappingProxyType


ARTICLES: Mapping[str, frozenset[str]] = MappingProxyType({
    "DE": frozenset({"das", "der", "die"}),
    "EN": frozenset({"a", "an", "the"}),
    "ES": frozenset({"el", "la", "las", "los"}),
    "FR": frozenset({"l'", "la", "le", "les"}),
    "IT": frozenset({"gli", "i", "il", "l'", "la", "le", "lo"}),
    "PT": frozenset({"a", "as", "o", "os"}),
    "SV": frozenset({"de", "den", "det"}),
})
