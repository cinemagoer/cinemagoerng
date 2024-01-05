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

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal, TypeAlias

from . import linguistics, lookup


@dataclass
class Person:
    imdb_id: str
    name: str


@dataclass
class Credit(Person):
    role: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def as_name(self) -> str | None:
        as_notes = [note for note in self.notes if note.startswith("as ")]
        return as_notes[0][3:] if len(as_notes) > 0 else None

    @property
    def uncredited(self) -> bool:
        return "uncredited" in self.notes


@dataclass(kw_only=True)
class _Title:
    imdb_id: str
    title: str

    primary_image: str | None = None

    year: int | None = None
    country_codes: list[str] = field(default_factory=list)
    language_codes: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    plot: dict[str, str] = field(default_factory=dict)
    taglines: list[str] = field(default_factory=list)

    rating: Decimal | None = None
    vote_count: int = 0

    cast: list[Credit] = field(default_factory=list)
    directors: list[Credit] = field(default_factory=list)
    writers: list[Credit] = field(default_factory=list)
    producers: list[Credit] = field(default_factory=list)
    composers: list[Credit] = field(default_factory=list)
    cinematographers: list[Credit] = field(default_factory=list)
    editors: list[Credit] = field(default_factory=list)
    editorial_department: list[Credit] = field(default_factory=list)
    casting_directors: list[Credit] = field(default_factory=list)
    production_designers: list[Credit] = field(default_factory=list)
    art_directors: list[Credit] = field(default_factory=list)
    set_decorators: list[Credit] = field(default_factory=list)
    costume_designers: list[Credit] = field(default_factory=list)
    make_up_department: list[Credit] = field(default_factory=list)
    production_managers: list[Credit] = field(default_factory=list)
    assistant_directors: list[Credit] = field(default_factory=list)
    art_department: list[Credit] = field(default_factory=list)
    sound_department: list[Credit] = field(default_factory=list)
    special_effects: list[Credit] = field(default_factory=list)
    visual_effects: list[Credit] = field(default_factory=list)
    stunts: list[Credit] = field(default_factory=list)
    camera_department: list[Credit] = field(default_factory=list)
    animation_department: list[Credit] = field(default_factory=list)
    casting_department: list[Credit] = field(default_factory=list)
    costume_department: list[Credit] = field(default_factory=list)
    location_management: list[Credit] = field(default_factory=list)
    music_department: list[Credit] = field(default_factory=list)
    script_department: list[Credit] = field(default_factory=list)
    transportation_department: list[Credit] = field(default_factory=list)
    additional_crew: list[Credit] = field(default_factory=list)
    thanks: list[Credit] = field(default_factory=list)

    @property
    def countries(self) -> list[str]:
        return [lookup.COUNTRY_CODES[c] for c in self.country_codes]

    @property
    def languages(self) -> list[str]:
        return [lookup.LANGUAGE_CODES[c.upper()] for c in self.language_codes]

    @property
    def sort_title(self) -> str:
        if len(self.language_codes) > 0:
            primary_lang = self.language_codes[0].upper()
            articles = linguistics.ARTICLES.get(primary_lang)
            if articles is not None:
                first, *rest = self.title.split(" ")
                if (len(rest) > 0) and (first.lower() in articles):
                    title = " ".join(rest)
                    if self.title[0].isupper() and title[0].islower():
                        title = title[0].upper() + title[1:]
                    return title
        return self.title


@dataclass(kw_only=True)
class Movie(_Title):
    type_id: Literal["movie"] = "movie"
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMovie(_Title):
    type_id: Literal["tvMovie"] = "tvMovie"
    runtime: int | None = None


@dataclass(kw_only=True)
class ShortMovie(_Title):
    type_id: Literal["short"] = "short"
    runtime: int | None = None


@dataclass(kw_only=True)
class TVShortMovie(_Title):
    type_id: Literal["tvShort"] = "tvShort"
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoMovie(_Title):
    type_id: Literal["video"] = "video"
    runtime: int | None = None


@dataclass(kw_only=True)
class MusicVideo(_Title):
    type_id: Literal["musicVideo"] = "musicVideo"
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoGame(_Title):
    type_id: Literal["videoGame"] = "videoGame"


@dataclass(kw_only=True)
class TVSeries(_Title):
    type_id: Literal["tvSeries"] = "tvSeries"
    end_year: int | None = None
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMiniSeries(_Title):
    type_id: Literal["tvMiniSeries"] = "tvMiniSeries"
    end_year: int | None = None
    runtime: int | None = None


@dataclass
class TVEpisode(_Title):
    type_id: Literal["tvEpisode"] = "tvEpisode"
    runtime: int | None = None


@dataclass
class TVSpecial(_Title):
    type_id: Literal["tvSpecial"] = "tvSpecial"
    runtime: int | None = None


Title: TypeAlias = Movie | TVMovie | ShortMovie | TVShortMovie \
                 | VideoMovie | MusicVideo | VideoGame \
                 | TVSeries | TVMiniSeries | TVEpisode \
                 | TVSpecial  # noqa: E126
