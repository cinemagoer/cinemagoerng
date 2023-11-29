# Copyright (C) 2023 H. Turgut Uyar <uyar@tekir.org>
#
# Piculet is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Piculet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Piculet.  If not, see <http://www.gnu.org/licenses/>.


from typing import Any, Callable

from decimal import Decimal
from html import unescape as unescape_html
from json import loads as load_json


json: Callable[[str], Any] = load_json
unescape: Callable[[str], str] = unescape_html


def decimal(value: float) -> Decimal:
    return Decimal(str(value))


def div60(value: int) -> int:
    return value // 60


def lang(value: dict[str, str]) -> dict[str, str]:
    return {value["lang"]: value["text"]}


def type_id(value: str) -> str:
    first, *rest = value.split(" ")
    return "".join([first.lower()] + rest)


def year_range(value: str) -> dict[str, int]:
    tokens = value.split("-")
    if not tokens[0].isdigit():
        return {}
    data = {"year": int(tokens[0])}
    if (len(tokens) > 1) and tokens[1].isdigit():
        data["end_year"] = int(tokens[1])
    return data


def runtime(value: str) -> int:
    return int(value.replace(" min", ""))


def vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))   # remove parens around value
