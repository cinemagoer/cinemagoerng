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

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import partial
from types import MappingProxyType
from typing import (
    Any,
    List,
    Literal,
    Mapping,
    MutableMapping,
    TypeAlias,
    TypedDict,
)

import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath
from lxml.etree import _Element as TreeNode
from lxml.etree import fromstring as parse_xml
from lxml.html import fromstring as parse_html


MapNode: TypeAlias = Mapping[str, Any]
MutableMapNode: TypeAlias = MutableMapping[str, Any]


_EMPTY: MapNode = MappingProxyType({})


Preprocessor: TypeAlias = Callable[[TreeNode | MapNode], TreeNode | MapNode]

preprocessors: dict[str, Preprocessor] = {}


class Preprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Preprocessor = preprocessors[name]

    def __str__(self) -> str:
        return self.name


Postprocessor: TypeAlias = Callable[[MutableMapNode], None]

postprocessors: dict[str, Postprocessor] = {}


class Postprocess:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.apply: Postprocessor = postprocessors[name]

    def __str__(self) -> str:
        return self.name


class DictItem(TypedDict):
    key: str
    value: Any | None


def make_dict(item: DictItem, /) -> dict[str, Any]:
    value = item.get("value")
    if value is None:
        return {}
    return {item["key"]: value}


Transformer: TypeAlias = Callable[[Any], Any]


transformers: dict[str, Transformer] = {
    "decimal": lambda x: Decimal(str(x)),
    "int": int,
    "json": json.loads,
    "lower": str.lower,
    "make_dict": make_dict,
    "str": str,
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


class MapPath:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self._compiled = compile_jmespath(path).search

    def __str__(self) -> str:
        return self.path

    def apply(self, root: MapNode) -> Any:
        return self._compiled(root)  # type: ignore

    def select(self, root: MapNode) -> list[MapNode]:
        selected = self._compiled(root)
        return selected if selected is not None else []  # type: ignore


@dataclass(kw_only=True)
class Extractor:
    transforms: list[Transform] = field(default_factory=list)


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
    transforms: list[Transform] = field(default_factory=list)


@dataclass(kw_only=True)
class MapRule:
    key: str | MapPicker
    extractor: MapPicker | MapCollector
    foreach: MapPath | None = None
    transforms: list[Transform] = field(default_factory=list)


def extract(root: TreeNode | MapNode, rule: TreeRule | MapRule) -> MapNode:
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
            case TreePicker() | MapPicker():
                key = rule.key.extract(subroot)
                for key_transform in rule.key.transforms:
                    key = key_transform.apply(key)
        data[key] = value

    return data if len(data) > 0 else _EMPTY


def collect(root: TreeNode | MapNode, rules: list[TreeRule] | list[MapRule]) -> MapNode:
    data: dict[str, Any] = {}
    for rule in rules:
        subdata = extract(root, rule)
        if len(subdata) > 0:
            data.update(subdata)
    return data if len(data) > 0 else _EMPTY


DocType: TypeAlias = Literal["html", "xml", "json"]


@dataclass(kw_only=True)
class Spec:
    version: str
    url: str
    url_default_params: dict[str, Any] = field(default_factory=dict)
    url_transform: Transform | None = None
    doctype: DocType
    pre: list[Preprocess] = field(default_factory=list)
    post: list[Postprocess] = field(default_factory=list)
    rules: list[TreeRule] | list[MapRule]


@dataclass(kw_only=True)
class TreeSpec(Spec):
    path_type: Literal["xpath"] = "xpath"
    rules: list[TreeRule]


@dataclass(kw_only=True)
class MapSpec(Spec):
    path_type: Literal["jmespath"] = "jmespath"
    rules: list[MapRule]


def scrape(
    document: str,
    *,
    doctype: DocType,
    rules: list[TreeRule] | list[MapRule],
    pre: list[Preprocess] | None = None,
    post: list[Postprocess] | None = None,
) -> MapNode:
    match doctype:
        case "html":
            root = parse_html(document)
        case "xml":
            root = parse_xml(document)
        case "json":
            root = json.loads(document)
    if pre is not None:
        for preprocess in pre:
            root = preprocess.apply(root)
    data = collect(root, rules)
    if post is not None:
        for postprocess in post:
            postprocess.apply(data)
    return data


_spec_classes = {Preprocess, Postprocess, Transform, TreePath, MapPath}

load_spec = partial(
    typedload.load,
    type_=TreeSpec | MapSpec,
    strconstructed=_spec_classes,
    pep563=True,
    failonextra=True,
    basiccast=False,
)
dump_spec = partial(typedload.dump, strconstructed=_spec_classes)


_data_classes = {Decimal}

deserialize = partial(typedload.load, strconstructed=_data_classes, pep563=True, basiccast=False)
serialize = partial(typedload.dump, strconstructed=_data_classes)
