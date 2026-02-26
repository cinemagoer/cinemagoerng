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

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from .person import Person


@dataclass
class Credit:
    person: Person
    _: KW_ONLY
    notes: list[str] = field(default_factory=list)

    @property
    def imdb_id(self) -> str:
        return self.person.imdb_id

    @property
    def name(self) -> str:
        return self.person.name

    @property
    def as_name(self) -> str | None:
        as_notes = [note for note in self.notes if note.startswith("as ")]
        return as_notes[0][3:] if len(as_notes) > 0 else None

    @property
    def uncredited(self) -> bool:
        return "uncredited" in self.notes


@dataclass
class CrewCredit(Credit):
    _: KW_ONLY
    job: str | None = None


@dataclass
class CastCredit(Credit):
    _: KW_ONLY
    characters: list[str] = field(default_factory=list)
