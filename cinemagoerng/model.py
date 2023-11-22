# Copyright 2023 H. Turgut Uyar <uyar@tekir.org>
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

from typing import TypeAlias

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(kw_only=True)
class _Title:
    imdb_id: int
    title: str
    year: int | None = None
    rating: Decimal | None = None
    vote_count: int = 0
    genres: list[str] = field(default_factory=list)
    plot: dict[str, str] = field(default_factory=dict)
    taglines: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class Movie(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMovie(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class ShortMovie(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class TVShortMovie(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoMovie(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class MusicVideo(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoGame(_Title):
    pass


@dataclass(kw_only=True)
class TVSeries(_Title):
    end_year: int | None = None
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMiniSeries(_Title):
    end_year: int | None = None
    runtime: int | None = None


@dataclass
class TVEpisode(_Title):
    runtime: int | None = None


@dataclass
class TVSpecial(_Title):
    runtime: int | None = None


Title: TypeAlias = Movie | TVMovie | ShortMovie | TVShortMovie \
                 | VideoMovie | MusicVideo | VideoGame \
                 | TVSeries | TVMiniSeries | TVEpisode \
                 | TVSpecial  # noqa: E126


TITLE_TYPE_IDS: dict[str, type] = {
    "movie": Movie,
    "tvMovie": TVMovie,
    "short": ShortMovie,
    "tvShort": TVShortMovie,
    "video": VideoMovie,
    "musicVideo": MusicVideo,
    "videoGame": VideoGame,
    "tvSeries": TVSeries,
    "tvMiniSeries": TVMiniSeries,
    "tvEpisode": TVEpisode,
    "tvSpecial": TVSpecial,
}


TITLE_TYPE_NAMES: dict[type, str] = {
    Movie: "Movie",
    TVMovie: "TV Movie",
    ShortMovie: "Short Movie",
    TVShortMovie: "TV Short Movie",
    VideoMovie: "Video Movie",
    MusicVideo: "Music Video",
    VideoGame: "Video Game",
    TVSeries: "TV Series",
    TVMiniSeries: "TV Mini-Series",
    TVEpisode: "TV Episode",
    TVSpecial: "TV Special",
}
