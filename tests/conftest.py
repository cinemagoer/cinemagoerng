import json
from pathlib import Path
from urllib.parse import urlparse

import cinemagoerng.web

cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)

fetch_orig = cinemagoerng.web.fetch


CACHE_SUFFIXES = {
    "application/json": ".json",
    "text/html": ".html",
}

CACHE_KEY_IGNORED_VARS = {
    "isAutoTranslationEnabled",
    "locale",
    "originalTitleText",
}


def get_cache_key(url: str, *, headers: dict[str, str] | None = None) -> str:
    parsed = urlparse(url)
    path = parsed.path.replace("/", "_")
    if path.startswith("_"):
        path = path[1:]
    if path.endswith("_"):
        path = path[:-1]

    if len(parsed.query) > 0:
        query_params = parsed.query.split("&")
        for param in query_params:
            equals = param.index("=")
            g_key, g_value = param[:equals], param[equals + 1:]
            match g_key:
                case "operationName":
                    g_op = g_value
                case "variables":
                    g_vars = {
                        k: v for k, v in json.loads(g_value).items()
                        if k not in CACHE_KEY_IGNORED_VARS
                    }
                    imdb_id = g_vars.pop("const")
        if len(g_vars) > 0:
            g_query = "__".join(f"{k}_{v}" for k, v in g_vars.items())
            path += f"title_{imdb_id}_{g_op}__{g_query}"

    request_headers = headers if headers is not None else {}
    content_type = request_headers.get("Content-Type", "text/html")
    suffix = CACHE_SUFFIXES[content_type]
    return f"{path}{suffix}"


def fetch_cached(url: str, /, *, headers: dict[str, str] | None = None) -> str:
    cache_key = get_cache_key(url, headers=headers)
    cache_path = cache_dir / cache_key
    if cache_key == "title_tt0000001_reference.html":
        cache_path.unlink(missing_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    content = fetch_orig(url, headers=headers)
    cache_path.write_text(content, encoding="utf-8")
    return content


cinemagoerng.web.fetch = fetch_cached
