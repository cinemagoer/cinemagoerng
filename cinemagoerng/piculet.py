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

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Mapping

from lxml.etree import XPath, _Element
from lxml.html import fromstring as parse_html


xpath: Callable[[str], XPath] = lru_cache(maxsize=None)(XPath)


def scrape(document: str, /, rules: Mapping[str, str]) -> dict[str, str]:
    root: _Element = parse_html(document)
    data: dict[str, str] = {}
    for key, path in rules.items():
        extract = xpath(path)
        raw: list[str] = extract(root)  # type: ignore
        data[key] = "".join(raw).strip()
    return data
