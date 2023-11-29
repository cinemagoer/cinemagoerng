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

from jmespath import compile as compile_jmespath
from lxml.etree import XPath, _Element
from lxml.html import fromstring as parse_html
from typedload.datadumper import Dumper
from typedload.dataloader import Loader

from .transformers import transformer_registry


_EMPTY: Mapping = MappingProxyType({})


make_xpath = lru_cache(maxsize=None)(XPath)
make_jmespath = lru_cache(maxsize=None)(compile_jmespath)


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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.__do(*args, **kwargs)


@dataclass(kw_only=True)
class Extractor:
    transform: Transform | None = None


@dataclass(kw_only=True)
class XPathExtractor(Extractor):
    xpath: str
    sep: str = ""

    def __post_init__(self) -> None:
        self.__compiled = make_xpath(self.xpath)

    def apply(self, data: _Element) -> str | Mapping:
        selected: list[str] = self.__compiled(data)  # type: ignore
        if len(selected) == 0:
            return _EMPTY
        return self.sep.join(selected).strip()


@dataclass(kw_only=True)
class JmesPathExtractor(Extractor):
    jmespath: str

    def __post_init__(self) -> None:
        self.__compiled = make_jmespath(self.jmespath)

    def apply(self, data: Mapping[str, Any]) -> Any:
        selected = self.__compiled.search(data)
        if (selected is None) or \
                ((isinstance(selected, Collection) and len(selected) == 0)):
            return _EMPTY
        return selected


@dataclass(kw_only=True)
class MapRulesExtractor(Extractor):
    rules: List["MapRule"] = field(default_factory=list)

    def apply(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


@dataclass(kw_only=True)
class MapRule:
    key: str
    extractor: JmesPathExtractor | MapRulesExtractor


@dataclass(kw_only=True)
class TreeRule:
    key: str
    extractor: XPathExtractor
    post_map: list[MapRule] = field(default_factory=list)


@dataclass(kw_only=True)
class Spec:
    url: str
    rules: list[TreeRule] = field(default_factory=list)


def apply_rules(rules: list[TreeRule] | list[MapRule],
                data: Any) -> Mapping[str, Any]:
    result: dict[str, Any] = {}
    for rule in rules:
        raw = rule.extractor.apply(data)
        if raw is _EMPTY:
            continue
        if rule.extractor.transform is None:
            value = raw
        else:
            value = rule.extractor.transform(raw)
        result[rule.key] = value
        match rule:
            case TreeRule():
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


_loader = Loader()
_loader.strconstructed = {Transform, Decimal}  # type: ignore
_loader.pep563 = True
deserialize = _loader.load

_dumper = Dumper()
_dumper.strconstructed = {Transform, Decimal}  # type: ignore
serialize = _dumper.dump
