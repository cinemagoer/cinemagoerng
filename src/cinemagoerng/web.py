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
from typing import Any, Literal, Mapping, NotRequired, TypeAlias, TypedDict
from urllib.error import HTTPError
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
def get_spec(page: str, /) -> piculet.XMLSpec | piculet.JSONSpec:
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


def scrape(
        spec: piculet.XMLSpec | piculet.JSONSpec,
        *,
        context: Mapping[str, Any],
        headers: dict[str, str] | None = None,
) -> piculet.CollectedData:
    url = _get_url(spec, context=context)
    request_headers = headers if headers is not None else {}
    if spec.graphql is not None:
        request_headers["Content-Type"] = "application/json"
    try:
        document = fetch(url, headers=request_headers)
    except HTTPError as e:
        if e.status == HTTPStatus.NOT_FOUND:
            return piculet._EMPTY
        raise e  # pragma: no cover
    return piculet.scrape(document, spec)


def get_title(
        imdb_id: str,
        *,
        page: TitlePage = "reference",
        headers: dict[str, str] | None = None,
) -> model.Title:
    spec = get_spec(f"title_{page}")
    context = {"imdb_id": imdb_id}
    data = scrape(spec=spec, context=context, headers=headers)
    return piculet.deserialize(data, model.Title)  # type: ignore


# def update_title(
#         title: model.Title,
#         /,
#         *,
#         page: TitleUpdatePage,
#         keys: list[str], paginate: bool = False,
#         headers: dict[str, str] | None = None,
# ) -> None:
#     data = piculet.scrape(document, spec)
#     for key in keys:
#         value = data.get(key)
#         if value is None:
#             continue
#         if key == "episodes":
#             if isinstance(value, dict):
#                 value = piculet.deserialize(value, model.EpisodeMap)
#                 title.episodes.update(value)
#             else:
#                 value = piculet.deserialize(value, list[model.TVEpisode])
#                 title.add_episodes(value)
