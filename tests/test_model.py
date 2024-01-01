import pytest

from cinemagoerng.model import Movie


@pytest.mark.parametrize(("imdb_id", "country_codes", "countries"), [
    ("tt0133093", ["US", "AU"], ["United States", "Australia"]),  # The Matrix
    ("tt0389150", ["GB"], ["United Kingdom"]),  # The Matrix Defence
])
def test_title_countries_property_should_return_country_names(imdb_id, country_codes, countries):
    movie = Movie(imdb_id=imdb_id, title="The Matrix", country_codes=country_codes)
    assert movie.countries == countries


@pytest.mark.parametrize(("imdb_id", "title", "language_codes", "languages"), [
    ("tt0133093", "The Matrix", ["en"], ["English"]),
    ("tt0043338", "Ace in the Hole", ["en", "es", "la"], ["English", "Spanish", "Latin"]),
    ("tt2971344", "Matrix: First Dream", ["zxx"], ["None"]),
])
def test_title_languages_property_should_return_language_names(imdb_id, title, language_codes, languages):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.languages == languages


@pytest.mark.parametrize(("imdb_id", "title", "language_codes", "sort_title"), [
    ("tt0133093", "The Matrix", ["en"], "Matrix"),
    ("tt0133093", "The Matrix", ["de"], "The Matrix"),
    ("tt0133093", "Die Matrix", ["en"], "Die Matrix"),
    ("tt0133093", "Die Matrix", ["de"], "Matrix"),
    ("tt0133093", "The Matrix", ["en", "de"], "Matrix"),
    ("tt0133093", "The Matrix", ["de", "en"], "The Matrix"),
    ("tt0133093", "The", ["en"], "The"),
])
def test_title_sort_title_property_should_strip_article(imdb_id, title, language_codes, sort_title):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.sort_title == sort_title
