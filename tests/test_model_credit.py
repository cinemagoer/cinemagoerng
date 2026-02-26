import pytest

from cinemagoerng.credit import Credit
from cinemagoerng.person import Person


@pytest.mark.parametrize(("imdb_id", "name"), [
    ("nm0905152", "Lilly Wachowski"),
    ("nm0000309", "David Bowie"),
])
def test_credit_imdb_id_should_return_person_imdb_id(imdb_id, name):
    credit = Credit(Person(imdb_id=imdb_id, name=name))
    assert credit.imdb_id == imdb_id


@pytest.mark.parametrize(("imdb_id", "name"), [
    ("nm0905152", "Lilly Wachowski"),
    ("nm0000309", "David Bowie"),
])
def test_credit_name_should_return_person_name(imdb_id, name):
    credit = Credit(Person(imdb_id=imdb_id, name=name))
    assert credit.name == name


@pytest.mark.parametrize(("imdb_id", "name", "notes", "as_name"), [
    ("nm0905152", "Lilly Wachowski", ["written by", "as The Wachowski Brothers"], "The Wachowski Brothers"),
    ("nm0000309", "David Bowie", [], None),
])
def test_credit_as_name_should_return_name_without_as(imdb_id, name, notes, as_name):
    credit = Credit(Person(imdb_id=imdb_id, name=name), notes=notes)
    assert credit.as_name == as_name


@pytest.mark.parametrize(("imdb_id", "name", "notes", "uncredited"), [
    ("nm0211063", "Thomas De Quincey", ['book "Suspiria de Profundis"', "uncredited"], True),
    ("nm0905152", "Lilly Wachowski", ["written by", "as The Wachowski Brothers"], False),
])
def test_uncredited_should_return_boolean(imdb_id, name, notes, uncredited):
    credit = Credit(Person(imdb_id=imdb_id, name=name), notes=notes)
    assert credit.uncredited == uncredited
