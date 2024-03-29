from pathlib import Path

import cinemagoerng.web


cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)


fetch_orig = cinemagoerng.web.fetch


def fetch_cached(url):
    cache_filename = "__".join(url.split("/")[3:]).replace("?", "_")
    if cache_filename.endswith("__"):
        cache_filename = cache_filename[:-2]
    cache_path = cache_dir / cache_filename
    if cache_filename == "title__tt0000001":
        cache_path.unlink(missing_ok=True)
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")
    content = fetch_orig(url)
    cache_path.write_text(content, encoding="utf-8")
    return content


cinemagoerng.web.fetch = fetch_cached
