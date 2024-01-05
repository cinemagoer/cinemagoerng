import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "primary_image"), [
    ("tt0133093", "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX101_CR0,0,101,150_.jpg"),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_primary_image_from_thumbnail(imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.primary_image == primary_image


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
        ["screenplay"],
        ["screenplay"],
        ['book "Suspiria de Profundis"', "uncredited"],
    ]),
])
def test_title_reference_parser_should_set_multiple_credit_notes(imdb_id, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [credit.notes for credit in parsed.writers] == writers


@pytest.mark.parametrize(("imdb_id", "costume_dept"), [
    ("tt1000252", [  # Blink
        ("costume supervisor", None),
        ("costume assistant", None),
        ("costume assistant", "Bobby Peach"),
        ("costume prop maker", None),
    ]),
])
def test_title_reference_parser_should_set_credit_jobs(imdb_id, costume_dept):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert [(credit.job, credit.as_name)
            for credit in parsed.costume_department] == costume_dept
