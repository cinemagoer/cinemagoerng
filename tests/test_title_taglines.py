import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "n", "taglines"), [
    ("tt0133093", 15, ["Free your mind", "Remember there is no spoon"]),  # The Matrix
    ("tt0109151", 1, ["If humans don't want me... why'd they create me?"]),  # Armitage III: Poly-Matrix
    ("tt3629794", 0, []),  # Aslan
])
def test_title_taglines_parser_should_set_taglines(imdb_id, n, taglines):
    parsed = web.get_title(imdb_id=imdb_id, page="taglines")
    assert len(parsed.taglines) == n
    assert set(parsed.taglines).issuperset(set(taglines))


@pytest.mark.parametrize(("imdb_id", "n_before", "n_after"), [
    ("tt0133093", 1, 15),  # The Matrix
])
def test_title_taglines_parser_should_set_all_taglines_on_update(imdb_id, n_before, n_after):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.taglines) == n_before
    parsed.set_taglines()
    assert len(parsed.taglines) == n_after
