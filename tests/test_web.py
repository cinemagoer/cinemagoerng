import pytest

from cinemagoerng import web


@pytest.mark.skip(reason="get back to this after refactoring title updates")
@pytest.mark.parametrize(("imdb_id", "n"), [
    ("tt0133093", 15),  # The Matrix
])
def test_updating_title_should_update_only_given_keys(imdb_id, n):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.taglines) == 1
    web.update_title(parsed, page="taglines", keys=["taglines"])
    assert len(parsed.taglines) == n
