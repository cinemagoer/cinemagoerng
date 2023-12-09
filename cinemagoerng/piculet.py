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

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from types import MappingProxyType
from typing import Any, Collection, List, Mapping, TypeAlias

import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element as Node
from lxml.html import fromstring as parse_html


StrMap: TypeAlias = Mapping[str, Any]


_EMPTY: StrMap = MappingProxyType({})


transformer_registry: dict[str, Callable] = {
    "decimal": lambda x: Decimal(str(x)),
    "int": int,
    "json": json.loads,
    "lower": str.lower,
}


class XPath:
    def __init__(self, path: str) -> None:
        self.path = path
        self.__compiled = compile_xpath(path)

    def __str__(self) -> str:
        return self.path

    def apply(self, root: Node) -> list[str]:
        return self.__compiled(root)  # type: ignore

    def select(self, root: Node) -> list[Node]:
        return self.__compiled(root)  # type: ignore


class JmesPath:
    def __init__(self, path: str) -> None:
        self.path = path
        self.__compiled = compile_jmespath(path)

    def __str__(self) -> str:
        return self.path

    def apply(self, root: StrMap) -> Any:
        return self.__compiled.search(root)

    def select(self, root: StrMap) -> list[StrMap]:
        return self.__compiled.search(root)


class Transform:
    def __init__(self, name: str) -> None:
        self.name = name
        multiple = name[-1] == "*"
        key = name if not multiple else name[:-1]
        transform = transformer_registry[key]
        if not multiple:
            self.__transform = transform
        else:
            self.__transform = lambda xs: [transform(x) for x in xs]

    def __str__(self) -> str:
        return self.name

    def __call__(self, data: Any) -> Any:
        return self.__transform(data)


@dataclass(kw_only=True)
class TreeExtractor:
    path: XPath
    sep: str = ""
    transform: Transform | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: XPath | None = None

    def extract(self, root: Node) -> str | StrMap:
        value = self.path.apply(root)
        if len(value) == 0:
            return _EMPTY
        return self.sep.join(value).strip()


@dataclass(kw_only=True)
class MapExtractor:
    path: JmesPath
    transform: Transform | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: JmesPath | None = None

    def extract(self, root: StrMap) -> Any:
        value = self.path.apply(root)
        if (value is None) or \
                ((isinstance(value, Collection) and len(value) == 0)):
            return _EMPTY
        return value


@dataclass(kw_only=True)
class TreeRulesExtractor:
    rules: List["TreeRule"] = field(default_factory=list)
    transform: Transform | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: XPath | None = None

    def extract(self, root: Node) -> StrMap:
        return apply_rules(self.rules, root)


@dataclass(kw_only=True)
class MapRulesExtractor:
    rules: List["MapRule"] = field(default_factory=list)
    transform: Transform | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: JmesPath | None = None

    def extract(self, root: StrMap) -> StrMap:
        return apply_rules(self.rules, root)


@dataclass(kw_only=True)
class TreeRule:
    key: str | TreeExtractor
    extractor: TreeExtractor | TreeRulesExtractor
    foreach: XPath | None = None


@dataclass(kw_only=True)
class MapRule:
    key: str | MapExtractor
    extractor: MapExtractor | MapRulesExtractor
    foreach: JmesPath | None = None


def apply_rule(rule: TreeRule | MapRule, root: Node | StrMap) -> StrMap:
    data: dict[str, Any] = {}
    subroots = [root] if rule.foreach is None else rule.foreach.select(root)
    for subroot in subroots:
        if rule.extractor.foreach is None:
            raw = rule.extractor.extract(subroot)
            if raw is _EMPTY:
                continue
        else:
            raws = [rule.extractor.extract(node)  # type: ignore
                    for node in rule.extractor.foreach.select(subroot) or []]
            raw = [v for v in raws if v is not _EMPTY]
            if len(raw) == 0:
                continue

        value = raw if rule.extractor.transform is None else \
            rule.extractor.transform(raw)

        match rule.key:
            case str():
                key = rule.key
            case TreeExtractor() | MapExtractor():
                raw_key = rule.key.extract(subroot)
                key = raw_key if rule.key.transform is None else \
                    rule.key.transform(raw_key)
        if key[0] != "_":
            data[key] = value

        if len(rule.extractor.post_map) > 0:
            subresult = apply_rules(rule.extractor.post_map, value)
            if len(subresult) > 0:
                data.update(subresult)
    return data if len(data) > 0 else _EMPTY


def apply_rules(rules: list[TreeRule] | list[MapRule],
                root: Node | StrMap) -> StrMap:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = apply_rule(rule, root)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def scrape(document: str, /, rules: list[TreeRule]) -> StrMap:
    root = parse_html(document)
    return apply_rules(rules, root)


@dataclass(kw_only=True)
class Spec:
    version: str
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def load_spec(document: dict, /) -> Spec:
    return typedload.load(document, Spec, pep563=True,
                          strconstructed={XPath, JmesPath, Transform},
                          failonextra=True, basiccast=False)


def dump_spec(spec: Spec, /) -> str:
    return typedload.dump(spec, strconstructed={XPath, JmesPath, Transform})


deserialize = partial(typedload.load, strconstructed={Decimal}, pep563=True,
                      basiccast=False)
serialize = partial(typedload.dump, strconstructed={Decimal})
