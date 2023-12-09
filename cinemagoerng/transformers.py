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

import html
import json
import re
from collections.abc import Callable
from typing import TypedDict


def parse_href_id(value: str) -> str:
    if "?" in value:
        value = value.split("?")[0]
    if value[-1] == "/":
        value = value[:-1]
    return value.split("/")[-1]


def parse_type_id(value: str) -> str:
    first, *rest = value.split(" ")
    return "".join([first.lower()] + rest)


def parse_year_range(value: str) -> dict[str, int]:
    tokens = value.split("-")
    data = {"year": int(tokens[0])}
    if (len(tokens) > 1) and len(tokens[1]) > 0:
        data["end_year"] = int(tokens[1])
    return data


def parse_runtime(value: str) -> int:
    return int(value.replace(" min", ""))


def parse_vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))   # remove parens around value


_re_locale = re.compile(r"""locale: '([^']+)'""")


def parse_locale(value: str) -> str | None:
    matched = _re_locale.search(value)
    return matched.group(1) if matched is not None else None


CREDIT_SECTIONS = {
    "production_managers_": "production_managers",
    "costume_departmen": "costume_department",
    "miscellaneous": "additional_crew",
}


def parse_credit_section_id(value: str) -> str:
    return CREDIT_SECTIONS.get(value, value)


class CreditInfo(TypedDict):
    job: str | None
    as_name: str | None
    uncredited: bool
    notes: list[str]


_re_credit_notes = re.compile(r"""\(([^)]+)\)*""")


def parse_credit_info(value: str) -> CreditInfo:
    parsed: CreditInfo = {
        "job": None,
        "as_name": None,
        "uncredited": False,
        "notes": [],
    }
    notes: list[str] = _re_credit_notes.findall(value)
    if "uncredited" in notes:
        parsed["uncredited"] = True
        notes.remove("uncredited")
    if len(notes) > 0:
        if notes[-1].startswith("as "):
            parsed["as_name"] = notes[-1][3:]
            parsed["notes"] = notes[:-1]
        else:
            parsed["notes"] = notes
    parens = value.find("(")
    if parens > 0:
        parsed["job"] = value[:parens].strip()
    else:
        parsed["job"] = value
    return parsed


def update_registry(registry: dict[str, Callable]) -> None:
    registry.update({
        "json": json.loads,
        "div60": lambda x: x // 60,
        "lang": lambda x: {x["lang"]: x["text"]},
        "unescape": html.unescape,
        "href_id": parse_href_id,
        "type_id": parse_type_id,
        "year_range": parse_year_range,
        "runtime": parse_runtime,
        "vote_count": parse_vote_count,
        "locale": parse_locale,
        "credit_section_id": parse_credit_section_id,
        "credit_info": parse_credit_info,
    })
