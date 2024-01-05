# Copyright (C) 2014-2024 H. Turgut Uyar <uyar@tekir.org>
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
from typing import Any, List, Mapping, MutableMapping, TypeAlias

import typedload
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element as TreeNode
from lxml.html import fromstring as parse_html


StrMap: TypeAlias = Mapping[str, Any]
MutableStrMap: TypeAlias = MutableMapping[str, Any]


_EMPTY: StrMap = MappingProxyType({})


Preprocessor: TypeAlias = Callable[[TreeNode], TreeNode]

preprocessors: dict[str, Preprocessor] = {}


class Preprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Preprocessor = preprocessors[name]

    def __str__(self) -> str:
        return self.name


Postprocessor: TypeAlias = Callable[[MutableStrMap, Any], None]

postprocessors: dict[str, Postprocessor] = {
    "unpack": lambda data, value: data.update(value),
}


class Postprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Postprocessor = postprocessors[name]

    def __str__(self) -> str:
        return self.name


Transformer: TypeAlias = Callable[[Any], Any]

transformers: dict[str, Transformer] = {
    "decimal": lambda x: Decimal(str(x)),
    "int": int,
    "lower": str.lower,
    "strip": str.strip,
}


class Transform:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Transformer = transformers[name]

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


@dataclass(kw_only=True)
class Extractor:
    pre: Preprocess | None = None
    transform: Transform | None = None
    post: Postprocess | None = None


@dataclass(kw_only=True)
class TreePicker(Extractor):
    path: TreePath
    sep: str = ""
    foreach: TreePath | None = None

    def extract(self, root: TreeNode) -> str | None:
        selected = self.path.apply(root)
        return self.sep.join(selected) if len(selected) > 0 else None


@dataclass(kw_only=True)
class TreeCollector(Extractor):
    rules: List["TreeRule"] = field(default_factory=list)
    foreach: TreePath | None = None

    def extract(self, root: TreeNode) -> StrMap:
        return collect(root, self.rules)


@dataclass(kw_only=True)
class TreeRule:
    key: str | TreePicker
    extractor: TreePicker | TreeCollector
    foreach: TreePath | None = None

    def extract(self, root: TreeNode) -> StrMap:
        data: dict[str, Any] = {}

        if self.foreach is None:
            subroots = [root]
        else:
            subroots = self.foreach.select(root)

        for subroot in subroots:
            if self.extractor.foreach is None:
                nodes = [subroot]
            else:
                nodes = self.extractor.foreach.select(subroot)

            raws = [self.extractor.extract(n) for n in nodes]
            raws = [v for v in raws if (v is not _EMPTY) and (v is not None)]
            if len(raws) == 0:
                continue
            values = raws if self.extractor.transform is None else \
                [self.extractor.transform.apply(r) for r in raws]
            value = values[0] if self.extractor.foreach is None else values

            match self.key:
                case str():
                    key = self.key
                case TreePicker():
                    raw_key = self.key.extract(subroot)
                    key = raw_key if self.key.transform is None else \
                        self.key.transform.apply(raw_key)
            if key[0] != "_":
                data[key] = value
            if self.extractor.post is not None:
                self.extractor.post.apply(data, value)
        return data if len(data) > 0 else _EMPTY


def collect(root: TreeNode, rules: list[TreeRule]) -> StrMap:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = rule.extract(root)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def scrape(document: str, rules: list[TreeRule]) -> StrMap:
    root = parse_html(document)
    preprocessors = dict.fromkeys(rule.extractor.pre.apply
                                  for rule in rules
                                  if rule.extractor.pre is not None)
    for preprocess in preprocessors:
        root = preprocess(root)
    return collect(root, rules)


@dataclass(kw_only=True)
class Spec:
    version: str
    url: str
    rules: list[TreeRule] = field(default_factory=list)


_spec_classes = {TreePath, Preprocess, Postprocess, Transform}

load_spec = partial(typedload.load, type_=Spec, strconstructed=_spec_classes,
                    pep563=True, failonextra=True, basiccast=False)
dump_spec = partial(typedload.dump, strconstructed=_spec_classes)


_data_classes = {Decimal}

deserialize = partial(typedload.load, strconstructed=_data_classes,
                      pep563=True, basiccast=False)
serialize = partial(typedload.dump, strconstructed=_data_classes)
