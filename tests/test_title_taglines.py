import pytest

from cinemagoerng import web as imdb


@pytest.mark.parametrize(("imdb_id", "n_before", "n_after", "taglines"), [
    ("tt0133093", 1, 15, ["Free your mind", "Remember there is no spoon"]),  # The Matrix
    ("tt0109151", 1, 1, ["If humans don't want me... why'd they create me?"]),  # Armitage III: Poly-Matrix
    ("tt3629794", 0, 0, []),  # Aslan
])
def test_title_taglines_parser_should_set_taglines(imdb_id, n_before, n_after, taglines):
    parsed = imdb.get_title(imdb_id=imdb_id)
    assert len(parsed.taglines) == n_before
    imdb.set_taglines(parsed)
    assert len(parsed.taglines) == n_after
    assert set(parsed.taglines).issuperset(set(taglines))
