# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal, TypeAlias

from . import linguistics, lookup


@dataclass
class Person:
    imdb_id: str
    name: str


@dataclass
class _Credit(Person):
    notes: list[str] = field(default_factory=list)

    @property
    def as_name(self) -> str | None:
        as_notes = [note for note in self.notes if note.startswith("as ")]
        return as_notes[0][3:] if len(as_notes) > 0 else None

    @property
    def uncredited(self) -> bool:
        return "uncredited" in self.notes


@dataclass
class CrewCredit(_Credit):
    job: str | None = None


@dataclass
class CastCredit(_Credit):
    characters: list[str] = field(default_factory=list)


@dataclass
class AKA:
    title: str
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

    @property
    def is_alternative(self):
        return len(self.notes) > 0


@dataclass
class Certificate:
    country: str
    ratings: list[str]


@dataclass
class Certification:
    mpa_rating: str | None = "Not Rated"
    mpa_rating_reason: str | None = None
    certificates: list[Certificate] = field(default_factory=list)


@dataclass
class AdvisoryVotes:
    none: int = 0
    mild: int = 0
    moderate: int = 0
    severe: int = 0


@dataclass
class AdvisoryDetail:
    text: str
    is_spoiler: bool


@dataclass
class Advisory:
    details: list[AdvisoryDetail] = field(default_factory=list)
    status: Literal["Unknown", "None", "Mild", "Moderate", "Severe"] = "Unknown"  # noqa: E501
    votes: AdvisoryVotes = field(default_factory=AdvisoryVotes)


@dataclass
class SpoilerAdvisory:
    details: list[str] = field(default_factory=list)


@dataclass
class Advisories:
    nudity: Advisory = field(default_factory=Advisory)
    violence: Advisory = field(default_factory=Advisory)
    profanity: Advisory = field(default_factory=Advisory)
    alcohol: Advisory = field(default_factory=Advisory)
    frightening: Advisory = field(default_factory=Advisory)


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
    plot_summaries: dict[str, list[str]] = field(default_factory=dict)
    taglines: list[str] = field(default_factory=list)
    akas: list[AKA] = field(default_factory=list)
    certification: Certification | None = None
    advisories: Advisories | None = None

    rating: Decimal | None = None
    vote_count: int = 0
    top_ranking: int | None = None
    bottom_ranking: int | None = None

    cast: list[CastCredit] = field(default_factory=list)
    directors: list[CrewCredit] = field(default_factory=list)
    writers: list[CrewCredit] = field(default_factory=list)
    producers: list[CrewCredit] = field(default_factory=list)
    composers: list[CrewCredit] = field(default_factory=list)
    cinematographers: list[CrewCredit] = field(default_factory=list)
    editors: list[CrewCredit] = field(default_factory=list)
    casting_directors: list[CrewCredit] = field(default_factory=list)
    production_designers: list[CrewCredit] = field(default_factory=list)
    art_directors: list[CrewCredit] = field(default_factory=list)
    set_decorators: list[CrewCredit] = field(default_factory=list)
    costume_designers: list[CrewCredit] = field(default_factory=list)
    make_up_department: list[CrewCredit] = field(default_factory=list)
    production_managers: list[CrewCredit] = field(default_factory=list)
    assistant_directors: list[CrewCredit] = field(default_factory=list)
    art_department: list[CrewCredit] = field(default_factory=list)
    sound_department: list[CrewCredit] = field(default_factory=list)
    special_effects: list[CrewCredit] = field(default_factory=list)
    visual_effects: list[CrewCredit] = field(default_factory=list)
    stunts: list[CrewCredit] = field(default_factory=list)
    choreographers: list[CrewCredit] = field(default_factory=list)
    camera_department: list[CrewCredit] = field(default_factory=list)
    animation_department: list[CrewCredit] = field(default_factory=list)
    casting_department: list[CrewCredit] = field(default_factory=list)
    costume_department: list[CrewCredit] = field(default_factory=list)
    editorial_department: list[CrewCredit] = field(default_factory=list)
    electrical_department: list[CrewCredit] = field(default_factory=list)
    location_management: list[CrewCredit] = field(default_factory=list)
    music_department: list[CrewCredit] = field(default_factory=list)
    production_department: list[CrewCredit] = field(default_factory=list)
    script_department: list[CrewCredit] = field(default_factory=list)
    transportation_department: list[CrewCredit] = field(default_factory=list)
    additional_crew: list[CrewCredit] = field(default_factory=list)
    thanks: list[CrewCredit] = field(default_factory=list)

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
class _TimedTitle(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class Movie(_TimedTitle):
    type_id: Literal["movie"] = "movie"


@dataclass(kw_only=True)
class TVMovie(_TimedTitle):
    type_id: Literal["tvMovie"] = "tvMovie"


@dataclass(kw_only=True)
class ShortMovie(_TimedTitle):
    type_id: Literal["short"] = "short"


@dataclass(kw_only=True)
class TVShortMovie(_TimedTitle):
    type_id: Literal["tvShort"] = "tvShort"


@dataclass(kw_only=True)
class VideoMovie(_TimedTitle):
    type_id: Literal["video"] = "video"


@dataclass(kw_only=True)
class MusicVideo(_TimedTitle):
    type_id: Literal["musicVideo"] = "musicVideo"


@dataclass(kw_only=True)
class VideoGame(_Title):
    type_id: Literal["videoGame"] = "videoGame"


@dataclass
class TVEpisode(_TimedTitle):
    type_id: Literal["tvEpisode"] = "tvEpisode"
    series: TVSeries | TVMiniSeries | None = None
    season: str | None = None
    episode: str | None = None
    release_date: date | None = None
    previous_episode: str | None = None
    next_episode: str | None = None


EpisodeMap: TypeAlias = dict[str, dict[str, TVEpisode]]


@dataclass(kw_only=True)
class _TVSeries(_TimedTitle):
    end_year: int | None = None
    episodes: EpisodeMap = field(default_factory=dict)
    creators: list[CrewCredit] = field(default_factory=list)

    def get_episodes_by_year(self, year: int) -> list[TVEpisode]:
        return [
            ep
            for season in self.episodes.values()
            for ep in season.values()
            if ep.year == year
        ]

    def add_episodes(self, new_episodes: list[TVEpisode]) -> None:
        for ep in new_episodes:
            if ep.episode not in self.episodes.get(ep.season, {}):
                if ep.season not in self.episodes:
                    self.episodes[ep.season] = {}
                self.episodes[ep.season][ep.episode] = ep


@dataclass(kw_only=True)
class TVSeries(_TVSeries):
    type_id: Literal["tvSeries"] = "tvSeries"


@dataclass(kw_only=True)
class TVMiniSeries(_TVSeries):
    type_id: Literal["tvMiniSeries"] = "tvMiniSeries"


@dataclass
class TVSpecial(_TimedTitle):
    type_id: Literal["tvSpecial"] = "tvSpecial"


Title: TypeAlias = (
    Movie
    | TVMovie
    | ShortMovie
    | TVShortMovie
    | VideoMovie
    | MusicVideo
    | VideoGame
    | TVSeries
    | TVMiniSeries
    | TVEpisode
    | TVSpecial
)
