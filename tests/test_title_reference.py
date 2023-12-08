import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "directors"), [
    ("tt0133093", ["The Wachowski Brothers", "The Wachowski Brothers"]),  # The Matrix
    ("tt1000252", [None]),  # Blink
])
def test_title_reference_parser_should_set_director_as_names(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [d.as_name for d in parsed.directors] == directors
