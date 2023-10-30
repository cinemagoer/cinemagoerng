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

import json
from functools import lru_cache
from pathlib import Path
from urllib.request import Request, urlopen

import typedload

from .model import Title
from .piculet import Spec, scrape


_USER_AGENT = " ".join([
    "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B)",
    "AppleWebKit/535.19 (KHTML, like Gecko)",
    "Chrome/18.0.1025.133 Mobile Safari/535.19",
])

SPECS_DIR = Path(__file__).parent / "specs"


def fetch(url: str, /) -> str:
    request = Request(url)
    request.add_header("User-Agent", _USER_AGENT)
    with urlopen(request) as connection:
        content: bytes = connection.read()
    return content.decode("utf-8")


@lru_cache(maxsize=None)
def _spec(name: str, /) -> Spec:
    spec_path = SPECS_DIR / f"{name}.json"
    content = spec_path.read_text(encoding="utf-8")
    return typedload.load(json.loads(content), Spec)


def get_title(imdb_id: int) -> Title:
    spec = _spec("title")
    url = spec.url % {"imdb_id": f"{imdb_id:07d}"}
    document = fetch(url)
    data = scrape(document, spec.rules)
    data["imdb_id"] = imdb_id
    return typedload.load(data, Title)


def update_title(title: Title, /, *, infoset: str) -> Title:
    spec = _spec(f"title_{infoset}")
    url = spec.url % {"imdb_id": f"{title.imdb_id:07d}"}
    document = fetch(url)
    data = scrape(document, spec.rules)
    existing_data = typedload.dump(title)
    return typedload.load(existing_data | data, Title)
