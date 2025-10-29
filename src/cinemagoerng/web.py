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
from pathlib import Path
from typing import Any, Mapping, NotRequired, TypedDict
from urllib.request import Request, urlopen

from . import model, piculet, registry

_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Firefox/102.0"


def fetch(url: str, /, *, headers: dict[str, str] | None = None) -> str:
    request = Request(url)
    request_headers = headers if headers is not None else {}
    if "User-Agent" not in request_headers:
        request_headers["User-Agent"] = _USER_AGENT
    for header, value in request_headers.items():
        request.add_header(header, value)
    with urlopen(request) as response:
        content: bytes = response.read()
    return content.decode("utf-8")


registry.update_preprocessors(piculet.preprocessors)
registry.update_postprocessors(piculet.postprocessors)
registry.update_transformers(piculet.transformers)


class GraphQLVariables(TypedDict):
    after: NotRequired[str]
    const: NotRequired[str]
    first: NotRequired[int]
    isAutoTranslationEnabled: NotRequired[bool]
    locale: NotRequired[str]
    originalTitleText: NotRequired[bool]


class GraphQLParams(TypedDict):
    operationName: str
    variables: GraphQLVariables
    extensions: dict[str, Any]


SPECS_DIR = Path(__file__).parent / "specs"


@lru_cache(maxsize=None)
def _spec(page: str, /) -> piculet.XMLSpec | piculet.JSONSpec:
    path = SPECS_DIR / f"{page}.json"
    content = path.read_text(encoding="utf-8")
    return piculet.load_spec(json.loads(content))  # type: ignore


def _get_url(
        spec: piculet.XMLSpec | piculet.JSONSpec,
        context: Mapping[str, Any],
) -> str:
    url_template = spec.url
    if spec.graphql is not None:
        g_params = []
        for g_key, g_value in spec.graphql.items():
            match g_value:
                case dict():
                    g_dump = json.dumps(g_value, separators=(",", ":"))
                    g_params.append(f"{g_key}={g_dump}")
                case _:
                    g_params.append(f"{g_key}={g_value}")
        url_template += "?" + "&".join(g_params)
    return url_template % context


def _scrape(
        spec: piculet.XMLSpec | piculet.JSONSpec,
        *,
        context: Mapping[str, Any],
        headers: dict[str, str] | None = None,
) -> piculet.CollectedData:
    url = _get_url(spec, context=context)
    request_headers = headers if headers is not None else {}
    if spec.graphql is not None:
        request_headers["Content-Type"] = "application/json"
    document = fetch(url, headers=request_headers)
    return piculet.scrape(document, spec)


def get_title(
        imdb_id: str,
        *,
        headers: dict[str, str] | None = None,
) -> model.Title:
    spec = _spec("title_reference")
    context = {"imdb_id": imdb_id}
    data = _scrape(spec=spec, context=context, headers=headers)
    return piculet.deserialize(data, model.Title)  # type: ignore


def set_taglines(
        title: model.Title,
        *,
        headers: dict[str, str] | None = None,
) -> None:
    spec = _spec("title_taglines")
    context = {"imdb_id": title.imdb_id}
    data = _scrape(spec=spec, context=context, headers=headers)
    taglines = data.get("taglines")
    if taglines is not None:
        title.taglines = data["taglines"]


def set_akas(
        title: model.Title,
        *,
        spec: piculet.XMLSpec | piculet.JSONSpec | None = None,
        headers: dict[str, str] | None = None,
) -> None:
    if spec is None:
        spec = _spec("title_akas")
    g_params: GraphQLParams = spec.graphql  # type: ignore
    g_vars = g_params["variables"]
    context: dict[str, Any] = {"imdb_id": title.imdb_id} | g_vars
    data = _scrape(spec, context=context, headers=headers)
    akas = [
        piculet.deserialize(aka, model.AKA) for aka in data.get("akas", [])
    ]
    title.akas.extend(akas)
    if data.get("has_next_page", False):
        g_vars["after"] = data["end_cursor"]
        set_akas(title, spec=spec, headers=headers)


def set_parental_guide(
        title: model.Title,
        *,
        headers: dict[str, str] | None = None,
) -> None:
    spec = _spec("title_parental_guide")
    context = {"imdb_id": title.imdb_id}
    data = _scrape(spec=spec, context=context, headers=headers)
    title.certification = piculet.deserialize(
        data["certification"],
        model.Certification,
    )
    title.advisories = piculet.deserialize(
        data["advisories"],
        model.Advisories,
    )


def set_episodes(
        title: model.TVSeries | model.TVMiniSeries,
        *,
        season: str,
        headers: dict[str, str] | None = None,
) -> None:
    spec = _spec("title_episodes")
    context = {"imdb_id": title.imdb_id, "season": season}
    data = _scrape(spec=spec, context=context, headers=headers)
    episodes = data.get("episodes")
    if episodes is not None:
        title.episodes[season] = piculet.deserialize(
            episodes,
            dict[str, model.TVEpisode],
        )
