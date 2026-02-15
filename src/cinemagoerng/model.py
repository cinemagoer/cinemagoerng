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
from datetime import date
from decimal import Decimal
from enum import StrEnum
from functools import partial
from typing import Any, Literal

from . import linguistics, lookup


norepr = partial(field, repr=False)


@dataclass
class Person:
    imdb_id: str
    name: str


@dataclass
class _Credit:
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
class CrewCredit(_Credit):
    _: KW_ONLY
    job: str | None = None


@dataclass
class CastCredit(_Credit):
    _: KW_ONLY
    characters: list[str] = field(default_factory=list)


@dataclass
class AKA:
    title: str
    _: KW_ONLY
    country_code: str | None = None
    language_code: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def country(self) -> str | None:
        if self.country_code is None:
            return None
        return lookup.COUNTRY_CODES[self.country_code]

    @property
    def language(self) -> str | None:
        if self.language_code is None:
            return None
        return lookup.LANGUAGE_CODES[self.language_code.upper()]


@dataclass(kw_only=True)
class Certificate:
    country: str
    ratings: list[str]


@dataclass(kw_only=True)
class Certification:
    mpa_rating: str | None = "Not Rated"
    mpa_rating_reason: str | None = None
    certificates: list[Certificate] = field(default_factory=list)


@dataclass(kw_only=True)
class AdvisoryVotes:
    none: int = 0
    mild: int = 0
    moderate: int = 0
    severe: int = 0


@dataclass(kw_only=True)
class AdvisoryDetail:
    text: str
    is_spoiler: bool


@dataclass(kw_only=True)
class Advisory:
    details: list[AdvisoryDetail] = field(default_factory=list)
    status: Literal["Unknown", "None", "Mild", "Moderate", "Severe"] = "Unknown"  # noqa: E501
    votes: AdvisoryVotes = field(default_factory=AdvisoryVotes)


@dataclass(kw_only=True)
class Advisories:
    nudity: Advisory = field(default_factory=Advisory)
    violence: Advisory = field(default_factory=Advisory)
    profanity: Advisory = field(default_factory=Advisory)
    alcohol: Advisory = field(default_factory=Advisory)
    frightening: Advisory = field(default_factory=Advisory)


class TitleType(StrEnum):
    MOVIE = "movie"
    SHORT = "short"
    VIDEO = "video"
    MUSIC_VIDEO = "musicVideo"
    TV_MOVIE = "tvMovie"
    TV_SHORT = "tvShort"
    TV_SERIES = "tvSeries"
    TV_MINI_SERIES = "tvMiniSeries"
    TV_EPISODE = "tvEpisode"
    TV_SPECIAL = "tvSpecial"
    VIDEO_GAME = "videoGame"


SERIES_ATTRS = frozenset({
    "end_year",
    "seasons",
    "episodes",
    "creators",
})

EPISODE_ATTRS = frozenset({
    "series",
    "season",
    "episode",
    "previous_episode_id",
    "next_episode_id",
})

UNSUPPORTED_ATTRS: dict[TitleType, frozenset[str]] = {
    TitleType.MOVIE: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.SHORT: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.VIDEO: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.MUSIC_VIDEO: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.TV_MOVIE: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.TV_SHORT: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.TV_SERIES: EPISODE_ATTRS,
    TitleType.TV_MINI_SERIES: EPISODE_ATTRS,
    TitleType.TV_EPISODE: SERIES_ATTRS,
    TitleType.TV_SPECIAL: SERIES_ATTRS | EPISODE_ATTRS,
    TitleType.VIDEO_GAME: SERIES_ATTRS | EPISODE_ATTRS | {"runtime"},
}


@dataclass
class Title:
    imdb_id: str
    title: str
    _: KW_ONLY
    type_id: TitleType

    primary_image: str | None = norepr(default=None)

    year: int | None = None
    release_date: date | None = norepr(default=None)
    country_codes: list[str] = field(default_factory=list)
    language_codes: list[str] = field(default_factory=list)

    runtime: int | None = norepr(default=None)

    genres: list[str] = field(default_factory=list)
    taglines: list[str] = norepr(default_factory=list)
    plot: dict[str, str] = field(default_factory=dict)
    plot_summaries: dict[str, list[str]] = norepr(default_factory=dict)

    rating: Decimal | None = None
    vote_count: int | None = None
    top_ranking: int | None = norepr(default=None)

    # for TV series
    end_year: int | None = norepr(default=None)
    seasons: list[str] | None = norepr(default=None)
    episodes: dict[str, dict[str, Title]] | None = norepr(default=None)
    creators: list[CrewCredit] | None = norepr(default=None)

    # for TV episodes
    series: Title | None = norepr(default=None)
    season: str | None = norepr(default=None)
    episode: str | None = norepr(default=None)
    previous_episode_id: str | None = norepr(default=None)
    next_episode_id: str | None = norepr(default=None)

    cast: list[CastCredit] = norepr(default_factory=list)
    directors: list[CrewCredit] = norepr(default_factory=list)
    writers: list[CrewCredit] = norepr(default_factory=list)
    producers: list[CrewCredit] = norepr(default_factory=list)
    composers: list[CrewCredit] = norepr(default_factory=list)
    cinematographers: list[CrewCredit] = norepr(default_factory=list)
    editors: list[CrewCredit] = norepr(default_factory=list)
    casting_directors: list[CrewCredit] = norepr(default_factory=list)
    production_designers: list[CrewCredit] = norepr(default_factory=list)
    art_directors: list[CrewCredit] = norepr(default_factory=list)
    set_decorators: list[CrewCredit] = norepr(default_factory=list)
    costume_designers: list[CrewCredit] = norepr(default_factory=list)
    makeup_department: list[CrewCredit] = norepr(default_factory=list)
    production_management: list[CrewCredit] = norepr(default_factory=list)
    assistant_directors: list[CrewCredit] = norepr(default_factory=list)
    art_department: list[CrewCredit] = norepr(default_factory=list)
    sound_department: list[CrewCredit] = norepr(default_factory=list)
    special_effects: list[CrewCredit] = norepr(default_factory=list)
    visual_effects: list[CrewCredit] = norepr(default_factory=list)
    stunts: list[CrewCredit] = norepr(default_factory=list)
    choreographers: list[CrewCredit] = norepr(default_factory=list)
    animation_department: list[CrewCredit] = norepr(default_factory=list)
    camera_department: list[CrewCredit] = norepr(default_factory=list)
    casting_department: list[CrewCredit] = norepr(default_factory=list)
    costume_department: list[CrewCredit] = norepr(default_factory=list)
    editorial_department: list[CrewCredit] = norepr(default_factory=list)
    location_management: list[CrewCredit] = norepr(default_factory=list)
    music_department: list[CrewCredit] = norepr(default_factory=list)
    production_department: list[CrewCredit] = norepr(default_factory=list)
    script_department: list[CrewCredit] = norepr(default_factory=list)
    transportation_department: list[CrewCredit] = norepr(default_factory=list)
    additional_crew: list[CrewCredit] = norepr(default_factory=list)
    thanks: list[CrewCredit] = norepr(default_factory=list)

    akas: list[AKA] = norepr(default_factory=list)

    certification: Certification | None = norepr(default=None)
    advisories: Advisories | None = norepr(default=None)

    def __post_init__(self) -> None:
        type_id = super().__getattribute__("type_id")
        for attr in UNSUPPORTED_ATTRS[type_id]:
            if super().__getattribute__(attr) is not None:
                raise TypeError(f"'{type_id}' takes no argument '{attr}'")

    def __getattribute__(self, name: str, /) -> Any:
        type_id = super().__getattribute__("type_id")
        if name in UNSUPPORTED_ATTRS[type_id]:
            raise AttributeError(f"'{type_id}' has no attribute '{name}'")
        return super().__getattribute__(name) if name != "type_id" else type_id

    @property
    def countries(self) -> list[str]:
        return [lookup.COUNTRY_CODES[c] for c in self.country_codes]

    @property
    def languages(self) -> list[str]:
        return [lookup.LANGUAGE_CODES[c.upper()] for c in self.language_codes]

    @property
    def sort_title(self) -> str:
        if len(self.language_codes) > 0:
            primary_lang: str = self.language_codes[0].upper()
            articles = linguistics.ARTICLES.get(primary_lang)
            if articles is not None:
                first, *rest = self.title.split(" ")
                if (len(rest) > 0) and (first.lower() in articles):
                    title = " ".join(rest)
                    if self.title[0].isupper() and title[0].islower():
                        title = title[0].upper() + title[1:]
                    return title
        return self.title


def Movie(*args: Any, **kwargs: Any) -> Title:
    return Title(type_id=TitleType.MOVIE, *args, **kwargs)
