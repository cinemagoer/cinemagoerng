# Copyright 2024-2025 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

import json
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from typing import Literal, TypeAlias
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from . import model, piculet, registry

_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Firefox/102.0"


def fetch(url: str, **kwargs) -> str:
    request = Request(url)
    request.add_header("User-Agent", _USER_AGENT)
    if "graphql" in url:
        request.add_header("Content-Type", "application/json")
    accept_language = kwargs.get("accept_language")
    if accept_language is not None:
        request.add_header("Accept-Language", accept_language)
    with urlopen(request) as response:
        content: bytes = response.read()
    return content.decode("utf-8")


registry.update_preprocessors(piculet.preprocessors)
registry.update_postprocessors(piculet.postprocessors)
registry.update_transformers(piculet.transformers)


SPECS_DIR = Path(__file__).parent / "specs"


@lru_cache(maxsize=None)
def _spec(page: str, /) -> piculet.XMLSpec | piculet.JSONSpec:
    path = SPECS_DIR / f"{page}.json"
    content = path.read_text(encoding="utf-8")
    return piculet.load_spec(json.loads(content))  # type: ignore


TitlePage: TypeAlias = Literal[
    "episodes",
    "parental_guide",
    "reference",
    "taglines",
]

TitleUpdatePage: TypeAlias = Literal[
    "akas",
    "episodes",
    "episodes_with_pagination",
    "parental_guide",
    "reference",
    "taglines",
]


def get_title(imdb_id: str, *, page: TitlePage = "reference",
              **kwargs) -> model.Title | None:
    spec = _spec(f"title_{page}")
    url_params = {"imdb_id": imdb_id} | spec.url_default_params | kwargs

    # Apply URL transform if specified
    if spec.url_transform:
        url = spec.url_transform.apply({"url": spec.url, "params": url_params})
    else:
        url = spec.url % url_params

    if fetch.__name__ == "fetch_cached":
        cache_key = f"title_{imdb_id}_{page}"
        extra_args = [f"{k}={v}" for k, v in kwargs.items()]
        cache_key += "_" + "_".join(extra_args) if extra_args else ""
        cache_key += f".{spec.doctype}"
        kwargs["cache_key"] = cache_key

    try:
        document = fetch(url, **kwargs)
    except HTTPError as e:
        if e.status == HTTPStatus.NOT_FOUND:
            return None
        raise e  # pragma: no cover
    data = piculet.scrape(document, spec)
    return piculet.deserialize(data, model.Title)


def update_title(title: model.Title, /, *, page: TitleUpdatePage,
                 keys: list[str], paginate: bool = False,
                 **kwargs) -> None:
    spec = _spec(f"title_{page}")
    url_params = {"imdb_id": title.imdb_id} | spec.url_default_params | kwargs

    # Apply URL transform if specified
    if spec.url_transform:
        url = spec.url_transform.apply({"url": spec.url, "params": url_params})
    else:
        url = spec.url % url_params

    if fetch.__name__ == "fetch_cached":
        cache_key = f"title_{title.imdb_id}_{page}"
        extra_args = [f"{k}={v}" for k, v in kwargs.items()]
        cache_key += "_" + "_".join(extra_args) if extra_args else ""
        cache_key += f".{spec.doctype}"
        kwargs["cache_key"] = cache_key

    document = fetch(url, **kwargs)
    data = piculet.scrape(document, spec)
    for key in keys:
        value = data.get(key)
        if value is None:
            continue
        if key == "episodes":
            if isinstance(value, dict):
                value = piculet.deserialize(value, model.EpisodeMap)
                title.episodes.update(value)
            else:
                value = piculet.deserialize(value, list[model.TVEpisode])
                title.add_episodes(value)
        elif key == "akas":
            value = [piculet.deserialize(aka, model.AKA) for aka in value]
            title.akas.extend(value)
        elif key == "certification":
            value = piculet.deserialize(value, model.Certification)
            setattr(title, key, value)
        elif key == "advisories":
            value = piculet.deserialize(value, model.Advisories)
            setattr(title, key, value)
        else:
            setattr(title, key, value)

    if paginate and data.get("has_next_page", False):
        kwargs["after"] = f'"{data["end_cursor"]}"'
        update_title(title, page=page, keys=keys, paginate=paginate, **kwargs)
