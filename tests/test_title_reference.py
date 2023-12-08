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
    assert [(credit.imdb_id, credit.name) for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "directors"), [
    ("tt1000252", [(None, [])]),  # Blink
    ("tt0133093", [  # The Matrix
        ("The Wachowski Brothers", []),
        ("The Wachowski Brothers", []),
    ]),
    ("tt0092580", [  # Aria'
        (None, ['segment "Les Boréades"']),
        (None, ['segment "Die tote Stadt"']),
        (None, ['segment "I pagliacci"']),
        (None, ['segment "Armide"']),
        (None, ['segment "Depuis le jour"']),
        (None, ['segment "Liebestod"']),
        (None, ['segment "Un ballo in maschera"']),
        (None, ['segment "Nessun dorma"']),
        (None, ['segment "La virgine degli angeli"']),
        (None, ['segment "Rigoletto"']),
    ]),
])
def test_title_reference_parser_should_set_director_info(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.as_name, credit.notes) for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "writers"), [
    ("tt7045440", [("nm0000309", "David Bowie")]),  # David Bowie: Ziggy Stardust
    ("tt0133093", [("nm0905152", "Lilly Wachowski"), ("nm0905154", "Lana Wachowski")]),  # The Matrix
    ("tt0076786", [  # Suspiria
        ("nm0000783", "Dario Argento"),
        ("nm0630453", "Daria Nicolodi"),
        ("nm0211063", "Thomas De Quincey"),
    ]),
    ("tt0365467", []),  # Making 'The Matrix'
])
def test_title_reference_parser_should_set_all_writers(imdb_id, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.imdb_id, credit.name) for credit in parsed.writers] == writers


@pytest.mark.parametrize(("imdb_id", "writers"), [
    ("tt7045440", [(None, [])]),  # David Bowie: Ziggy Stardust
    ("tt0133093", [  # The Matrix
        ("The Wachowski Brothers", ["written by"]),
        ("The Wachowski Brothers", ["written by"]),
    ]),
    ("tt0076786", [  # Suspiria
        (None, ["screenplay"]),
        (None, ["screenplay"]),
        (None, ['book "Suspiria de Profundis"', "uncredited"]),
    ]),
])
def test_title_reference_parser_should_set_writer_info(imdb_id, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.as_name, credit.notes) for credit in parsed.writers] == writers
