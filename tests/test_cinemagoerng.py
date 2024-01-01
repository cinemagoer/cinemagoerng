from importlib import metadata

import pytest

import cinemagoerng
from cinemagoerng.model import Movie


def test_installed_version_should_match_tested_version():
    assert metadata.version("cinemagoerng") == cinemagoerng.__version__


@pytest.mark.parametrize(("imdb_id", "country_codes", "countries"), [
    ("tt0133093", ["US", "AU"], ["United States", "Australia"]),  # The Matrix
    ("tt0389150", ["GB"], ["United Kingdom"]),  # The Matrix Defence
])
def test_title_countries_property_should_return_country_names(imdb_id, country_codes, countries):
    movie = Movie(imdb_id=imdb_id, type_id="movie", title="The Matrix", country_codes=country_codes)
    assert movie.countries == countries


@pytest.mark.parametrize(("imdb_id", "language_codes", "languages"), [
    ("tt0133093", ["en"], ["English"]),  # The Matrix
    ("tt0043338", ["en", "es", "la"], ["English", "Spanish", "Latin"]),  # Ace in the Hole
    ("tt2971344", ["zxx"], ["None"]),  # Matrix: First Dream
])
def test_title_languages_property_should_return_language_names(imdb_id, language_codes, languages):
    movie = Movie(imdb_id=imdb_id, type_id="movie", title="The Matrix", language_codes=language_codes)
    assert movie.languages == languages
