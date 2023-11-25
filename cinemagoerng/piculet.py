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

from jmespath import compile as compile_jmespath
from lxml.etree import XPath
from lxml.html import fromstring as parse_html


@lru_cache(maxsize=None)
def make_jmespath(path: str, /) -> Callable:
    compiled = compile_jmespath(path)
    return compiled.search


@dataclass
class JmesPathRule:
    jmespath: str
    transform: str | None = None
    apply: Callable = field(init=False)

    def __post_init__(self) -> None:
        self.apply = make_jmespath(self.jmespath)


@dataclass
class PostMapRule:
    key: str
    extractor: JmesPathRule


make_xpath: Callable[[str], XPath] = lru_cache(maxsize=None)(XPath)


@dataclass
class XPathRule:
    xpath: str
    transform: str | None = None
    apply: XPath = field(init=False)

    def __post_init__(self) -> None:
        self.apply = make_xpath(self.xpath)


@dataclass
class Rule:
    key: str
    extractor: XPathRule
    skip: bool = False
    post_map: list[PostMapRule] = field(default_factory=list)


@dataclass
class Spec:
    url: str
    rules: list[Rule] = field(default_factory=list)


def scrape(document: str, /, rules: list[Rule]) -> Mapping[str, Any]:
    root = parse_html(document)
    data: dict[str, Any] = {}
    for rule in rules:
        selected: Sequence[str] = rule.extractor.apply(root)  # type: ignore
        if len(selected) == 0:
            continue
        raw = "".join(selected).strip()
        match rule.extractor.transform:
            case None:
                value = raw
            case "json":
                value = json.loads(raw)
            case _:
                raise ValueError("Unknown transformer")
        if not rule.skip:
            data[rule.key] = value

        for post_rule in rule.post_map:
            post_raw = post_rule.extractor.apply(value)
            if (post_raw is None) or \
                    ((isinstance(post_raw, list) and len(post_raw) == 0)):
                continue
            match post_rule.extractor.transform:
                case None:
                    post_value = post_raw
                case "unescape":
                    post_value = [html.unescape(v) for v in post_raw]
                case "div60":
                    post_value = post_raw // 60
                case "decimal":
                    post_value = Decimal(str(post_raw))
                case "lang":
                    lang_key = f"{post_rule.key}.lang"
                    post_value = {data[lang_key]: post_raw}
                    del data[lang_key]
                case _:
                    raise ValueError("Unknown transformer")
            data[post_rule.key] = post_value
    return data
