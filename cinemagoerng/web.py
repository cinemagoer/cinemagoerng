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
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen


try:
    import socks
    from sockshandler import SocksiPyHandler

    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

from . import model, piculet, registry


_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Firefox/102.0"


def _parse_proxy_url(
    proxy_url: str,
) -> tuple[str, str, int, Optional[str], Optional[str]]:
    """Parse proxy URL into components.

    Args:
        proxy_url: Proxy URL in format [scheme://][user:pass@]hostname:port

    Returns:
        Tuple of (proxy_type, host, port, username, password)

    Raises:
        ValueError: If URL format is invalid
    """
    parsed = urlparse(proxy_url)

    # Handle scheme
    if parsed.scheme:
        proxy_type = parsed.scheme.lower()
    else:
        proxy_type = "http"

    if proxy_type not in ("http", "socks4", "socks5"):
        raise ValueError(f"Unsupported proxy type: {proxy_type}")

    # Handle auth
    username = None
    password = None
    if "@" in parsed.netloc:
        auth, host_port = parsed.netloc.split("@", 1)
        if ":" in auth:
            username, password = auth.split(":", 1)
    else:
        host_port = parsed.netloc

    # Handle host/port
    if ":" not in host_port:
        raise ValueError("Proxy URL must include port number")

    host, port_str = host_port.rsplit(":", 1)
    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(f"Invalid port number: {port_str}")

    return proxy_type, host, port, username, password


def fetch(url: str, proxy_url: Optional[str] = None, **kwargs) -> str:
    """
    Fetch content from a URL with optional proxy support.

    Args:
        url: The URL to fetch
        proxy_url: Optional proxy URL in format [scheme://][user:pass@]hostname:port
                  Supported schemes: http, socks4, socks5
        **kwargs: Additional keyword arguments

    Returns:
        str: The decoded content from the URL

    Raises:
        ImportError: If SOCKS proxy is requested but PySocks is not installed
        ValueError: If invalid proxy configuration is provided
    """
    request = Request(url)
    request.add_header("User-Agent", _USER_AGENT)
    if "graphql" in url:
        request.add_header("Content-Type", "application/json")

    opener = None
    if proxy_url is not None:
        proxy_type, host, port, username, password = _parse_proxy_url(
            proxy_url
        )

        if proxy_type == "http":
            proxy_dict = {}
            auth = ""
            if username and password:
                auth = f"{username}:{password}@"
            proxy_url = f"http://{auth}{host}:{port}"
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            opener = build_opener(ProxyHandler(proxy_dict))
        else:  # socks4 or socks5
            if not SOCKS_AVAILABLE:
                raise ImportError(
                    "SOCKS proxy support requires the 'PySocks' package. "
                    "Install it with: pip install cinemagoerng[socks]"
                )
            socks_type = (
                socks.PROXY_TYPE_SOCKS4
                if proxy_type == "socks4"
                else socks.PROXY_TYPE_SOCKS5
            )
            opener = build_opener(
                SocksiPyHandler(
                    proxytype=socks_type,
                    proxyaddr=host,
                    proxyport=port,
                    username=username,
                    password=password,
                )
            )

    # Use the opener's open method if we have a proxy, otherwise use the default urlopen # noqa: E501
    url_opener = opener.open if opener is not None else urlopen

    with url_opener(request) as response:
        content: bytes = response.read()
    return content.decode("utf-8")


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
    proxy_url: Optional[str] = None,
    **kwargs,
) -> model.Title | None:
    spec = _spec(f"title_{page}")
    url_params = {"imdb_id": imdb_id} | spec.url_default_params | kwargs

    # Apply URL transform if specified
    if spec.url_transform:
        url = spec.url_transform.apply({"url": spec.url, "params": url_params})
    else:
        url = spec.url % url_params

    try:
        document = fetch(
            url,
            proxy_url=proxy_url,
            imdb_id=imdb_id,
            page=page,
            doc_type=spec.doctype,
            **kwargs,
        )
    except HTTPError as e:
        if e.status == HTTPStatus.NOT_FOUND:
            return None
        raise e  # pragma: no cover
    data = piculet.scrape(
        document,
        doctype=spec.doctype,
        rules=spec.rules,
        pre=spec.pre,
        post=spec.post,
    )
    return piculet.deserialize(data, model.Title)


def update_title(
    title: model.Title,
    /,
    *,
    page: TitleUpdatePage,
    keys: list[str],
    proxy_url: Optional[str] = None,
    paginate_result: bool = False,
    **kwargs,
) -> None:
    spec = _spec(f"title_{page}")
    url_params = {"imdb_id": title.imdb_id} | spec.url_default_params | kwargs

    if spec.url_transform:
        url = spec.url_transform.apply({"url": spec.url, "params": url_params})
    else:
        url = spec.url % url_params

    document = fetch(
        url,
        proxy_url=proxy_url,
        imdb_id=title.imdb_id,
        page=page,
        doc_type=spec.doctype,
        **kwargs,
    )
    data = piculet.scrape(
        document,
        doctype=spec.doctype,
        rules=spec.rules,
        pre=spec.pre,
        post=spec.post,
    )
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

    if paginate_result and data.get("has_next_page", False):
        kwargs["after"] = f'"{data["end_cursor"]}"'
        update_title(
            title,
            page=page,
            keys=keys,
            proxy_url=proxy_url,
            paginate_result=paginate_result,
            **kwargs,
        )
