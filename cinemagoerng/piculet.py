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

from typing import Any, Callable, Mapping, Sequence

import html
import json
from dataclasses import dataclass, field
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
    post_map: dict[str, DictRule] = field(default_factory=dict)
    skip: bool = False


@dataclass
class Spec:
    url: str
    rules: dict[str, Rule] = field(default_factory=dict)


def scrape(document: str, /, rules: Mapping[str, Rule]) -> Mapping[str, Any]:
    root = parse_html(document)
    data: dict[str, Any] = {}
    for key, rule in rules.items():
        extract = xpath(rule.path)
        raw: Sequence[str] = extract(root)  # type: ignore
        if len(raw) == 0:
            continue
        value = "".join(raw).strip()
        match rule.transform:
            case "json":
                value = json.loads(value)
        if not rule.skip:
            data[key] = value

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
