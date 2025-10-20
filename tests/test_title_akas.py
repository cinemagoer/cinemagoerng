import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "n_before", "n_after", "akas"), [
    ("tt0429489", 0, 3, [  # A Ay
        ("Луна", "SUHH", "Soviet Union", "ru", "Russian", False, []),
        ("Oh, Moon!", "US", "United States", None, None, True, ["literal English title"]),
        ("Oh, Moon!", "XWW", "World-wide", "en", "English", True, ["complete title"])
    ]),
    ("tt3629794", 0, 0, []),  # Aslan
    ("tt0133093", 0, 68, []),  # The Matrix
])
def test_title_akas_parser_should_set_all_paginated_akas(imdb_id, n_before, n_after, akas):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.akas) == n_before
    web.set_akas(parsed)
    assert len(parsed.akas) == n_after
    if len(akas) > 0:
        assert [(aka.title, aka.country_code, aka.country,
                 aka.language_code, aka.language,
                 aka.is_alternative, aka.notes)
                 for aka in parsed.akas] == akas
