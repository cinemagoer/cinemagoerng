import pytest

from cinemagoerng.model import AKA, CrewCredit, Movie, Person


@pytest.mark.parametrize(("imdb_id", "title", "country_codes", "countries"), [
    ("tt0133093", "The Matrix", ["US", "AU"], ["United States", "Australia"]),
    ("tt0389150", "The Matrix Defence", ["GB"], ["United Kingdom"]),
])
def test_title_countries_should_return_country_names(imdb_id, title, country_codes, countries):
    movie = Movie(imdb_id=imdb_id, title=title, country_codes=country_codes)
    assert movie.countries == countries


@pytest.mark.parametrize(("imdb_id", "title", "language_codes", "languages"), [
    ("tt0133093", "The Matrix", ["en"], ["English"]),
    ("tt0043338", "Ace in the Hole", ["en", "es", "la"], ["English", "Spanish", "Latin"]),
    ("tt2971344", "Matrix: First Dream", ["zxx"], ["None"]),
])
def test_title_languages_should_return_language_names(imdb_id, title, language_codes, languages):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.languages == languages


@pytest.mark.parametrize(("imdb_id", "title", "language_codes", "sort_title"), [
    ("tt0133093", "The Matrix", ["en"], "Matrix"),
    ("tt0095016", "Die Hard", ["en"], "Die Hard"),
    ("tt0095016", "Die Hard", ["de"], "Hard"),  # language not true
    ("tt0068278", "Die bitteren Tränen der Petra von Kant", ["de"], "Bitteren Tränen der Petra von Kant"),
    ("tt0429489", "A Ay", ["tr", "en", "it"], "A Ay"),
    ("tt0429489", "A Ay", ["en", "tr", "it"], "Ay"),  # language order not true
    ("tt10277922", "The", ["en"], "The"),
])
def test_title_sort_title_should_strip_article(imdb_id, title, language_codes, sort_title):
    movie = Movie(imdb_id=imdb_id, title=title, language_codes=language_codes)
    assert movie.sort_title == sort_title


@pytest.mark.parametrize(("title", "country_code", "country"), [
    ("Луна", "SUHH", "Soviet Union"),
    ("DUMMY", None, None),
])
def test_title_aka_countries_should_return_country_names(title, country_code, country):
    aka = AKA(title=title, country_code=country_code)
    assert aka.country == country


@pytest.mark.parametrize(("title", "language_code", "language"), [
    ("Луна", "ru", "Russian"),
    ("DUMMY", None, None),
])
def test_title_aka_languages_should_return_language_names(title, language_code, language):
    aka = AKA(title=title, language_code=language_code)
    assert aka.language == language


@pytest.mark.parametrize(("imdb_id", "name"), [
    ("nm0905152", "Lilly Wachowski"),
    ("nm0000309", "David Bowie"),
])
def test_title_credit_imdb_id_should_return_person_imdb_id(imdb_id, name):
    credit = CrewCredit(Person(imdb_id=imdb_id, name=name))
    assert credit.imdb_id == imdb_id


@pytest.mark.parametrize(("imdb_id", "name"), [
    ("nm0905152", "Lilly Wachowski"),
    ("nm0000309", "David Bowie"),
])
def test_title_credit_name_should_return_person_name(imdb_id, name):
    credit = CrewCredit(Person(imdb_id=imdb_id, name=name))
    assert credit.name == name


@pytest.mark.parametrize(("imdb_id", "name", "notes", "as_name"), [
    ("nm0905152", "Lilly Wachowski", ["written by", "as The Wachowski Brothers"], "The Wachowski Brothers"),
    ("nm0000309", "David Bowie", [], None),
])
def test_title_credit_as_name_should_return_just_name(imdb_id, name, notes, as_name):
    credit = CrewCredit(Person(imdb_id=imdb_id, name=name), notes=notes)
    assert credit.as_name == as_name


@pytest.mark.parametrize(("imdb_id", "name", "notes", "uncredited"), [
    ("nm0211063", "Thomas De Quincey", ['book "Suspiria de Profundis"', "uncredited"], True),
    ("nm0905152", "Lilly Wachowski", ["written by", "as The Wachowski Brothers"], False),
])
def test_title_uncredited_should_return_boolean(imdb_id, name, notes, uncredited):
    credit = CrewCredit(Person(imdb_id=imdb_id, name=name), notes=notes)
    assert credit.uncredited == uncredited
