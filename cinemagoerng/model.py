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

from dataclasses import dataclass, field
from typing import Literal, TypeAlias


@dataclass(kw_only=True)
class _Title:
    imdb_id: int
    title: str
    year: int | None = None
    genres: list[str] = field(default_factory=list)
    taglines: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class _TimedTitle(_Title):
    runtime: int | None = None


@dataclass(kw_only=True)
class Movie(_TimedTitle):
    type: Literal["movie"]

    @property
    def type_name(self) -> str:
        return "Movie"


@dataclass(kw_only=True)
class TVMovie(_TimedTitle):
    type: Literal["tvMovie"]

    @property
    def type_name(self) -> str:
        return "TV Movie"


@dataclass(kw_only=True)
class ShortMovie(_TimedTitle):
    type: Literal["short"]

    @property
    def type_name(self) -> str:
        return "Short Movie"


@dataclass(kw_only=True)
class TVShortMovie(_TimedTitle):
    type: Literal["tvShort"]

    @property
    def type_name(self) -> str:
        return "TV Short Movie"


@dataclass(kw_only=True)
class VideoMovie(_TimedTitle):
    type: Literal["video"]

    @property
    def type_name(self) -> str:
        return "Video Movie"


@dataclass(kw_only=True)
class MusicVideo(_TimedTitle):
    type: Literal["musicVideo"]

    @property
    def type_name(self) -> str:
        return "Music Video"


@dataclass(kw_only=True)
class VideoGame(_Title):
    type: Literal["videoGame"]

    @property
    def type_name(self) -> str:
        return "Video Game"


@dataclass(kw_only=True)
class TVSeries(_TimedTitle):
    type: Literal["tvSeries"]
    end_year: int | None = None

    @property
    def type_name(self) -> str:
        return "TV Series"


@dataclass(kw_only=True)
class TVMiniSeries(_TimedTitle):
    type: Literal["tvMiniSeries"]
    end_year: int | None = None

    @property
    def type_name(self) -> str:
        return "TV Mini-Series"


@dataclass
class TVEpisode(_TimedTitle):
    type: Literal["tvEpisode"]

    @property
    def type_name(self) -> str:
        return "TV Series Episode"


@dataclass
class TVSpecial(_TimedTitle):
    type: Literal["tvSpecial"]

    @property
    def type_name(self) -> str:
        return "TV Special"


Title: TypeAlias = Movie | TVMovie | ShortMovie | TVShortMovie \
                 | VideoMovie | MusicVideo | VideoGame \
                 | TVSeries | TVMiniSeries | TVEpisode \
                 | TVSpecial  # noqa: E126
