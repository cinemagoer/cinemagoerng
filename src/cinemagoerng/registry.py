# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
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

import html
import json
import re
from decimal import Decimal
from typing import Any, NotRequired, TypedDict

from .piculet import Node, Postprocessor, Preprocessor, Query, Transformer


########################################################################
# PREPROCESSORS                                                        #
########################################################################


def parse_next_data(root: Node) -> Node:
    next_data = Query("//script[@id='__NEXT_DATA__']/text()").apply(root)
    return json.loads(next_data)


preprocessors: dict[str, Preprocessor] = {
    "parse_next_data": parse_next_data,
}


########################################################################
# POSTPROCESSORS                                                       #
########################################################################


def set_episodes_series(data: dict[str, Any]) -> dict[str, Any]:
    series = data.get("series")
    if series is not None:
        for episode in data.get("episodes", []):
            episode["series"] = series
    return data


def set_episodes_plot_languages(data: dict[str, Any]) -> dict[str, Any]:
    lang = data.get("_page_lang")
    if lang is not None:
        for episode in data.get("episodes", []):
            plot = episode.get("plot")
            if plot is not None:
                episode["plot"] = {lang: plot}
    return data


def build_episode_map(data: dict[str, Any]) -> dict[str, Any]:
    episodes = data.get("episodes")
    if episodes is not None:
        data["episodes"] = {ep["episode"]: ep for ep in episodes}
    return data


postprocessors: dict[str, Postprocessor] = {
    "set_episodes_series": set_episodes_series,
    "set_episodes_plot_languages": set_episodes_plot_languages,
    "build_episode_map": build_episode_map,
}


########################################################################
# TRANSFORMERS                                                         #
########################################################################


class DictItem(TypedDict):
    key: str
    value: Any | None


def make_dict(item: DictItem, /) -> dict[str, Any]:
    value = item.get("value")
    if value is None:
        return {}
    return {item["key"]: value}


class DateDict(TypedDict):
    year: int | None
    month: int | None
    day: int | None


def make_date(value: DateDict) -> str | None:
    year = value.get("year")
    month = value.get("month")
    day = value.get("day")
    if (year is None) or (month is None) or (day is None):
        return None
    return f"{year}-{month:02}-{day:02}"


_CREDIT_CATEGORIES = {
    "director": "directors",
    "writer": "writers",
    "composer": "composers",
    "cinematographer": "cinematographers",
    "editor": "editors",
    "casting director": "casting_directors",
    "production designer": "production_designers",
    "art director": "art_directors",
    "set decorator": "set_decorators",
    "costume designer": "costume_designers",
    "second unit directors or assistant directors": "assistant_directors",
    "choreographer": "choreographers",
    "camera and electrical department": "camera_department",
    "costume and wardrobe department": "costume_department",
    "script and continuity department": "script_department",
    "miscellaneous": "additional_crew",
}


def parse_credit_category(value: str) -> str:
    value = value.lower()
    return _CREDIT_CATEGORIES.get(value, value.replace(" ", "_"))


_re_parenthesized = re.compile(r"""\(([^)]*)\)*""")


class CreditAttributes(TypedDict):
    job: NotRequired[str]
    notes: list[str]


def parse_credit_job(value: str) -> str | None:
    if len(value) == 0:
        return None
    parenthesis = value.find("(")
    job = value if parenthesis < 0 else value[:parenthesis].strip()
    return job if len(job) > 0 else None


def parse_credit_notes(value: str) -> list[str]:
    if len(value) == 0:
        return []
    return _re_parenthesized.findall(value)


transformers: dict[str, Transformer] = {
    "str": str,
    "lower": str.lower,
    "decimal": lambda x: Decimal(str(x)),
    "make_dict": make_dict,
    "date": make_date,
    "unescape": html.unescape,
    "div60": lambda x: x // 60,
    "credit_category": parse_credit_category,
    "credit_job": parse_credit_job,
    "credit_notes": parse_credit_notes,
}
