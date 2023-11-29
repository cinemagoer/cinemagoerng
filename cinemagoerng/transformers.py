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


from typing import Callable

import html
import json
from decimal import Decimal


transformer_registry: dict[str, Callable] = {
    "decimal": lambda x: Decimal(str(x)),
    "div60": lambda x: x // 60,
    "json": json.loads,
    "lang": lambda x: {x["lang"]: x["text"]},
    "unescape": html.unescape,
}


def parse_type_id(value: str) -> str:
    first, *rest = value.split(" ")
    return "".join([first.lower()] + rest)


transformer_registry["type_id"] = parse_type_id


def parse_year_range(value: str) -> dict[str, int]:
    tokens = value.split("-")
    if not tokens[0].isdigit():
        return {}
    data = {"year": int(tokens[0])}
    if (len(tokens) > 1) and tokens[1].isdigit():
        data["end_year"] = int(tokens[1])
    return data


transformer_registry["year_range"] = parse_year_range


def parse_runtime(value: str) -> int:
    return int(value.replace(" min", ""))


transformer_registry["runtime"] = parse_runtime


def parse_vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))   # remove parens around value


transformer_registry["vote_count"] = parse_vote_count
