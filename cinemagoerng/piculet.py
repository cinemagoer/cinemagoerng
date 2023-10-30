# Copyright (C) 2014-2023 H. Turgut Uyar <uyar@tekir.org>
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
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Mapping, MutableMapping, Sequence, TypeAlias

import jmespath
from lxml.etree import XPath
from lxml.html import fromstring as parse_html


xpath: Callable[[str], XPath] = lru_cache(maxsize=None)(XPath)


@dataclass
class Rule:
    path: str
    transform: str | None = None
    post_map: dict[str, str] | None = None


@dataclass
class Spec:
    url: str
    rules: dict[str, Rule]


ParsedData: TypeAlias = str | int | dict | None


def scrape(document: str, /,
           rules: Mapping[str, Rule]) -> MutableMapping[str, ParsedData]:
    root = parse_html(document)
    data: dict[str, ParsedData] = {}
    for key, rule in rules.items():
        extract = xpath(rule.path)
        raw: Sequence[str] = extract(root)  # type: ignore
        if len(raw) == 0:
            continue
        value = "".join(raw).strip()
        match rule.transform:
            case "int":
                data[key] = int(value)
            case "json":
                data[key] = json.loads(value)
            case _:
                data[key] = value

        if rule.post_map is not None:
            for item_key, item_path in rule.post_map.items():
                item_value = jmespath.search(item_path, data[key])
                match item_value:
                    case str():
                        item_value = html.unescape(item_value)
                    case [x, *_] if isinstance(x, str):
                        item_value = [html.unescape(v) for v in item_value]
                if item_value is not None:
                    data[item_key] = item_value

    return data
