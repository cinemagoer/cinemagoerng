import pytest

from cinemagoerng import web as imdb


@pytest.mark.parametrize(("imdb_id", "n_before", "n_after", "akas"), [
    ("tt0429489", 0, 10, [  # A Ay
        ("Oh, Moon!", "AU", "Australia", None, None, []),
        ("Oh, Moon!", "CA", "Canada", "en", "English", []),
        ("A Ay", "DE", "Germany", None, None, []),
        ("Oh, Moon!", "IN", "India", "en", "English", []),
        ("Oh, Moon!", "IE", "Ireland", "en", "English", []),
        ("Oh, Moon!", "NZ", "New Zealand", "en", "English", []),
        ("Луна", "SUHH", "Soviet Union", "ru", "Russian", []),
        ("Oh, Moon!", "GB", "United Kingdom", None, None, []),
        ("Oh, Moon!", "US", "United States", None, None, ["literal English title"]),
        ("Oh, Moon!", "XWW", "World-wide", "en", "English", ["complete title"])
    ]),
    ("tt3629794", 0, 0, []),  # Aslan
    ("tt0133093", 0, 68, []),  # The Matrix
])
def test_title_akas_parser_should_set_all_akas_on_update(imdb_id, n_before, n_after, akas):
    parsed = imdb.get_title(imdb_id=imdb_id)
    assert len(parsed.akas) == n_before
    imdb.set_akas(parsed)
    assert len(parsed.akas) == n_after
    if len(akas) > 0:
        assert [(aka.title, aka.country_code, aka.country, aka.language_code, aka.language, aka.notes)
                for aka in parsed.akas] == akas
