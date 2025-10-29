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

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Literal, TypeAlias

from . import linguistics, lookup, web
from .piculet import JSONSpec, XMLSpec, deserialize


@dataclass(kw_only=True)
class Person:
    imdb_id: str
    name: str


@dataclass
class _Credit:
    person: Person
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


@dataclass(kw_only=True)
class CrewCredit(_Credit):
    job: str | None = None


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
class _Title:
    imdb_id: str
    title: str

    primary_image: str | None = None

    year: int | None = None
    country_codes: list[str] = field(default_factory=list)
    language_codes: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    taglines: list[str] = field(default_factory=list)
    plot: dict[str, str] = field(default_factory=dict)
    plot_summaries: dict[str, list[str]] = field(default_factory=dict)

    rating: Decimal | None = None
    vote_count: int = 0
    top_ranking: int | None = None

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
    makeup_department: list[CrewCredit] = field(default_factory=list)
    production_management: list[CrewCredit] = field(default_factory=list)
    assistant_directors: list[CrewCredit] = field(default_factory=list)
    art_department: list[CrewCredit] = field(default_factory=list)
    sound_department: list[CrewCredit] = field(default_factory=list)
    special_effects: list[CrewCredit] = field(default_factory=list)
    visual_effects: list[CrewCredit] = field(default_factory=list)
    stunts: list[CrewCredit] = field(default_factory=list)
    choreographers: list[CrewCredit] = field(default_factory=list)
    animation_department: list[CrewCredit] = field(default_factory=list)
    camera_department: list[CrewCredit] = field(default_factory=list)
    casting_department: list[CrewCredit] = field(default_factory=list)
    costume_department: list[CrewCredit] = field(default_factory=list)
    editorial_department: list[CrewCredit] = field(default_factory=list)
    location_management: list[CrewCredit] = field(default_factory=list)
    music_department: list[CrewCredit] = field(default_factory=list)
    production_department: list[CrewCredit] = field(default_factory=list)
    script_department: list[CrewCredit] = field(default_factory=list)
    transportation_department: list[CrewCredit] = field(default_factory=list)
    additional_crew: list[CrewCredit] = field(default_factory=list)
    thanks: list[CrewCredit] = field(default_factory=list)

    akas: list[AKA] = field(default_factory=list)

    certification: Certification | None = None
    advisories: Advisories | None = None

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

    def set_taglines(
            self,
            *,
            headers: dict[str, str] | None = None,
    ) -> None:
        spec = web.get_spec("title_taglines")
        context = {"imdb_id": self.imdb_id}
        data = web.scrape(spec=spec, context=context, headers=headers)
        taglines = data.get("taglines")
        if taglines is not None:
            self.taglines = data["taglines"]

    def set_akas(
            self,
            *,
            spec: XMLSpec | JSONSpec | None = None,
            headers: dict[str, str] | None = None,
    ) -> None:
        if spec is None:
            spec = web.get_spec("title_akas")
        g_params: web.GraphQLParams = spec.graphql  # type: ignore
        g_vars = g_params["variables"]
        if "after" not in g_vars:
            g_vars["after"] = "null"
        context: dict[str, Any] = {"imdb_id": self.imdb_id} | g_vars
        data = web.scrape(spec, context=context, headers=headers)
        akas = [deserialize(aka, AKA) for aka in data.get("akas", [])]
        self.akas.extend(akas)
        if data.get("has_next_page", False):
            g_vars["after"] = data["end_cursor"]
            self.set_akas(spec=spec, headers=headers)

    def set_parental_guide(
            self,
            *,
            headers: dict[str, str] | None = None,
    ) -> None:
        spec = web.get_spec("title_parental_guide")
        context = {"imdb_id": self.imdb_id}
        data = web.scrape(spec=spec, context=context, headers=headers)
        self.certification = deserialize(data["certification"], Certification)
        self.advisories = deserialize(data["advisories"], Advisories)


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


@dataclass(kw_only=True)
class TVEpisode(_TimedTitle):
    type_id: Literal["tvEpisode"] = "tvEpisode"
    series: TVSeries | TVMiniSeries
    season: str
    episode: str
    release_date: date | None = None
    previous_episode_id: str | None = None
    next_episode_id: str | None = None


@dataclass(kw_only=True)
class _TVSeries(_TimedTitle):
    end_year: int | None = None
    seasons: list[str] = field(default_factory=list)
    episodes: dict[str, dict[str, TVEpisode]] = field(default_factory=dict)
    creators: list[CrewCredit] = field(default_factory=list)

    def set_episodes(
            self,
            *,
            season: str,
            headers: dict[str, str] | None = None,
    ) -> None:
        spec = web.get_spec("title_episodes")
        context = {"imdb_id": self.imdb_id, "season": season}
        data = web.scrape(spec=spec, context=context, headers=headers)
        episodes = data.get("episodes")
        if episodes is not None:
            self.episodes[season] = deserialize(episodes, dict[str, TVEpisode])


@dataclass(kw_only=True)
class TVSeries(_TVSeries):
    type_id: Literal["tvSeries"] = "tvSeries"


@dataclass(kw_only=True)
class TVMiniSeries(_TVSeries):
    type_id: Literal["tvMiniSeries"] = "tvMiniSeries"


@dataclass(kw_only=True)
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
