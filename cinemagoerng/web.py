# Copyright 2024 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.

import json
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from typing import Literal, Optional, TypeAlias

import httpx

from . import model, piculet, registry
from .operations import GetTitle, UpdateTitle


_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Firefox/102.0"


class HTTPClient:
    def __init__(self):
        self.headers = {"User-Agent": _USER_AGENT}
        self._default_client_params = {
            "timeout": 30.0,
            "follow_redirects": True,
        }

    def _get_headers(self, url: str) -> dict:
        headers = self.headers.copy()
        if "graphql" in url:
            headers["Content-Type"] = "application/json"
        return headers

    def _merge_client_params(
        self, httpx_kwargs: Optional[dict] = None
    ) -> dict:
        params = self._default_client_params.copy()
        if httpx_kwargs:
            params.update(httpx_kwargs)
        return params

    async def fetch_async(
        self, url: str, httpx_kwargs: Optional[dict] = None, **kwargs
    ) -> str:
        client_params = self._merge_client_params(httpx_kwargs)
        async with httpx.AsyncClient(**client_params) as client:
            response = await client.get(url, headers=self._get_headers(url))
            response.raise_for_status()
            return response.text

    def fetch(
        self, url: str, httpx_kwargs: Optional[dict] = None, **kwargs
    ) -> str:
        client_params = self._merge_client_params(httpx_kwargs)
        with httpx.Client(**client_params) as client:
            response = client.get(url, headers=self._get_headers(url))
            response.raise_for_status()
            return response.text


_http_client = HTTPClient()

registry.update_preprocessors(piculet.preprocessors)
registry.update_postprocessors(piculet.postprocessors)
registry.update_transformers(piculet.transformers)


SPECS_DIR = Path(__file__).parent / "specs"


@lru_cache(maxsize=None)
def _spec(page: str, /) -> piculet.Spec:
    path = SPECS_DIR / f"{page}.json"
    content = path.read_text(encoding="utf-8")
    return piculet.load_spec(json.loads(content))


TitlePage: TypeAlias = Literal[
    "main", "reference", "taglines", "episodes", "parental_guide"
]
TitleUpdatePage: TypeAlias = Literal[
    "main",
    "reference",
    "taglines",
    "episodes",
    "episodes_with_pagination",
    "akas",
    "parental_guide",
]


def get_title(
    imdb_id: str,
    *,
    page: TitlePage = "reference",
    httpx_kwargs: Optional[dict] = None,
    **kwargs,
) -> model.Title | None:
    """Get title information synchronously."""
    operation = GetTitle(_http_client.fetch)
    try:
        return operation.execute(
            _spec(f"title_{page}"),
            imdb_id=imdb_id,
            httpx_kwargs=httpx_kwargs,
            page=page,
            **kwargs,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return None
        raise


async def get_title_async(
    imdb_id: str,
    *,
    page: TitlePage = "reference",
    httpx_kwargs: Optional[dict] = None,
    **kwargs,
) -> model.Title | None:
    """Get title information asynchronously."""
    operation = GetTitle(_http_client.fetch_async)
    try:
        return await operation.execute_async(
            _spec(f"title_{page}"),
            imdb_id=imdb_id,
            httpx_kwargs=httpx_kwargs,
            page=page,
            **kwargs,
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return None
        raise


def update_title(
    title: model.Title,
    /,
    *,
    page: TitleUpdatePage,
    keys: list[str],
    httpx_kwargs: Optional[dict] = None,
    paginate_result: bool = False,
    **kwargs,
) -> None:
    """Update title with additional information synchronously."""
    operation = UpdateTitle(_http_client.fetch, title, keys)
    operation.execute(
        _spec(f"title_{page}"),
        imdb_id=title.imdb_id,
        httpx_kwargs=httpx_kwargs,
        page=page,
        paginate_result=paginate_result,
        **kwargs,
    )


async def update_title_async(
    title: model.Title,
    /,
    *,
    page: TitleUpdatePage,
    keys: list[str],
    httpx_kwargs: Optional[dict] = None,
    paginate_result: bool = False,
    **kwargs,
) -> None:
    operation = UpdateTitle(_http_client.fetch_async, title, keys)
    await operation.execute_async(
        _spec(f"title_{page}"),
        imdb_id=title.imdb_id,
        httpx_kwargs=httpx_kwargs,
        page=page,
        paginate_result=paginate_result,
        **kwargs,
    )
