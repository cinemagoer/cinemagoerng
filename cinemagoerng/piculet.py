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

from typing import Any, Callable, Collection, Mapping, Union

import html
import json
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache

from jmespath import compile as compile_jmespath
from jmespath.parser import ParsedResult as JmesPath
from lxml.etree import XPath, _Element
from lxml.html import fromstring as parse_html


transformers: dict[str, Callable] = {
    "decimal": lambda x: Decimal(str(x)),
    "div60": lambda x: x // 60,
    "json": json.loads,
    "lang": lambda x: {x["lang"]: x["text"]},
    "unescape": html.unescape,
}


make_xpath = lru_cache(maxsize=None)(XPath)
make_jmespath = lru_cache(maxsize=None)(compile_jmespath)


@dataclass(kw_only=True)
class Extractor:
    transform: str | None = None


@dataclass(kw_only=True)
class XPathExtractor(Extractor):
    xpath: str
    joiner: str = ""
    _compiled: XPath = field(init=False)

    def __post_init__(self) -> None:
        self._compiled = make_xpath(self.xpath)

    def apply(self, data: _Element) -> str | None:
        selected: list[str] = self._compiled(data)  # type: ignore
        if len(selected) == 0:
            return None
        return self.joiner.join(selected)


@dataclass(kw_only=True)
class JmesPathExtractor(Extractor):
    jmespath: str
    _compiled: JmesPath = field(init=False)

    def __post_init__(self) -> None:
        self._compiled = make_jmespath(self.jmespath)

    def apply(self, data: Mapping[str, Any]) -> Any:
        return self._compiled.search(data)


@dataclass(kw_only=True)
class MapRule:
    key: str
    extractor: Union[JmesPathExtractor, "MapRulesExtractor"]


@dataclass(kw_only=True)
class MapRulesExtractor(Extractor):
    rules: list[MapRule] = field(default_factory=list)

    def apply(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


@dataclass(kw_only=True)
class TreeRule:
    key: str
    extractor: XPathExtractor
    skip: bool = False
    post_map: list[MapRule] = field(default_factory=list)


def apply_rules(rules: list[TreeRule] | list[MapRule],
                data: Any) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for rule in rules:
        raw = rule.extractor.apply(data)
        if (raw is None) or ((isinstance(raw, Collection) and len(raw) == 0)):
            continue
        if rule.extractor.transform is None:
            value = raw
        else:
            multiple = rule.extractor.transform[-1] == "*"
            transform_key = rule.extractor.transform if not multiple else \
                rule.extractor.transform[:-1]
            transform = transformers.get(transform_key)
            if transform is None:
                raise ValueError("Unknown transformer")
            value = transform(raw) if not multiple else \
                [transform(r) for r in raw]

        match rule:
            case TreeRule():
                if not rule.skip:
                    result[rule.key] = value
                subresult = apply_rules(rule.post_map, value)
                result.update(subresult)
            case MapRule():
                result[rule.key] = value
    return result


@dataclass(kw_only=True)
class Spec:
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def scrape(document: str, /, rules: list[TreeRule]) -> Mapping[str, Any]:
    root = parse_html(document)
    return apply_rules(rules, root)
