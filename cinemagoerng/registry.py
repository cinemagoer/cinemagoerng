# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
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
from typing import Any, TypedDict

from lxml.etree import Element

from .piculet import Postprocessor, Preprocessor, StrMap, Transformer, TreeNode


def scalar_to_xml(tag: str, data: Any) -> TreeNode:
    element = Element(tag)
    element.text = str(data)
    return element


def list_to_xml(tag: str, data: list[Any]) -> TreeNode:
    element = Element(tag)
    key = "item"
    for value in data:
        match value:
            case None:
                continue
            case dict():
                child = dict_to_xml(key, value)
            case list():
                child = list_to_xml(key, value)
            case _:
                child = scalar_to_xml(key, value)
        element.append(child)
    return element


def dict_to_xml(tag: str, data: StrMap) -> TreeNode:
    element = Element(tag)
    for key, value in data.items():
        match value:
            case None:
                continue
            case dict():
                child = dict_to_xml(key, value)
            case list():
                child = list_to_xml(key, value)
            case _:
                child = scalar_to_xml(key, value)
        element.append(child)
    return element


_data_sections: list[str] = ["aboveTheFoldData", "mainColumnData",
                             "contentData", "translationContext"]


def parse_next_data(root: TreeNode) -> TreeNode:
    next_data_path = "//script[@id='__NEXT_DATA__']/text()"
    script: str = root.xpath(next_data_path)[0]  # type:ignore
    data = json.loads(script)
    xml_data: dict[str, Any] = {}
    for section in _data_sections:
        section_data: StrMap | None = data["props"]["pageProps"].get(section)
        if section_data is not None:
            xml_data[section] = section_data
    return dict_to_xml("NEXT_DATA", xml_data)


def remove_see_more(root: TreeNode) -> TreeNode:
    links = root.xpath("//a[text()='See more »']")
    for link in links:
        link.getparent().remove(link)
    return root


def update_preprocessors(registry: dict[str, Preprocessor]) -> None:
    registry.update({
        "next_data": parse_next_data,
        "see_more": remove_see_more,
    })


def generate_episode_map(data, value):
    for season in data:
        data[season] = {ep["episode"]: ep for ep in data[season]}


def update_postprocessors(registry: dict[str, Postprocessor]) -> None:
    registry.update({
        "episode_map": generate_episode_map,
    })


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


_month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_month_nums = {m: (i + 1) for i, m in enumerate(_month_names)}


def parse_text_date(x: str) -> None:
    tokens = x.split("(")[0].split()
    if len(tokens) != 3:
        return None
    day, month_name, year = tokens
    month = _month_nums[month_name]
    return f"{year}-{month:02}-{day}"


class LangDict(TypedDict):
    lang: str
    text: str


def make_lang(x: LangDict) -> dict[str, str]:
    return {x["lang"]: x["text"]}


def parse_href_id(value: str) -> str:
    if "?" in value:
        value = value.split("?")[0]
    if value[-1] == "/":
        value = value[:-1]
    return value.split("/")[-1]


def parse_type_id(value: str) -> str:
    first, *rest = value.strip().split(" ")
    return "".join([first.lower()] + rest)


def parse_year_range(value: str) -> dict[str, int]:
    tokens = value.strip().split("-")
    data = {"year": int(tokens[0])}
    if (len(tokens) > 1) and len(tokens[1]) > 0:
        data["end_year"] = int(tokens[1])
    return data


def parse_country_code(value: str) -> str:
    return value.split("/country/")[-1]


def parse_language_code(value: str) -> str:
    return value.split("/language/")[-1]


def parse_runtime(value: str) -> int:
    return int(value.replace(" min", ""))


def parse_vote_count(value: str) -> int:
    return int(value[1:-1].replace(",", ""))   # remove parens around value


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


def parse_season_number(value: str) -> str:
    return value.strip().split("Season ")[1]


def parse_episode_number(value: str) -> str:
    return value.strip().split("Episode ")[1]


def update_transformers(registry: dict[str, Transformer]) -> None:
    registry.update({
        "date": make_date,
        "text_date": parse_text_date,
        "lang": make_lang,
        "unescape": html.unescape,
        "div60": lambda x: int(x) // 60,
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
        "season_number": parse_season_number,
        "episode_number": parse_episode_number,
    })
