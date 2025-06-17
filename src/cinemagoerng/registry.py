# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

import html
import json
import re
from typing import Any, TypedDict

from .piculet import (
    JSONNode,
    Postprocessor,
    Preprocessor,
    Transformer,
    XMLNode,
    XMLPath,
)


def parse_next_data(root: XMLNode) -> JSONNode:
    path = XMLPath("//script[@id='__NEXT_DATA__']/text()")
    next_data = path.apply(root)[0]
    return json.loads(next_data)


def update_preprocessors(registry: dict[str, Preprocessor]) -> None:
    registry.update(
        {
            "parse_next_data": parse_next_data,
        }
    )


def unpack_dicts(data):
    for child in data.values():
        if isinstance(child, dict):
            unpack_dicts(child)
        if isinstance(child, list):
            for subchild in child:
                if isinstance(subchild, dict):
                    unpack_dicts(subchild)
    collected = data.get("__dict__")
    if collected is not None:
        data.update(collected)
        del data["__dict__"]
    return data


def generate_episode_map(data):
    for season, episodes in data["episodes"].items():
        data["episodes"][season] = {ep["episode"]: ep for ep in episodes}
    return data


def set_plot_langs(data):
    episodes = data.get("episodes")
    default_lang = data.get("_page_lang", "en-US")

    if not episodes:
        return data

    # Flatten episodes if it's a dictionary of seasons
    if not isinstance(episodes, list):
        episodes = [
            episode
            for season in episodes.values()
            for episode in season.values()
        ]

    # Update plot language for each episode
    for episode in episodes:
        if "_plot" in episode:
            episode["plot"] = {default_lang: episode["_plot"]}
    return data


def update_postprocessors(registry: dict[str, Postprocessor]) -> None:
    registry.update(
        {
            "generate_episode_map": generate_episode_map,
            "set_plot_langs": set_plot_langs,
            "unpack_dicts": unpack_dicts,
        }
    )


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


def make_date(x: DateDict) -> str | None:
    year = x.get("year")
    month = x.get("month")
    day = x.get("day")
    if (year is None) or (month is None) or (day is None):
        return None
    return f"{year}-{month:02}-{day:02}"


_month_names = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
_month_nums = {m: (i + 1) for i, m in enumerate(_month_names)}


_CREDIT_CATEGORIES = {
    "director": "directors",
}


def parse_credit_category(value: str) -> str:
    return _CREDIT_CATEGORIES.get(value, value)


class CreditNotes(TypedDict):
    imdb_id: str
    name: str
    roles: list[str]
    notes: list[str]


_re_credit_notes = re.compile(r"""\(([^)]*)\)*""")


def parse_credit_notes(value: CreditNotes) -> CreditNotes:
    if "roles" not in value:
        value["roles"] = []
    if "notes" not in value:
        value["notes"] = []
    roles: list[str] = []
    notes: list[str] = []
    for note in value["notes"]:
        subnotes: list[str] = _re_credit_notes.findall(note)
        if len(subnotes) == 0:
            roles.append(note)
        else:
            notes.extend(subnotes)
        parens = note.find("(")
        role = note[:parens].strip()
        if len(role) > 0:
            roles.append(role)
    value["roles"].extend(roles)
    value["notes"].extend(notes)
    return value


def parse_text_date(x: str) -> str | None:
    tokens = x.split("(")[0].split()
    if len(tokens) != 3:
        return None
    day, month_name, year = tokens
    month = _month_nums[month_name]
    return f"{year}-{month:02}-{day}"


def parse_episode_series_title(value: str) -> str | None:
    if value[0] != '"':
        return None
    return value.split('"')[1]


def parse_episode_count(value: str) -> int:
    return int(value[:-1].split("(")[1])


def parse_season_number(value: str) -> str:
    return value.strip().split("Season ")[1]


def parse_episode_number(value: str) -> str:
    return value.strip().split("Episode ")[1]


def exists(value: str) -> bool:
    return value is not None and value != ""


def extract_value(value: dict) -> str:
    return value.get("value")


def flatten_list_of_dicts(value: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert a list of dictionaries to a single dictionary."""
    return {k: v for d in value for k, v in d.items()}


def build_episode_graphql_url(url_data: dict[str, Any]) -> str:
    url = url_data["url"]
    params = url_data["params"]
    variables: dict[str, Any] = {
        "after": params["after"].replace('"', ""),
        "const": params["imdb_id"],
        "first": 50,
        "locale": "en-US",
        "originalTitleText": False,
        "returnUrl": "https://www.imdb.com/close_me",
        "sort": {"by": "EPISODE_THEN_RELEASE", "order": "ASC"},
    }

    if params["filter_type"] == "year":
        variables["filter"] = {
            "releasedOnOrAfter": {"year": params["start_year"]},
            "releasedOnOrBefore": {"year": params["end_year"]},
        }
    elif params["filter_type"] == "season":
        variables["filter"] = {"includeSeasons": [params["season"]]}

    extensions = {
        "persistedQuery": {
            "sha256Hash": "e5b755e1254e3bc3a36b34aff729b1d107a63263dec628a8f59935c9e778c70e",  # noqa: E501
            "version": 1,
        }
    }

    # Properly escape the JSON for GraphQL
    variables_json = json.dumps(variables, separators=(",", ":"))
    extensions_json = json.dumps(extensions, separators=(",", ":"))

    return url % {"variables": variables_json, "extensions": extensions_json}


def update_transformers(registry: dict[str, Transformer]) -> None:
    registry.update(
        {
            "make_dict": make_dict,
            "date": make_date,
            "credit_category": parse_credit_category,
            "credit_notes": parse_credit_notes,
            "text_date": parse_text_date,
            "unescape": html.unescape,
            "div60": lambda x: x // 60,
            "split&": lambda s: s.split(" & "),
            "episode_series_title": parse_episode_series_title,
            "episode_count": parse_episode_count,
            "season_number": parse_season_number,
            "episode_number": parse_episode_number,
            "exists": exists,
            "extract_value": extract_value,
            "flatten_list_of_dicts": flatten_list_of_dicts,
            "build_episode_graphql_url": build_episode_graphql_url,
        }
    )
