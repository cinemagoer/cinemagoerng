import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "primary_image"), [
    ("tt0133093", "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX101_CR0,0,101,150_.jpg"),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_primary_image_from_thumbnail(imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(("imdb_id", "n", "cast"), [
    ("tt7045440", 1, [("nm0000309", "David Bowie")]),  # David Bowie: Ziggy Stardust
    ("tt0101597", 2, [("nm0000614", "Alan Rickman"), ("nm0000656", "Madeleine Stowe")]),  # Closet Land
    ("tt1000252", 12, []),  # Blink
    ("tt0133093", 41, []),  # The Matrix
    ("tt3629794", 0, []),  # Aslan
])
def test_title_reference_parser_should_set_all_cast(imdb_id, n, cast):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.cast) == n
    if len(cast) > 0:
        assert [(credit.imdb_id, credit.name) for credit in parsed.cast] == cast


@pytest.mark.parametrize(("imdb_id", "n", "directors"), [
    ("tt1000252", 1, [("nm0531751", "Hettie Macdonald")]),  # Blink
    ("tt0133093", 2, [("nm0905154", "Lana Wachowski"), ("nm0905152", "Lilly Wachowski")]),  # The Matrix
    ("tt0092580", 10, [  # Aria
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
    ("tt3629794", 0, []),  # Aslan
])
def test_title_reference_parser_should_set_all_credits(imdb_id, n, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.directors) == n
    if len(directors) > 0:
        assert [(credit.imdb_id, credit.name) for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "n", "directors"), [
    ("tt1000252", 1, [[]]),  # Blink
    ("tt0133093", 2, [[], []]),  # The Matrix
    ("tt0092580", 10, [  # Aria'
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
def test_title_reference_parser_should_set_credit_notes(imdb_id, n, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.directors) == n
    if len(directors) > 0:
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
