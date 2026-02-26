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
from typing import Literal, TypeAlias

from . import linguistics, lookup
from .certification import Advisories, Certification
from .credit import CastCredit, CrewCredit


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


class TitleType(StrEnum):
    MOVIE = "movie"
    SHORT = "short"
    VIDEO = "video"
    TV_MOVIE = "tvMovie"
    TV_SHORT = "tvShort"
    TV_SERIES = "tvSeries"
    TV_MINI_SERIES = "tvMiniSeries"
    TV_EPISODE = "tvEpisode"
    TV_SPECIAL = "tvSpecial"
    MUSIC_VIDEO = "musicVideo"
    VIDEO_GAME = "videoGame"


@dataclass
class _Title:
    imdb_id: str
    title: str

    _: KW_ONLY

    primary_image: str | None = field(default=None, repr=False)

    year: int | None = None
    country_codes: list[str] = field(default_factory=list)
    language_codes: list[str] = field(default_factory=list)

    genres: list[str] = field(default_factory=list)
    taglines: list[str] = field(default_factory=list, repr=False)
    plot: dict[str, str] = field(default_factory=dict)
    plot_summaries: dict[str, list[str]] = field(default_factory=dict, repr=False)  # noqa: E501

    rating: Decimal | None = None
    vote_count: int | None = None
    top_ranking: int | None = field(default=None, repr=False)

    cast: list[CastCredit] = field(default_factory=list, repr=False)

    directors: list[CrewCredit] = field(default_factory=list)
    writers: list[CrewCredit] = field(default_factory=list, repr=False)
    producers: list[CrewCredit] = field(default_factory=list, repr=False)
    crew: dict[str, list[CrewCredit]] = field(default_factory=dict, repr=False)
    thanks: list[CrewCredit] = field(default_factory=list, repr=False)

    akas: list[AKA] = field(default_factory=list, repr=False)
    release_date: date | None = field(default=None, repr=False)

    certification: Certification | None = field(default=None, repr=False)
    advisories: Advisories | None = field(default=None, repr=False)

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


@dataclass
class _TimedTitle(_Title):
    runtime: int | None = None


@dataclass
class Movie(_TimedTitle):
    type_id: Literal[TitleType.MOVIE] = TitleType.MOVIE


@dataclass
class ShortMovie(_TimedTitle):
    type_id: Literal[TitleType.SHORT] = TitleType.SHORT


@dataclass
class Video(_TimedTitle):
    type_id: Literal[TitleType.VIDEO] = TitleType.VIDEO


@dataclass
class TVMovie(_TimedTitle):
    type_id: Literal[TitleType.TV_MOVIE] = TitleType.TV_MOVIE


@dataclass
class TVShortMovie(_TimedTitle):
    type_id: Literal[TitleType.TV_SHORT] = TitleType.TV_SHORT


@dataclass
class _TVSeries(_TimedTitle):
    _: KW_ONLY

    end_year: int | None = None
    seasons: list[str] = field(default_factory=list, repr=False)
    episodes: dict[str, dict[str, TVEpisode]] = field(default_factory=dict, repr=False)  # noqa: E501

    creators: list[CrewCredit] = field(default_factory=list, repr=False)


@dataclass
class TVSeries(_TVSeries):
    type_id: Literal[TitleType.TV_SERIES] = TitleType.TV_SERIES


@dataclass
class TVMiniSeries(_TVSeries):
    type_id: Literal[TitleType.TV_MINI_SERIES] = TitleType.TV_MINI_SERIES


@dataclass
class TVEpisode(_TimedTitle):
    type_id: Literal[TitleType.TV_EPISODE] = TitleType.TV_EPISODE

    _: KW_ONLY

    series: TVSeries | TVMiniSeries
    season: str
    episode: str
    previous_episode_id: str | None = field(default=None, repr=False)
    next_episode_id: str | None = field(default=None, repr=False)


@dataclass
class TVSpecial(_TimedTitle):
    type_id: Literal[TitleType.TV_SPECIAL] = TitleType.TV_SPECIAL


@dataclass
class MusicVideo(_TimedTitle):
    type_id: Literal[TitleType.MUSIC_VIDEO] = TitleType.MUSIC_VIDEO


@dataclass
class VideoGame(_Title):
    type_id: Literal[TitleType.VIDEO_GAME] = TitleType.VIDEO_GAME


AnyMovie: TypeAlias = Movie | ShortMovie | Video | TVMovie | TVShortMovie

Title: TypeAlias = (
    Movie
    | ShortMovie
    | Video
    | TVMovie
    | TVShortMovie
    | TVSeries
    | TVMiniSeries
    | TVEpisode
    | TVSpecial
    | MusicVideo
    | VideoGame
)
