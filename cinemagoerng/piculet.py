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

from dataclasses import dataclass
from functools import lru_cache
from typing import Callable, Dict, Union

from lxml.etree import XPath
from lxml.html import fromstring as parse_html


xpath: Callable[[str], XPath] = lru_cache(maxsize=None)(XPath)


@dataclass
class Spec:
    url: str
    rules: Dict[str, str]


def scrape(document: str, /,
           rules: Dict[str, str]) -> Dict[str, Union[str, int]]:
    root = parse_html(document)
    data: Dict[str, Union[str, int]] = {}
    for key, path in rules.items():
        extract = xpath(path)
        raw: list[str] = extract(root)  # type: ignore
        data[key] = "".join(raw).strip()
    return data
