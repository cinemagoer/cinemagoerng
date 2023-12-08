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

from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache, partial
from types import MappingProxyType

import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element as Node
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

    def __call__(self, node: Node) -> list[str] | list[Node]:
        return self.__compiled(node)  # type: ignore


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
        self.__transform = make_transform(name)

    def __str__(self) -> str:
        return self.name

    def __call__(self, data: Any) -> Any:
        return self.__transform(data)


@dataclass(kw_only=True)
class Extractor:
    transform: Transform | None = None
    post_map: List["MapRule"] = field(default_factory=list)


@dataclass(kw_only=True)
class XPathExtractor(Extractor):
    path: XPath
    sep: str = ""
    foreach: XPath | None = None

    def __call__(self, data: Node) -> str | Mapping:
        selected: list[str] = self.path(data)  # type: ignore
        if len(selected) == 0:
            return _EMPTY
        return self.sep.join(selected).strip()


@dataclass(kw_only=True)
class JmesPathExtractor(Extractor):
    path: JmesPath
    foreach: JmesPath | None = None

    def __call__(self, data: Mapping[str, Any]) -> Any:
        selected = self.path(data)
        if (selected is None) or \
                ((isinstance(selected, Collection) and len(selected) == 0)):
            return _EMPTY
        return selected


@dataclass(kw_only=True)
class TreeRulesExtractor(Extractor):
    rules: List["TreeRule"] = field(default_factory=list)
    foreach: XPath | None = None

    def __call__(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


@dataclass(kw_only=True)
class MapRulesExtractor(Extractor):
    rules: List["MapRule"] = field(default_factory=list)
    foreach: JmesPath | None = None

    def __call__(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


@dataclass(kw_only=True)
class TreeRule:
    key: str
    extractor: XPathExtractor | TreeRulesExtractor


@dataclass(kw_only=True)
class MapRule:
    key: str
    extractor: JmesPathExtractor | MapRulesExtractor


@dataclass(kw_only=True)
class Spec:
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def load_spec(document: dict, /) -> Spec:
    return typedload.load(document, Spec, pep563=True,
                          strconstructed={XPath, JmesPath, Transform})


def dump_spec(spec: Spec, /) -> str:
    return typedload.dump(spec, strconstructed={XPath, JmesPath, Transform})


def apply_rules(rules: list[TreeRule] | list[MapRule],
                data: Any) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for rule in rules:
        if rule.extractor.foreach is None:
            raw = rule.extractor(data)
            if raw is _EMPTY:
                continue
        else:
            raws = [rule.extractor(d)  # type: ignore
                    for d in rule.extractor.foreach(data) or []]
            raw = [v for v in raws if v is not _EMPTY]
            if len(raw) == 0:
                continue
        if rule.extractor.transform is None:
            value = raw
        else:
            value = rule.extractor.transform(raw)
            if isinstance(value, map):
                value = list(value)
        result[rule.key] = value

        if len(rule.extractor.post_map) > 0:
            subresult = apply_rules(rule.extractor.post_map, value)
            if subresult is not _EMPTY:
                result.update(subresult)
    if len(result) == 0:
        return _EMPTY
    return result


def scrape(document: str, /, rules: list[TreeRule]) -> Mapping[str, Any]:
    root = parse_html(document)
    return apply_rules(rules, root)


deserialize = partial(typedload.load, strconstructed={Decimal})
serialize = partial(typedload.dump, strconstructed={Decimal})
