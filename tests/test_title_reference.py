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
def test_title_reference_parser_should_set_all_credits(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.imdb_id, credit.name) for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "directors"), [
    ("tt1000252", [[]]),  # Blink
    ("tt0133093", [[], []]),  # The Matrix
    ("tt0092580", [  # Aria'
        ['segment "Les Boréades"'],
        ['segment "Die tote Stadt"'],
        ['segment "I pagliacci"'],
        ['segment "Armide"'],
        ['segment "Depuis le jour"'],
        ['segment "Liebestod"'],
        ['segment "Un ballo in maschera"'],
        ['segment "Nessun dorma"'],
        ['segment "La virgine degli angeli"'],
        ['segment "Rigoletto"'],
    ]),
])
def test_title_reference_parser_should_set_credit_notes(imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [credit.notes for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "writers"), [
    ("tt0076786", [  # Suspiria
        (False, ["screenplay"]),
        (False, ["screenplay"]),
        (True, ['book "Suspiria de Profundis"']),
    ]),
])
def test_title_reference_parser_should_remove_uncredited_from_notes(imdb_id, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.uncredited, credit.notes) for credit in parsed.writers] == writers


@pytest.mark.parametrize(("imdb_id", "costume_dept"), [
    ("tt1000252", [  # Blink
        ("costume supervisor", None, False),
        ("costume assistant", None, False),
        ("costume assistant", "Bobby Peach", False),
        ("costume prop maker", None, True),
    ]),
])
def test_title_reference_parser_should_set_credit_jobs(imdb_id, costume_dept):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.job, credit.as_name, credit.uncredited)
            for credit in parsed.costume_department] == costume_dept
