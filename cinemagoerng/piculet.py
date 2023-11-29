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

from typing import Any, Callable, Collection, Mapping, Union

from dataclasses import dataclass, field
from functools import lru_cache, partial

from jmespath import compile as compile_jmespath
from lxml.etree import XPath, _Element
from lxml.html import fromstring as parse_html

from .transformers import transformer_registry


make_xpath = lru_cache(maxsize=None)(XPath)
make_jmespath = lru_cache(maxsize=None)(compile_jmespath)


@dataclass(kw_only=True)
class Extractor:
    transformer: str | None = None
    transform: Callable | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.transformer is not None:
            multiple = self.transformer[-1] == "*"
            key = self.transformer if not multiple else self.transformer[:-1]
            transform = transformer_registry.get(key)
            if transform is None:
                raise ValueError(f"Unknown transformer: {key}")
            if not multiple:
                self.transform = transform
            else:
                self.transform = partial(map, transform)


@dataclass(kw_only=True)
class XPathExtractor(Extractor):
    xpath: str
    sep: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.__compiled = make_xpath(self.xpath)

    def apply(self, data: _Element) -> str | None:
        selected: list[str] = self.__compiled(data)  # type: ignore
        if len(selected) == 0:
            return None
        return self.sep.join(selected).strip()


@dataclass(kw_only=True)
class JmesPathExtractor(Extractor):
    jmespath: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self.__compiled = make_jmespath(self.jmespath)

    def apply(self, data: Mapping[str, Any]) -> Any:
        return self.__compiled.search(data)


@dataclass(kw_only=True)
class MapRule:
    key: str
    extractor: Union[JmesPathExtractor, "MapRulesExtractor"]


@dataclass(kw_only=True)
class MapRulesExtractor(Extractor):
    rules: list[MapRule] = field(default_factory=list)

    def apply(self, data: Any) -> Mapping[str, Any]:
        return apply_rules(self.rules, data)


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
        if (raw is None) or ((isinstance(raw, Collection) and len(raw) == 0)):
            continue
        if rule.extractor.transform is None:
            value = raw
        else:
            value = rule.extractor.transform(raw)
        result[rule.key] = value
        match rule:
            case TreeRule():
                subresult = apply_rules(rule.post_map, value)
                result.update(subresult)
    return result


def scrape(document: str, /, rules: list[TreeRule]) -> Mapping[str, Any]:
    root = parse_html(document)
    data = apply_rules(rules, root)
    return data
