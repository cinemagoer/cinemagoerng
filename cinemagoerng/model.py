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

from typing import Literal, TypeAlias

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(kw_only=True)
class _Title:
    imdb_id: str
    title: str
    year: int | None = None
    rating: Decimal | None = None
    vote_count: int = 0
    genres: list[str] = field(default_factory=list)
    plot: dict[str, str] = field(default_factory=dict)
    taglines: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class Movie(_Title):
    type_id: Literal["movie"]
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMovie(_Title):
    type_id: Literal["tvMovie"]
    runtime: int | None = None


@dataclass(kw_only=True)
class ShortMovie(_Title):
    type_id: Literal["short"]
    runtime: int | None = None


@dataclass(kw_only=True)
class TVShortMovie(_Title):
    type_id: Literal["tvShort"]
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoMovie(_Title):
    type_id: Literal["video"]
    runtime: int | None = None


@dataclass(kw_only=True)
class MusicVideo(_Title):
    type_id: Literal["musicVideo"]
    runtime: int | None = None


@dataclass(kw_only=True)
class VideoGame(_Title):
    type_id: Literal["videoGame"]


@dataclass(kw_only=True)
class TVSeries(_Title):
    type_id: Literal["tvSeries"]
    end_year: int | None = None
    runtime: int | None = None


@dataclass(kw_only=True)
class TVMiniSeries(_Title):
    type_id: Literal["tvMiniSeries"]
    end_year: int | None = None
    runtime: int | None = None


@dataclass
class TVEpisode(_Title):
    type_id: Literal["tvEpisode"]
    runtime: int | None = None


@dataclass
class TVSpecial(_Title):
    type_id: Literal["tvSpecial"]
    runtime: int | None = None


Title: TypeAlias = Movie | TVMovie | ShortMovie | TVShortMovie \
                 | VideoMovie | MusicVideo | VideoGame \
                 | TVSeries | TVMiniSeries | TVEpisode \
                 | TVSpecial  # noqa: E126
