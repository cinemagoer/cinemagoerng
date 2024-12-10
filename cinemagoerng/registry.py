# Copyright 2024 H. Turgut Uyar <uyar@tekir.org>
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
    MapNode,
    Postprocessor,
    Preprocessor,
    Transformer,
    TreeNode,
    TreePath,
)


def parse_next_data(root: TreeNode) -> MapNode:
    path = TreePath("//script[@id='__NEXT_DATA__']/text()")
    next_data = path.apply(root)[0]
    return json.loads(next_data)


def remove_see_more(root: TreeNode) -> TreeNode:
    path = TreePath("//a[text()='See more »']")
    links = path.select(root)
    for link in links:
        parent: TreeNode = link.getparent()  # type: ignore
        parent.remove(link)
    return root


def update_preprocessors(registry: dict[str, Preprocessor]) -> None:
    registry.update(
        {
            "parse_next_data": parse_next_data,
            "remove_see_more": remove_see_more,
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


def generate_episode_map(data):
    for season, episodes in data["episodes"].items():
        data["episodes"][season] = {ep["episode"]: ep for ep in episodes}


def set_plot_langs(data):
    episodes = data.get("episodes")
    default_lang = data.get("_page_lang", "en-US")

    if not episodes:
        return

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


def update_postprocessors(registry: dict[str, Postprocessor]) -> None:
    registry.update(
        {
            "unpack_dicts": unpack_dicts,
            "generate_episode_map": generate_episode_map,
            "set_plot_langs": set_plot_langs,
        }
    )


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


def parse_text_date(x: str) -> str | None:
    tokens = x.split("(")[0].split()
    if len(tokens) != 3:
        return None
    day, month_name, year = tokens
    month = _month_nums[month_name]
    return f"{year}-{month:02}-{day}"


def parse_href_id(value: str) -> str:
    if "?" in value:
        value = value.split("?")[0]
    if value[-1] == "/":
        value = value[:-1]
    return value.split("/")[-1]


def parse_type_id(value: str) -> str:
    if value[0] == "(" and value[-1] == ")":
        value = value[1:-1]
    first, *rest = value.strip().split(" ")
    return "".join([first.lower()] + rest)


def parse_year_range(value: str) -> dict[str, int]:
    pattern = re.compile(r"\d{4}")
    year_values = pattern.findall(value)
    if not year_values:
        return {}
    data = {"year": int(year_values[0])}
    if len(year_values) > 1:
        data["end_year"] = int(year_values[1])
    return data


def parse_country_code(value: str) -> str:
    return value.split("/country/")[-1]


def parse_language_code(value: str) -> str:
    return value.split("/language/")[-1]


def parse_runtime(value: str) -> int:
    return int(value.replace(" min", ""))


def parse_vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))  # remove parens around value


def parse_ranking(value: str) -> int:
    return int(value.split("#")[-1])


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
    role: str | None
    notes: list[str]


_re_credit_notes = re.compile(r"""\(([^)]*)\)*""")


def parse_credit_info(value: str) -> CreditInfo:
    value = value.strip()
    parsed: CreditInfo = {"role": None, "notes": []}
    notes: list[str] = _re_credit_notes.findall(value)
    if len(notes) == 0:
        parsed["role"] = value.strip()
    else:
        parsed["notes"] = [note for note in notes if len(note) > 0]
        parens = value.find("(")
        role = value[:parens].strip()
        if len(role) > 0:
            parsed["role"] = role
    return parsed


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
            "date": make_date,
            "text_date": parse_text_date,
            "unescape": html.unescape,
            "div60": lambda x: x // 60,
            "href_id": parse_href_id,
            "type_id": parse_type_id,
            "year_range": parse_year_range,
            "country_code": parse_country_code,
            "language_code": parse_language_code,
            "runtime": parse_runtime,
            "vote_count": parse_vote_count,
            "ranking": parse_ranking,
            "locale": parse_locale,
            "credit_section_id": parse_credit_section_id,
            "credit_info": parse_credit_info,
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
