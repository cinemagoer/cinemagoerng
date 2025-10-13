from pathlib import Path

import cinemagoerng.web

cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)

fetch_orig = cinemagoerng.web.fetch


def fetch_cached(url: str, imdb_id: str, page: str, doc_type: str, **kwargs):
    key = f"title_{imdb_id}_{page}"
    extra_args = [f"{k}={v}" for k, v in kwargs.items()]
    key += "_" + "_".join(extra_args) if extra_args else ""
    key += f".{doc_type}"
    cache_path = cache_dir / key
    if key == "tt0000001_main.html":
        cache_path.unlink(missing_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    content = fetch_orig(url)
    cache_path.write_text(content, encoding="utf-8")
    return content


cinemagoerng.web.fetch = fetch_cached
