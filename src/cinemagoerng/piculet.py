# Copyright (C) 2014-2025 H. Turgut Uyar <uyar@tekir.org>
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

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from types import MappingProxyType
from typing import Any, Literal, Mapping, TypeAlias

import lxml.etree
import lxml.html
import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath


XMLNode: TypeAlias = lxml.etree._Element
JSONNode: TypeAlias = Mapping[str, Any]


DocType: TypeAlias = Literal["html", "xml", "json"]

_PARSERS: dict[DocType, Callable[[str], XMLNode | JSONNode]] = {
    "html": lxml.html.fromstring,
    "xml": lxml.etree.fromstring,
    "json": json.loads,
}


CollectedData: TypeAlias = Mapping[str, Any]

_EMPTY: CollectedData = MappingProxyType({})


Preprocessor: TypeAlias = Callable[[XMLNode | JSONNode], XMLNode | JSONNode]

preprocessors: dict[str, Preprocessor] = {}


class Preprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Preprocessor = preprocessors[name]

    def __str__(self) -> str:
        return self.name


Postprocessor: TypeAlias = Callable[[CollectedData], CollectedData]

postprocessors: dict[str, Postprocessor] = {}


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
    "str": str,
    "strip": str.strip,
}


class Transform:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Transformer = transformers[name]

    def __str__(self) -> str:
        return self.name


class XMLPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_xpath(path)

    def __str__(self) -> str:
        return self.path

    def apply(self, root: XMLNode) -> list[str]:
        return self._compiled(root)  # type: ignore

    def select(self, root: XMLNode) -> list[XMLNode]:
        return self._compiled(root)  # type: ignore


class JSONPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_jmespath(path).search

    def __str__(self) -> str:
        return self.path

    def apply(self, root: JSONNode) -> Any:
        return self._compiled(root)  # type: ignore

    def select(self, root: JSONNode) -> list[JSONNode]:
        selected = self._compiled(root)
        return selected if selected is not None else []  # type: ignore


@dataclass(kw_only=True)
class XMLPicker:
    path: XMLPath
    sep: str = ""
    transforms: list[Transform] = field(default_factory=list)
    foreach: XMLPath | None = None

    def extract(self, root: XMLNode) -> str | None:
        selected = self.path.apply(root)
        return self.sep.join(selected) if len(selected) > 0 else None


@dataclass(kw_only=True)
class JSONPicker:
    path: JSONPath
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None

    def extract(self, root: JSONNode) -> Any:
        return self.path.apply(root)


@dataclass(kw_only=True)
class XMLCollector:
    rules: list[XMLRule] = field(default_factory=list)
    transforms: list[Transform] = field(default_factory=list)
    foreach: XMLPath | None = None

    def extract(self, root: XMLNode) -> CollectedData:
        return collect(root, self.rules)


@dataclass(kw_only=True)
class JSONCollector:
    rules: list[JSONRule] = field(default_factory=list)
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None

    def extract(self, root: JSONNode) -> CollectedData:
        return collect(root, self.rules)


@dataclass(kw_only=True)
class XMLRule:
    key: str | XMLPicker
    extractor: XMLPicker | XMLCollector
    transforms: list[Transform] = field(default_factory=list)
    foreach: XMLPath | None = None


@dataclass(kw_only=True)
class JSONRule:
    key: str | JSONPicker
    extractor: JSONPicker | JSONCollector
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None


def extract(
    root: XMLNode | JSONNode, rule: XMLRule | JSONRule
) -> CollectedData:
    data: dict[str, Any] = {}

    if rule.foreach is None:
        subroots = [root]
    else:
        subroots = rule.foreach.select(root)

    for subroot in subroots:
        if rule.extractor.foreach is None:
            nodes = [subroot]
        else:
            nodes = rule.extractor.foreach.select(subroot)

        raws = [rule.extractor.extract(n) for n in nodes]
        raws = [v for v in raws if (v is not _EMPTY) and (v is not None)]
        if len(raws) == 0:
            continue
        if len(rule.extractor.transforms) == 0:
            values = raws
        else:
            values = []
            for value in raws:
                for transform in rule.extractor.transforms:
                    value = transform.apply(value)
                values.append(value)
        value = values[0] if rule.extractor.foreach is None else values

        for transform in rule.transforms:
            value = transform.apply(value)

        match rule.key:
            case str():
                key = rule.key
            case XMLPicker() | JSONPicker():
                key = rule.key.extract(subroot)
                for key_transform in rule.key.transforms:
                    key = key_transform.apply(key)
        data[key] = value

    return data if len(data) > 0 else _EMPTY


def collect(
    root: XMLNode | JSONNode, rules: list[XMLRule] | list[JSONRule]
) -> CollectedData:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


@dataclass(kw_only=True)
class _Spec:
    version: str
    url: str
    url_default_params: dict[str, Any] = field(default_factory=dict)
    url_transform: Transform | None = None
    doctype: DocType
    pre: list[Preprocess] = field(default_factory=list)
    post: list[Postprocess] = field(default_factory=list)


@dataclass(kw_only=True)
class XMLSpec(_Spec):
    path_type: Literal["xpath"] = "xpath"
    rules: list[XMLRule] = field(default_factory=list)


@dataclass(kw_only=True)
class JSONSpec(_Spec):
    path_type: Literal["jmespath"] = "jmespath"
    rules: list[JSONRule] = field(default_factory=list)


def scrape(document: str, spec: XMLSpec | JSONSpec) -> CollectedData:
    root = _PARSERS[spec.doctype](document)
    for preprocess in spec.pre:
        root = preprocess.apply(root)
    data = collect(root, spec.rules)
    for postprocess in spec.post:
        data = postprocess.apply(data)
    return data


_data_classes = {Decimal}
deserialize = partial(
    typedload.load,
    strconstructed=_data_classes,
    pep563=True,
    basiccast=False,
)
serialize = partial(typedload.dump, strconstructed=_data_classes)

_spec_classes = {Preprocess, Postprocess, Transform, XMLPath, JSONPath}
load_spec = partial(
    deserialize,
    type_=XMLSpec | JSONSpec,
    strconstructed=_spec_classes,
    failonextra=True,
)
dump_spec = partial(serialize, strconstructed=_spec_classes)
