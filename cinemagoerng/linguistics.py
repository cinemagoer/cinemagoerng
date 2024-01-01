# Copyright 2024 H. Turgut Uyar <uyar@tekir.org>
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


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
