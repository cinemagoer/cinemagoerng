# Copyright 2023 H. Turgut Uyar <uyar@tekir.org>
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Retrieve data from the IMDb web site."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from urllib.request import Request, urlopen


BASE_URL = "https://www.imdb.com"

_URL_PARAMS = MappingProxyType({"base": BASE_URL})

_USER_AGENT = " ".join([
    "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B)",
    "AppleWebKit/535.19 (KHTML, like Gecko)",
    "Chrome/18.0.1025.133 Mobile Safari/535.19",
])

CACHE_DIR = Path.home() / ".cache" / "cinemagoerng" / "imdb"
if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

SPECS_DIR = Path(__file__).parent / "specs"


@lru_cache()
def _retrieve(url: str, /, skip_cache: bool = False) -> str:
    if not skip_cache:
        cache_file = url.split(BASE_URL)[-1][1:].replace("/", "__")
        cache_path = CACHE_DIR / cache_file
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

    request = Request(url)
    request.add_header("User-Agent", _USER_AGENT)
    with urlopen(request) as connection:
        content: bytes = connection.read()
    cache_path.write_bytes(content)
    return content.decode("utf-8")


def _get_spec(spec_name: str, /) -> Any:
    spec_file = SPECS_DIR / f"{spec_name}.json"
    spec_content = spec_file.read_text(encoding="utf-8")
    return json.loads(spec_content)


def _get_imdb(spec_name: str, /, *,
              url_params: Mapping[str, str],
              skip_cache: bool = False) -> Mapping[str, Any]:
    spec = _get_spec(spec_name)
    url_pattern: str = spec["url"]
    # XXX: use dict union when 3.8 is dropped
    url = url_pattern % {**url_params, **_URL_PARAMS}
    _ = _retrieve(url, skip_cache=skip_cache)
    return {}


def get_title_reference(imdb_id: int, *,
                        skip_cache: bool = False) -> Mapping[str, Any]:
    """Get the data from the combined reference page of a title.

    :param imdb_id: IMDb id of the title to retrieve.
    :return: Extracted data.
    """
    url_params = {"imdb_id": f"{imdb_id:07d}"}
    return _get_imdb("title_reference", url_params=url_params,
                     skip_cache=skip_cache)
