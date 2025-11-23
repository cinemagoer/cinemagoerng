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

"""
Piculet is a module for extracting data from HTML/XML and JSON documents.
The queries are written in XPath for HTML/XML, and in JMESPath for JSON.

The documentation is available on: https://piculet.readthedocs.io/
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Literal, Mapping, TypeAlias

import lxml.etree
import lxml.html
import typedload
from jmespath import compile as compile_jmespath
from lxml.etree import XPath as compile_xpath


deserialize = partial(typedload.load, pep563=True, basiccast=False)
"""Generate an object from a dictionary."""

serialize = typedload.dump
"""Generate a dictionary from an object."""


Node: TypeAlias = lxml.etree._Element | dict[str, Any]

DocType: TypeAlias = Literal["html", "xml", "json"]

_PARSERS: dict[DocType, Callable[[str], Node]] = {
    "html": lxml.html.fromstring,
    "xml": lxml.etree.fromstring,
    "json": json.loads,
}


Preprocessor: TypeAlias = Callable[[Node], Node]
Postprocessor: TypeAlias = Callable[[dict[str, Any]], dict[str, Any]]
Transformer: TypeAlias = Callable[[Any], Any]


class Query:
    """A query based on XPath or JMESPath.

    Expressions starting with ``/`` or ``./`` are assumed to be XPath.
    and others are assumed to be JMESPath.
    """

    def __init__(self, path: str) -> None:
        self.path: str = path
        """Path expression to apply to nodes."""

        self._compiled: Callable[[Node], Any] = \
            compile_xpath(path) if path.startswith(("/", "./")) else \
            compile_jmespath(path).search  # type: ignore

    def __str__(self) -> str:
        return self.path

    def apply(self, node: Node) -> Any:
        """Apply this query to a node.

        If this is an XPath query, it should return a list of texts,
        which will be concatenated.
        """
        value: Any = self._compiled(node)
        if isinstance(self._compiled, lxml.etree.XPath):
            return "".join(value) if len(value) > 0 else None
        return value

    def get(self, node: Node) -> Node:
        """Get the first node matched by applying this query to a node."""
        value: Any = self._compiled(node)
        if isinstance(self._compiled, lxml.etree.XPath):
            return value[0]
        return value

    def select(self, node: Node) -> list[Node]:
        """Get all nodes matched by applying this query to a node."""
        value: Any = self._compiled(node)
        if isinstance(self._compiled, lxml.etree.XPath):
            return value
        return value if value is not None else []


@dataclass(kw_only=True)
class Extractor:
    """Base class for extractors."""

    root: Query | None = None
    """Query to select the root node to extract the data from."""

    foreach: Query | None = None
    """Query to select the nodes for producing multiple results."""

    transforms: list[str] = field(default_factory=list)
    """Names of transform functions to apply to the obtained data."""

    _transforms: list[Transformer] = field(default_factory=list)

    def _set_transforms(self, registry: Mapping[str, Transformer]) -> None:
        self._transforms = [registry[name] for name in self.transforms]


@dataclass(kw_only=True)
class Picker(Extractor):
    """An extractor that produces a single value."""

    path: Query
    """Query to apply to a node to extract the value."""

    def extract(self, node: Node) -> Any:
        """Extract data from a node."""
        return self.path.apply(node)


@dataclass(kw_only=True)
class Collector(Extractor):
    """An extractor that collects multiple pieces of data."""

    rules: list[Rule] = field(default_factory=list)
    """Rules to apply to a node to collect the data."""

    def _set_transforms(self, registry: Mapping[str, Transformer]) -> None:
        super()._set_transforms(registry)
        for rule in self.rules:
            rule._set_transformers(registry)

    def extract(self, node: Node) -> dict[str, Any] | None:
        """Extract data from a node."""
        data: dict[str, Any] = {}
        for rule in self.rules:
            subdata = rule.apply(node)
            if subdata is not None:
                data.update(subdata)
        return data if len(data) > 0 else None


@dataclass(kw_only=True)
class Rule:
    """A rule that generates key-value pairs from a node."""

    key: str | Picker
    """Name of key or extractor to produce the key."""

    extractor: Picker | Collector
    """Extractor to produce the value."""

    foreach: Query | None = None
    """Query to select the nodes for producing multiple key-value pairs."""

    def _set_transformers(self, registry: Mapping[str, Transformer]) -> None:
        self.extractor._set_transforms(registry)
        if isinstance(self.key, Picker):
            self.key._set_transforms(registry)

    def apply(self, root: Node) -> dict[str, Any] | None:
        """Apply this rule to a node."""
        data: dict[str, Any] = {}

        if self.extractor.root is not None:
            root = self.extractor.root.get(root)
        nodes = [root] if self.foreach is None else self.foreach.select(root)
        for node in nodes:
            if self.extractor.foreach is None:
                value = self.extractor.extract(node)
                if value is None:
                    continue
                for transform in self.extractor._transforms:
                    value = transform(value)
            else:
                raws = [self.extractor.extract(n)
                        for n in self.extractor.foreach.select(node)]
                value = [v for v in raws if v is not None]
                if len(value) == 0:
                    continue
                if len(self.extractor.transforms) > 0:
                    for i in range(len(value)):
                        for transform in self.extractor._transforms:
                            value[i] = transform(value[i])

            if isinstance(self.key, str):
                key = self.key
            else:
                key = self.key.extract(node)
                for key_transform in self.key._transforms:
                    key = key_transform(key)
            data[key] = value

        return data if len(data) > 0 else None


@dataclass(kw_only=True)
class Spec(Collector):
    """A scraping specification."""

    pre: list[str] = field(default_factory=list)
    """Names of preprocessor functions."""

    post: list[str] = field(default_factory=list)
    """Names of postprocessor functions."""

    _pre: list[Preprocessor] = field(default_factory=list)
    _post: list[Postprocessor] = field(default_factory=list)

    def _set_pre(self, registry: Mapping[str, Preprocessor]) -> None:
        self._pre = [registry[name] for name in self.pre]

    def _set_post(self, registry: Mapping[str, Postprocessor]) -> None:
        self._post = [registry[name] for name in self.post]

    def preprocess(self, root: Node) -> Node:
        """Apply the preprocessors to the root node."""
        for preprocess in self._pre:
            root = preprocess(root)
        return root

    def extract(self, root: Node):
        """Extract data from a node."""
        if self.root is not None:
            root = self.root.get(root)
        data = super().extract(root)
        return data if data is not None else {}

    def postprocess(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply the postprocessors to the collected data."""
        for postprocess in self._post:
            data = postprocess(data)
        return data

    def scrape(
            self,
            document: str | Node,
            *,
            doctype: DocType,
        ) -> dict[str, Any]:
        """Scrape a document."""
        root = document if not isinstance(document, str) else \
            build_tree(document, doctype=doctype)
        root = self.preprocess(root)
        data = self.extract(root)
        data = self.postprocess(data)
        return data


def build_tree(document: str, doctype: DocType) -> Node:
    """Convert a document to a tree."""
    return _PARSERS[doctype](document)


def load_spec(
        content: Mapping[str, Any],
        *,
        type_: type = Spec,
        transformers: Mapping[str, Transformer] | None = None,
        preprocessors: Mapping[str, Preprocessor] | None = None,
        postprocessors: Mapping[str, Postprocessor] | None = None,
) -> Spec:
    """Deserialize a mapping into a scraping specification."""
    spec: Spec = deserialize(
        content,
        type_=type_,
        strconstructed={Query},
        failonextra=True,
    )
    if preprocessors is not None:
        spec._set_pre(preprocessors)
    if postprocessors is not None:
        spec._set_post(postprocessors)
    if transformers is not None:
        spec._set_transforms(transformers)
    return spec


def dump_spec(spec: Spec) -> dict[str, Any]:
    return serialize(spec, strconstructed={Query})
