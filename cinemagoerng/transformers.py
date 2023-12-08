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


from typing import Callable, TypedDict

import html
import json
import re
from decimal import Decimal


transformer_registry: dict[str, Callable] = {
    "decimal": lambda x: Decimal(str(x)),
    "div60": lambda x: x // 60,
    "json": json.loads,
    "lang": lambda x: {x["lang"]: x["text"]},
    "unescape": html.unescape,
}


def parse_href_id(value: str) -> str:
    if "?" in value:
        value = value.split("?")[0]
    if value[-1] == "/":
        value = value[:-1]
    return value.split("/")[-1]


transformer_registry["href_id"] = parse_href_id


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


_re_locale = re.compile(r"""locale: '([^']+)'""")


def parse_locale(value: str) -> str | None:
    matched = _re_locale.search(value)
    return matched.group(1) if matched is not None else None


transformer_registry["locale"] = parse_locale


class CreditNotes(TypedDict):
    notes: list[str]
    as_name: str | None


def parse_credit_notes(value: str) -> CreditNotes:
    parsed: CreditNotes = {"notes": [], "as_name": None}
    for note in value.splitlines():
        text = note.strip()
        if (text[0] == "(") and (text[-1] == ")"):
            text = text[1:-1]
            if text.startswith("as "):
                parsed["as_name"] = text[3:]
            else:
                parsed["notes"].append(text)
    return parsed


transformer_registry["credit_notes"] = parse_credit_notes
