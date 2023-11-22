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

from typing import Callable, Mapping, MutableMapping, Sequence, TypeAlias

import html
import json
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache

import jmespath
from lxml.etree import XPath
from lxml.html import fromstring as parse_html


xpath: Callable[[str], XPath] = lru_cache(maxsize=None)(XPath)


@dataclass
class DictRule:
    path: str
    transform: str | None = None


@dataclass
class Rule:
    path: str
    transform: str | None = None
    post_map: dict[str, DictRule] | None = None


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
            case "json":
                value = json.loads(value)
        if key[:2] != "__":
            data[key] = value

        if rule.post_map is not None:
            for post_key, post_rule in rule.post_map.items():
                post_value = jmespath.search(post_rule.path, value)
                if post_value is None:
                    continue
                match post_rule.transform:
                    case "unescape":
                        post_value = [html.unescape(v) for v in post_value]
                    case "div60":
                        post_value = post_value // 60
                    case "decimal":
                        post_value = Decimal(str(post_value))
                    case "lang":
                        lang_key = f"{post_key}.lang"
                        post_value = {data[lang_key]: post_value}
                        del data[lang_key]
                data[post_key] = post_value

    return data
