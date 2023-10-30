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

from dataclasses import dataclass
from typing import Literal, TypeAlias


@dataclass(kw_only=True)
class _Title:
    imdb_id: int
    title: str
    year: int | None = None
    genres: list[str] | None = None


@dataclass(kw_only=True)
class Movie(_Title):
    type: Literal["movie"]


@dataclass(kw_only=True)
class TVMovie(_Title):
    type: Literal["tvMovie"]


@dataclass(kw_only=True)
class Video(_Title):
    type: Literal["video"]


@dataclass(kw_only=True)
class VideoGame(_Title):
    type: Literal["videoGame"]


@dataclass(kw_only=True)
class TVSeries(_Title):
    type: Literal["tvSeries"]
    end_year: int | None = None


@dataclass(kw_only=True)
class TVMiniSeries(_Title):
    type: Literal["tvMiniSeries"]
    end_year: int | None = None


@dataclass
class TVEpisode(_Title):
    type: Literal["tvEpisode"]


Title: TypeAlias = Movie | TVMovie | Video | VideoGame \
                 | TVSeries | TVMiniSeries | TVEpisode  # noqa: E126
