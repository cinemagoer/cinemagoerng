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

from typing import Any, Callable, Collection, List, Mapping

import json
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache, partial
from pathlib import Path
from types import MappingProxyType

import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element
from lxml.html import fromstring as parse_html

from .transformers import transformer_registry


_EMPTY: Mapping = MappingProxyType({})


make_xpath = lru_cache(maxsize=None)(compile_xpath)


class XPath:
    def __init__(self, path: str) -> None:
        self.path = path
        self.__compiled = make_xpath(path)

    def __str__(self) -> str:
        return self.path

    def __call__(self, data: _Element) -> list[str] | list[_Element]:
        return self.__compiled(data)  # type: ignore


make_jmespath = lru_cache(maxsize=None)(compile_jmespath)


class JmesPath:
    def __init__(self, path: str) -> None:
        self.path = path
        self.__compiled = make_jmespath(path)

    def __str__(self) -> str:
        return self.path

    def __call__(self, data: Mapping[str, Any]) -> Any:
        return self.__compiled.search(data)


@lru_cache(maxsize=None)
def make_transform(name: str) -> Callable:
    multiple = name[-1] == "*"
    key = name if not multiple else name[:-1]
    transform = transformer_registry[key]
    if not multiple:
        return transform
    else:
        return partial(map, transform)


class Transform:
    def __init__(self, name: str) -> None:
        self.name = name
        self.__do = make_transform(name)

    def __str__(self) -> str:
        return self.name

    def __call__(self, data: Any) -> Any:
        return self.__do(data)


@dataclass(kw_only=True)
class XPathExtractor:
    xpath: XPath
    sep: str = ""
    transform: Transform | None = None
    foreach: XPath | None = None

    def __call__(self, data: _Element) -> str | Mapping:
        selected: list[str] = self.xpath(data)  # type: ignore
        if len(selected) == 0:
            return _EMPTY
        return self.sep.join(selected).strip()


@dataclass(kw_only=True)
class JmesPathExtractor:
    jmespath: JmesPath
    transform: Transform | None = None
    foreach: JmesPath | None = None

    def __call__(self, data: Mapping[str, Any]) -> Any:
        selected = self.jmespath(data)
        if (selected is None) or \
                ((isinstance(selected, Collection) and len(selected) == 0)):
            return _EMPTY
        return selected


@dataclass(kw_only=True)
class MapRulesExtractor:
    rules: List["MapRule"] = field(default_factory=list)
    transform: Transform | None = None
    foreach: None = None

    def __call__(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


@dataclass(kw_only=True)
class MapRule:
    key: str
    extractor: JmesPathExtractor | MapRulesExtractor
    post_map: List["MapRule"] = field(default_factory=list)


@dataclass(kw_only=True)
class TreeRule:
    key: str
    extractor: XPathExtractor
    post_map: List["MapRule"] = field(default_factory=list)


@dataclass(kw_only=True)
class Spec:
    url: str
    rules: list[TreeRule] = field(default_factory=list)


@lru_cache(maxsize=None)
def load_spec(path: Path, /) -> Spec:
    content = path.read_text(encoding="utf-8")
    return typedload.load(json.loads(content), Spec, pep563=True,
                          strconstructed={XPath, JmesPath, Transform})


def apply_rules(rules: list[TreeRule] | list[MapRule],
                data: Any) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for rule in rules:
        if rule.extractor.foreach is None:
            raw = rule.extractor(data)
            if raw is _EMPTY:
                continue
        else:
            raw_ = [rule.extractor(r) for r in rule.extractor.foreach(data)]
            raw = [v for v in raw_ if v is not _EMPTY]
            if len(raw) == 0:
                continue
        if rule.extractor.transform is None:
            value = raw
        else:
            value = rule.extractor.transform(raw)
        result[rule.key] = value

        if len(rule.post_map) > 0:
            subresult = apply_rules(rule.post_map, value)
            if subresult is not _EMPTY:
                result.update(subresult)
    if len(result) == 0:
        return _EMPTY
    return result


def scrape(document: str, /, rules: list[TreeRule]) -> Mapping[str, Any]:
    root = parse_html(document)
    data = apply_rules(rules, root)
    return data


deserialize = partial(typedload.load, strconstructed={Decimal})
serialize = partial(typedload.dump, strconstructed={Decimal})
