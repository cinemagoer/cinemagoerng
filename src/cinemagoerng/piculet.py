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
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from typing import Any, Literal, MutableMapping, TypeAlias, TypeVar

import lxml.etree
import lxml.html
import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath

XMLNode: TypeAlias = lxml.etree._Element
JSONNode: TypeAlias = dict

Node = TypeVar("Node", XMLNode, JSONNode)

__lxml_ns = lxml.etree.FunctionNamespace(None)
__lxml_ns["string-join"] = lambda _, texts, sep: sep.join(texts)

DocType: TypeAlias = Literal["html", "xml", "json"]

_PARSERS: dict[DocType, Callable[[str], XMLNode | JSONNode]] = {
    "html": lxml.html.fromstring,
    "xml": lxml.etree.fromstring,
    "json": json.loads,
}

CollectedData: TypeAlias = MutableMapping[str, Any]

_EMPTY: CollectedData = {}


Preprocessor: TypeAlias = Callable[[Node], XMLNode | JSONNode]

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
    _re_text_path = re.compile(r""".*\/(text\(\)|(@\w+))$""")

    def __init__(self, path: str) -> None:
        self.path: str = path
        if XMLPath._re_text_path.match(path):
            path = f"string({path})"
        self._compiled = compile_xpath(path)

    def __str__(self) -> str:
        return self.path

    def apply(self, root: XMLNode) -> Any:
        value = self._compiled(root)
        return value if value != "" else None

    def select(self, root: XMLNode) -> list[XMLNode]:
        return self._compiled(root)  # type: ignore


class JSONPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_jmespath(path).search

    def __str__(self) -> str:
        return self.path

    def apply(self, root: JSONNode) -> Any:
        return self._compiled(root)

    def select(self, root: JSONNode) -> list[JSONNode]:
        selected = self._compiled(root)
        return selected if selected is not None else []  # type: ignore


@dataclass(kw_only=True)
class XMLPicker:
    path: XMLPath
    transforms: list[Transform] = field(default_factory=list)
    foreach: XMLPath | None = None

    def extract(self, root: XMLNode) -> Any:
        return self.path.apply(root)


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
        return collect_xml(root, self.rules)


@dataclass(kw_only=True)
class JSONCollector:
    rules: list[JSONRule] = field(default_factory=list)
    transforms: list[Transform] = field(default_factory=list)
    foreach: JSONPath | None = None

    def extract(self, root: JSONNode) -> CollectedData:
        return collect_json(root, self.rules)


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


def extract_xml(root: XMLNode, rule: XMLRule) -> CollectedData:
    data: dict[str, Any] = {}

    subroots = [root] if rule.foreach is None else rule.foreach.select(root)
    for subroot in subroots:
        if rule.extractor.foreach is None:
            value = rule.extractor.extract(subroot)
            if (value is None) or (value is _EMPTY):
                continue
            for transform in rule.extractor.transforms:
                value = transform.apply(value)
        else:
            raws = [rule.extractor.extract(n)
                    for n in rule.extractor.foreach.select(subroot)]
            value = [v for v in raws if (v is not None) and (v is not _EMPTY)]
            if len(value) == 0:
                continue
            if len(rule.extractor.transforms) > 0:
                for i in range(len(value)):
                    for transform in rule.extractor.transforms:
                        value[i] = transform.apply(value[i])

        for transform in rule.transforms:
            value = transform.apply(value)

        match rule.key:
            case str():
                key = rule.key
            case XMLPicker():
                key = rule.key.extract(subroot)
                for key_transform in rule.key.transforms:
                    key = key_transform.apply(key)
        data[key] = value

    return data if len(data) > 0 else _EMPTY


def extract_json(root: JSONNode, rule: JSONRule) -> CollectedData:
    data: dict[str, Any] = {}

    subroots = [root] if rule.foreach is None else rule.foreach.select(root)
    for subroot in subroots:
        if rule.extractor.foreach is None:
            value = rule.extractor.extract(subroot)
            if (value is None) or (value is _EMPTY):
                continue
            for transform in rule.extractor.transforms:
                value = transform.apply(value)
        else:
            raws = [rule.extractor.extract(n)
                    for n in rule.extractor.foreach.select(subroot)]
            value = [v for v in raws if (v is not None) and (v is not _EMPTY)]
            if len(value) == 0:
                continue
            if len(rule.extractor.transforms) > 0:
                for i in range(len(value)):
                    for transform in rule.extractor.transforms:
                        value[i] = transform.apply(value[i])

        for transform in rule.transforms:
            value = transform.apply(value)

        match rule.key:
            case str():
                key = rule.key
            case JSONPicker():
                key = rule.key.extract(subroot)
                for key_transform in rule.key.transforms:
                    key = key_transform.apply(key)
        data[key] = value

    return data if len(data) > 0 else _EMPTY


def collect_xml(root: XMLNode, rules: list[XMLRule]) -> CollectedData:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract_xml(root, rule)
        data.update(subdata)
    return data if len(data) > 0 else _EMPTY


def collect_json(root: JSONNode, rules: list[JSONRule]) -> CollectedData:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract_json(root, rule)
        data.update(subdata)
    return data if len(data) > 0 else _EMPTY


@dataclass(kw_only=True)
class _Spec:
    version: str
    url: str
    graphql: dict[str, Any] | None = None
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
    match (root, spec):
        case (XMLNode(), XMLSpec()):
            data = collect_xml(root, spec.rules)
        case (JSONNode(), JSONSpec()):
            data = collect_json(root, spec.rules)
        case _:
            raise TypeError("Node and spec types don't match")
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
