import hashlib
from pathlib import Path

import cinemagoerng.web


cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)


fetch_orig = cinemagoerng.web.fetch


def fetch_cached(url, key):
    cache_path = cache_dir / key
    if "?season=" in url:
        season = url.split("?season=")[-1]
        suffix = cache_path.suffix
        cache_path = cache_path.with_suffix(f".season{season}{suffix}")
    if key == "tt0000001_main.html":
        cache_path.unlink(missing_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    content = fetch_orig(url)
    cache_path.write_text(content, encoding="utf-8")
    return content


cinemagoerng.web.fetch = fetch_cached
