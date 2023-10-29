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
from typing import Union


@dataclass
class Title:
    imdb_id: int
    default_title: str
    original_title: Union[str, None]
    years: Union[str, None]

    @property
    def title(self) -> str:
        return self.original_title if self.original_title is not None else \
            self.default_title

    @property
    def year(self) -> Union[int, None]:
        if self.years is None:
            return None
        return int(self.years.split("-")[0])

    @property
    def end_year(self) -> Union[int, None]:
        if self.years is None:
            return None
        years = self.years.split("-")
        if len(years) == 1:
            return None
        if years[1] == "":
            return None
        return int(years[1])
