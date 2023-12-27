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
from typing import Any, List, Mapping, TypeAlias

import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element as TreeNode
from lxml.html import fromstring as parse_html


MapNode: TypeAlias = Mapping[str, Any]


_EMPTY: MapNode = MappingProxyType({})


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
        self._compiled = compile_xpath(path)

    def __str__(self) -> str:
        return self.path

    def apply(self, root: TreeNode) -> list[str]:
        return self._compiled(root)  # type: ignore

    def select(self, root: TreeNode) -> list[TreeNode]:
        return self._compiled(root)  # type: ignore


class MapPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_jmespath(path).search

    def __str__(self) -> str:
        return self.path

    def apply(self, root: MapNode) -> Any:
        return self._compiled(root)

    def select(self, root: MapNode) -> list[MapNode]:
        selected = self._compiled(root)
        return selected if selected is not None else []


@dataclass(kw_only=True)
class Extractor:
    transform: Transformer | None = None
    post_map: List["MapRule"] = field(default_factory=list)


@dataclass(kw_only=True)
class TreePicker(Extractor):
    path: TreePath
    sep: str = ""
    foreach: TreePath | None = None

    def extract(self, root: TreeNode) -> str | None:
        selected = self.path.apply(root)
        return self.sep.join(selected) if len(selected) > 0 else None


@dataclass(kw_only=True)
class MapPicker(Extractor):
    path: MapPath
    foreach: MapPath | None = None

    def extract(self, root: MapNode) -> Any:
        return self.path.apply(root)


@dataclass(kw_only=True)
class TreeCollector(Extractor):
    rules: List["TreeRule"] = field(default_factory=list)
    foreach: TreePath | None = None

    def extract(self, root: TreeNode) -> MapNode:
        return collect(root, self.rules)


@dataclass(kw_only=True)
class MapCollector(Extractor):
    rules: List["MapRule"] = field(default_factory=list)
    foreach: MapPath | None = None

    def extract(self, root: MapNode) -> MapNode:
        return collect(root, self.rules)


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


def extract(root: TreeNode | MapNode, rule: TreeRule | MapRule) -> MapNode:
    data: dict[str, Any] = {}

    if rule.foreach is None:
        subroots = [root]
    else:
        subroots = rule.foreach.select(root)  # type: ignore

    for subroot in subroots:
        if rule.extractor.foreach is None:
            nodes = [subroot]
        else:
            nodes = rule.extractor.foreach.select(subroot)  # type: ignore

        raws = [rule.extractor.extract(n) for n in nodes]  # type: ignore
        raws = [v for v in raws if (v is not _EMPTY) and (v is not None)]
        if len(raws) == 0:
            continue
        values = raws if rule.extractor.transform is None else \
            [rule.extractor.transform.apply(r) for r in raws]
        value = values[0] if rule.extractor.foreach is None else values

        match rule.key:
            case str():
                key = rule.key
            case TreePicker() | MapPicker():
                raw_key = rule.key.extract(subroot)  # type: ignore
                key = raw_key if rule.key.transform is None else \
                    rule.key.transform.apply(raw_key)
        if key[0] != "_":
            data[key] = value

        if len(rule.extractor.post_map) > 0:
            subresult = collect(value, rule.extractor.post_map)  # type: ignore
            if len(subresult) > 0:
                data.update(subresult)
    return data if len(data) > 0 else _EMPTY


def collect(root: TreeNode | MapNode,
            rules: list[TreeRule] | list[MapRule]) -> MapNode:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def scrape(document: str, rules: list[TreeRule]) -> MapNode:
    root = parse_html(document)
    return collect(root, rules)


@dataclass(kw_only=True)
class Spec:
    version: str
    url: str
    rules: list[TreeRule] = field(default_factory=list)


_spec_classes = {TreePath, MapPath, Transformer}


def load_spec(document: dict, /) -> Spec:
    return typedload.load(document, Spec, strconstructed=_spec_classes,
                          pep563=True, failonextra=True, basiccast=False)


def dump_spec(spec: Spec, /) -> str:
    return typedload.dump(spec, strconstructed=_spec_classes)


_data_classes = {Decimal}


deserialize = partial(typedload.load, strconstructed=_data_classes,
                      pep563=True, basiccast=False)
serialize = partial(typedload.dump, strconstructed=_data_classes)
