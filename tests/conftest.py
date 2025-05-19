import hashlib
from pathlib import Path
from typing import Any, Optional

import cinemagoerng.web


# Setup cache directory
cache_dir = Path(__file__).parent / "imdb-cache"
if not cache_dir.exists():
    cache_dir.mkdir(parents=True, exist_ok=True)


class CachedHTTPClient(cinemagoerng.web.HTTPClient):
    """HTTP client with caching support for both sync and async operations."""

    def _get_cache_key(self, url: str, **kwargs) -> tuple[str, Path]:
        """Generate cache key and path for the request."""
        imdb_id = kwargs.get("imdb_id")
        page = kwargs.get("page")
        doc_type = kwargs.get("doc_type", "html")

        # Generate cache key
        key = f"title_{imdb_id}_{page}" if imdb_id and page else "search"

        # Remove httpx kwargs and internal params from cache key
        cache_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ("httpx_kwargs", "doc_type", "imdb_id", "page")
        }
        extra_args = [f"{k}={v}" for k, v in sorted(cache_kwargs.items())]
        key += "_" + "_".join(extra_args) if extra_args else ""

        if len(key) > 30:
            hash_key = hashlib.md5(url.encode()).hexdigest()
            key = f"{key[:30]}_{hash_key[:10]}"
        key += f".{doc_type}"

        cache_path = cache_dir / key
        return key, cache_path

    def _read_cache(self, cache_path: Path) -> Optional[str]:
        """Read content from cache if available."""
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
        return None

    def _write_cache(self, cache_path: Path, content: str) -> None:
        """Write content to cache."""
        cache_path.write_text(content, encoding="utf-8")

    def fetch(
        self,
        url: str,
        **kwargs: Any,
    ) -> str:
        """Synchronous fetch with caching support."""
        # Handle special test cases
        key, cache_path = self._get_cache_key(url, **kwargs)
        if key == "tt0000001_main.html":
            cache_path.unlink(missing_ok=True)

        cached_content = self._read_cache(cache_path)
        if cached_content is not None:
            return cached_content

        # Fetch content
        content = super().fetch(url, **kwargs)

        self._write_cache(cache_path, content)

        return content

    async def fetch_async(
        self,
        url: str,
        **kwargs: Any,
    ) -> str:
        """Asynchronous fetch with caching support."""
        # Handle special test cases
        key, cache_path = self._get_cache_key(url, **kwargs)
        if key == "tt0000001_main.html":
            cache_path.unlink(missing_ok=True)

        cached_content = self._read_cache(cache_path)
        if cached_content is not None:
            return cached_content

        # Fetch content
        content = await super().fetch_async(url, **kwargs)

        self._write_cache(cache_path, content)

        return content


# Replace original HTTP client with cached version
cinemagoerng.web._http_client = CachedHTTPClient()
