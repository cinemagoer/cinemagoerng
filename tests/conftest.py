import os
from pathlib import Path
from typing import Optional

import cinemagoerng.web


def load_env() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


# Load environment variables at startup
load_env()

# Setup cache directory
cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)

fetch_orig = cinemagoerng.web.fetch


def fetch_cached(url: str, imdb_id: str, page: str, doc_type: str, **kwargs) -> str:
    """
    Cached version of fetch that supports proxy configuration from environment.
    """
    # Get proxy from environment if not explicitly provided
    proxy_url: Optional[str] = kwargs.get("proxy_url") or os.getenv("IMDB_PROXY_URL")
    if proxy_url:
        kwargs["proxy_url"] = proxy_url
    else:
        kwargs.pop("proxy_url", None)

    # Generate cache key
    key = f"title_{imdb_id}_{page}"
    # Remove proxy from cache key to ensure same cache for proxy/non-proxy
    extra_args = [f"{k}={v}" for k, v in kwargs.items() if k != "proxy_url"]
    key += "_" + "_".join(extra_args) if extra_args else ""
    key += f".{doc_type}"

    cache_path = cache_dir / key

    # Special case handling
    if key == "tt0000001_main.html":
        cache_path.unlink(missing_ok=True)

    # Return cached content if available
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    # Fetch new content
    content = fetch_orig(url, **kwargs)
    cache_path.write_text(content, encoding="utf-8")
    return content


# Replace original fetch with cached version
cinemagoerng.web.fetch = fetch_cached
