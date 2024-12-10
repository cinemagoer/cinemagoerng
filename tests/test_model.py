import pytest

from cinemagoerng.model import Credit, Movie


@pytest.mark.parametrize(
    ("imdb_id", "country_codes", "countries"),
    [
        (
            "tt0133093",
            ["US", "AU"],
            ["United States", "Australia"],
        ),  # The Matrix
        ("tt0389150", ["GB"], ["United Kingdom"]),  # The Matrix Defence
    ],
)
def test_title_countries_property_should_return_country_names(
    imdb_id, country_codes, countries
):
    movie = Movie(
        imdb_id=imdb_id, title="The Matrix", country_codes=country_codes
    )
    assert movie.countries == countries


@pytest.mark.parametrize(
    ("imdb_id", "title", "language_codes", "languages"),
    [
        ("tt0133093", "The Matrix", ["en"], ["English"]),
        (
            "tt0043338",
            "Ace in the Hole",
            ["en", "es", "la"],
            ["English", "Spanish", "Latin"],
        ),
        ("tt2971344", "Matrix: First Dream", ["zxx"], ["None"]),
    ],
)
def test_title_languages_property_should_return_language_names(
    imdb_id, title, language_codes, languages
):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.languages == languages


@pytest.mark.parametrize(
    ("imdb_id", "title", "language_codes", "sort_title"),
    [
        ("tt0133093", "The Matrix", ["en"], "Matrix"),
        ("tt0095016", "Die Hard", ["en"], "Die Hard"),
        ("tt0095016", "Die Hard", ["de"], "Hard"),  # language not true
        (
            "tt0068278",
            "Die bitteren Tränen der Petra von Kant",
            ["de"],
            "Bitteren Tränen der Petra von Kant",
        ),
        ("tt0429489", "A Ay", ["tr", "en", "it"], "A Ay"),
        (
            "tt0429489",
            "A Ay",
            ["en", "tr", "it"],
            "Ay",
        ),  # language order not true
        ("tt10277922", "The", ["en"], "The"),
    ],
)
def test_title_sort_title_property_should_strip_article(
    imdb_id, title, language_codes, sort_title
):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.sort_title == sort_title


@pytest.mark.parametrize(
    ("imdb_id", "name", "role", "notes", "as_name"),
    [
        (
            "nm0905152",
            "Lilly Wachowski",
            None,
            ["written by", "as The Wachowski Brothers"],
            "The Wachowski Brothers",
        ),
        ("nm0000309", "David Bowie", None, [], None),
    ],
)
def test_title_credit_as_name_property_should_return_bare_name(
    imdb_id, name, role, notes, as_name
):
    credit = Credit(imdb_id=imdb_id, name=name, role=role, notes=notes)
    assert credit.as_name == as_name


@pytest.mark.parametrize(
    ("imdb_id", "name", "role", "notes", "uncredited"),
    [
        (
            "nm0211063",
            "Thomas De Quincey",
            None,
            ['book "Suspiria de Profundis"', "uncredited"],
            True,
        ),
        (
            "nm0905152",
            "Lilly Wachowski",
            None,
            ["written by", "as The Wachowski Brothers"],
            False,
        ),
    ],
)
def test_title_uncredited_property_should_return_boolean(
    imdb_id, name, role, notes, uncredited
):
    credit = Credit(imdb_id=imdb_id, name=name, role=role, notes=notes)
    assert credit.uncredited == uncredited
