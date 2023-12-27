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
    "lower": str.lower,
    "strip": str.strip,
}


class Transformer:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Callable = transformer_registry[name]

    def __str__(self) -> str:
        return self.name


class TreePath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        compiled = compile_xpath(path)
        self.apply: Callable[[Node], list[str]] = compiled  # type: ignore
        self.select: Callable[[Node], list[Node]] = compiled  # type: ignore

    def __str__(self) -> str:
        return self.path


class MapPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        compiled = compile_jmespath(path).search
        self.apply: Callable[[StrMap], Any] = compiled
        self.select: Callable[[StrMap], list[StrMap]] = compiled

    def __str__(self) -> str:
        return self.path


@dataclass(kw_only=True)
class TreePicker:
    path: TreePath
    sep: str = ""
    transform: Transformer | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: TreePath | None = None

    def extract(self, root: Node) -> str | StrMap:
        value = self.path.apply(root)
        if len(value) == 0:
            return _EMPTY
        return self.sep.join(value)


@dataclass(kw_only=True)
class MapPicker:
    path: MapPath
    transform: Transformer | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: MapPath | None = None

    def extract(self, root: StrMap) -> Any:
        value = self.path.apply(root)
        if (value is None) or \
                ((isinstance(value, Collection) and len(value) == 0)):
            return _EMPTY
        return value


@dataclass(kw_only=True)
class TreeCollector:
    rules: List["TreeRule"] = field(default_factory=list)
    transform: Transformer | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: TreePath | None = None

    def extract(self, root: Node) -> StrMap:
        return scrape_tree(root, self.rules)


@dataclass(kw_only=True)
class MapCollector:
    rules: List["MapRule"] = field(default_factory=list)
    transform: Transformer | None = None
    post_map: List["MapRule"] = field(default_factory=list)
    foreach: MapPath | None = None

    def extract(self, root: StrMap) -> StrMap:
        return scrape_map(root, self.rules)


@dataclass(kw_only=True)
class TreeRule:
    key: str | TreePicker
    extractor: TreePicker | TreeCollector
    foreach: TreePath | None = None


@dataclass(kw_only=True)
class MapRule:
    key: str | MapPicker
    extractor: MapPicker | MapCollector
    foreach: MapPath | None = None


def extract_tree(root: Node, rule: TreeRule) -> StrMap:
    data: dict[str, Any] = {}
    subroots = [root] if rule.foreach is None else rule.foreach.select(root)
    for subroot in subroots:
        if rule.extractor.foreach is None:
            raw = rule.extractor.extract(subroot)
            if raw is _EMPTY:
                continue
            value = raw if rule.extractor.transform is None else \
                rule.extractor.transform.apply(raw)
        else:
            raws = [rule.extractor.extract(node)
                    for node in rule.extractor.foreach.select(subroot) or []]
            raws = [v for v in raws if v is not _EMPTY]
            if len(raws) == 0:
                continue
            value = raws if rule.extractor.transform is None else \
                [rule.extractor.transform.apply(r) for r in raws]

        match rule.key:
            case str():
                key = rule.key
            case TreePicker():
                raw_key = rule.key.extract(subroot)
                key = raw_key if rule.key.transform is None else \
                    rule.key.transform.apply(raw_key)
        if key[0] != "_":
            data[key] = value

        if len(rule.extractor.post_map) > 0:
            subresult = scrape_map(value, rule.extractor.post_map)
            if len(subresult) > 0:
                data.update(subresult)
    return data if len(data) > 0 else _EMPTY


def extract_map(root: StrMap, rule: MapRule) -> StrMap:
    data: dict[str, Any] = {}
    subroots = [root] if rule.foreach is None else rule.foreach.select(root)
    for subroot in subroots:
        if rule.extractor.foreach is None:
            raw = rule.extractor.extract(subroot)
            if raw is _EMPTY:
                continue
            value = raw if rule.extractor.transform is None else \
                rule.extractor.transform.apply(raw)
        else:
            raws = [rule.extractor.extract(node)
                    for node in rule.extractor.foreach.select(subroot) or []]
            raws = [v for v in raws if v is not _EMPTY]
            if len(raws) == 0:
                continue
            value = raws if rule.extractor.transform is None else \
                [rule.extractor.transform.apply(r) for r in raws]

        match rule.key:
            case str():
                key = rule.key
            case MapPicker():
                raw_key = rule.key.extract(subroot)
                key = raw_key if rule.key.transform is None else \
                    rule.key.transform.apply(raw_key)
        if key[0] != "_":
            data[key] = value

        if len(rule.extractor.post_map) > 0:
            subresult = scrape_map(value, rule.extractor.post_map)
            if len(subresult) > 0:
                data.update(subresult)
    return data if len(data) > 0 else _EMPTY


def scrape_tree(root: Node, rules: list[TreeRule]) -> StrMap:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract_tree(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def scrape_map(root: StrMap, rules: list[MapRule]) -> StrMap:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract_map(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def scrape(document: str, /, rules: list[TreeRule]) -> StrMap:
    root = parse_html(document)
    return scrape_tree(root, rules)


@dataclass(kw_only=True)
class Spec:
    version: str
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def load_spec(document: dict, /) -> Spec:
    return typedload.load(document, Spec, pep563=True,
                          strconstructed={TreePath, MapPath, Transformer},
                          failonextra=True, basiccast=False)


def dump_spec(spec: Spec, /) -> str:
    return typedload.dump(spec,
                          strconstructed={TreePath, MapPath, Transformer})


deserialize = partial(typedload.load, strconstructed={Decimal}, pep563=True,
                      basiccast=False)
serialize = partial(typedload.dump, strconstructed={Decimal})
