import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "directors"), [
    ("tt1000252", [("nm0531751", "Hettie Macdonald")]),  # Blink
    ("tt0133093", [("nm0905154", "Lana Wachowski"), ("nm0905152", "Lilly Wachowski"),]),  # The Matrix
    ("tt0092580", [  # Aria
        ("nm0000265", "Robert Altman"),
        ("nm0000915", "Bruce Beresford"),
        ("nm0117317", "Bill Bryden"),
        ("nm0000419", "Jean-Luc Godard"),
        ("nm0418746", "Derek Jarman"),
        ("nm0734466", "Franc Roddam"),
        ("nm0001676", "Nicolas Roeg"),
        ("nm0001692", "Ken Russell"),
        ("nm0836430", "Charles Sturridge"),
        ("nm0854697", "Julien Temple"),
    ]),
    ("tt3629794", []),  # Aslan
])
def test_title_reference_parser_should_set_all_directors(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(d.imdb_id, d.name) for d in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "directors"), [
    ("tt1000252", [None]),  # Blink
    ("tt0133093", ["The Wachowski Brothers", "The Wachowski Brothers"]),  # The Matrix
    ("tt0092580", [None] * 10),  # Aria
])
def test_title_reference_parser_should_set_director_as_names(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [d.as_name for d in parsed.directors] == directors
