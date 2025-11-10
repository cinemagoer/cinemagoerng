# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

import html
import json
import re
from typing import Any, NotRequired, TypedDict

from .piculet import (
    CollectedData,
    JSONNode,
    Postprocessor,
    Preprocessor,
    Transformer,
    XMLNode,
    XMLPath,
)

########################################################################
# PREPROCESSORS                                                        #
########################################################################


def parse_next_data(root: XMLNode) -> JSONNode:
    path = XMLPath("//script[@id='__NEXT_DATA__']/text()")
    next_data = path.apply(root)
    return json.loads(next_data)


def update_preprocessors(preprocessors: dict[str, Preprocessor]) -> None:
    preprocessors.update({
        "parse_next_data": parse_next_data,
    })


########################################################################
# POSTPROCESSORS                                                       #
########################################################################


def set_episodes_series(data: CollectedData) -> CollectedData:
    series = data.get("series")
    if series is not None:
        for episode in data.get("episodes", []):
            episode["series"] = series
    return data


def set_episodes_plot_languages(data: CollectedData) -> CollectedData:
    lang = data.get("_page_lang")
    if lang is not None:
        for episode in data.get("episodes", []):
            plot = episode.get("plot")
            if plot is not None:
                episode["plot"] = {lang: plot}
            else:
                episode["plot"] = {}
    return data


def build_episode_map(data: CollectedData) -> CollectedData:
    episodes = data.get("episodes")
    if episodes is not None:
        data["episodes"] = {ep["episode"]: ep for ep in episodes}
    return data


def update_postprocessors(postprocessors: dict[str, Postprocessor]) -> None:
    postprocessors.update({
        "set_episodes_series": set_episodes_series,
        "set_episodes_plot_languages": set_episodes_plot_languages,
        "build_episode_map": build_episode_map,
    })


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


def flatten_list_of_dicts(value: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert a list of dictionaries to a single dictionary."""
    return {k: v for d in value for k, v in d.items()}


def update_transformers(transformers: dict[str, Transformer]) -> None:
    transformers.update({
        "make_dict": make_dict,
        "date": make_date,
        "unescape": html.unescape,
        "div60": lambda x: x // 60,
        "credit_category": parse_credit_category,
        "credit_job": parse_credit_job,
        "credit_notes": parse_credit_notes,
        "flatten_list_of_dicts": flatten_list_of_dicts,
    })