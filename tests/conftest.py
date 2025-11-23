import copy
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
        q_vars: dict[str, str] = {}
        g_op: str | None = None
        for param in query_params:
            equals = param.index("=")
            q_key, q_value = param[:equals], param[equals + 1:]
            match q_key:
                case "operationName":
                    g_op = q_value
                case "variables":
                    q_vars = q_vars | {
                        k: v for k, v in json.loads(q_value).items()
                        if k not in CACHE_KEY_IGNORED_VARS
                    }
                case "extensions":
                    pass
                case _:
                    q_vars[q_key] = q_value
        if len(q_vars) > 0:
            if g_op is not None:
                imdb_id = q_vars.pop("const")
                path += f"title_{imdb_id}_{g_op}"
            q_query = "__".join(f"{k}_{v}" for k, v in q_vars.items())
            path += f"__{q_query}"

    request_headers = copy.copy(headers) if headers is not None else {}
    content_type = request_headers.pop("Content-Type", "text/html")
    suffix = CACHE_SUFFIXES[content_type]
    if len(request_headers) > 0:
        q_headers = "__".join(f"{k.lower()}_{v}" for k, v in request_headers.items())
        path += f"__{q_headers}"
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
