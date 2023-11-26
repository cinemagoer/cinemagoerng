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

from typing import Any, Callable, Collection, Mapping, Union

import html
import json
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache, partial

from jmespath import compile as compile_jmespath
from jmespath.parser import ParsedResult as JmesPath
from lxml.etree import XPath, _Element
from lxml.html import fromstring as parse_html

from . import custom_transformers


def parse_range(value: str, name: str) -> dict[str, int]:
    tokens = value.split("-")
    if not tokens[0].isdigit():
        return {}
    data = {name: int(tokens[0])}
    if (len(tokens) > 1) and tokens[1].isdigit():
        data[f"end_{name}"] = int(tokens[1])
    return data


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
    transformer: str | None = None
    transform: Callable | None = field(init=False)

    def __post_init__(self) -> None:
        if self.transformer is None:
            self.transform = None
        else:
            multiple = self.transformer[-1] == "*"
            key = self.transformer if not multiple else self.transformer[:-1]
            if key.startswith("parse:"):
                transform: Callable | None = \
                    getattr(custom_transformers,
                            key.replace("parse:", "parse_"),
                            None)
            elif key.startswith("range:"):
                transform = partial(parse_range, name=key[6:])
            else:
                transform = transformers.get(key)
            if transform is None:
                raise ValueError("Unknown transformer")
            self.transform = transform if not multiple else \
                lambda xs: [transform(x) for x in xs]



@dataclass(kw_only=True)
class XPathExtractor(Extractor):
    xpath: str
    sep: str = ""
    _compiled: XPath = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._compiled = make_xpath(self.xpath)

    def apply(self, data: _Element) -> str | None:
        selected: list[str] = self._compiled(data)  # type: ignore
        if len(selected) == 0:
            return None
        return self.sep.join(selected).strip()


@dataclass(kw_only=True)
class JmesPathExtractor(Extractor):
    jmespath: str
    _compiled: JmesPath = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
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
    post_map: list[MapRule] = field(default_factory=list)


def apply_rules(rules: list[TreeRule] | list[MapRule],
                data: Any) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for rule in rules:
        raw = rule.extractor.apply(data)
        if (raw is None) or ((isinstance(raw, Collection) and len(raw) == 0)):
            continue
        if rule.extractor.transformer is None:
            value = raw
        else:
            value = rule.extractor.transform(raw)

        result[rule.key] = value
        match rule:
            case TreeRule():
                subresult = apply_rules(rule.post_map, value)
                result.update(subresult)
    return result


@dataclass(kw_only=True)
class Spec:
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def scrape(document: str, /, rules: list[TreeRule]) -> Mapping[str, Any]:
    root = parse_html(document)
    data = apply_rules(rules, root)
    return data
