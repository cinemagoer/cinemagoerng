from pytest import mark

from cinemagoerng import web


def test_title_reference_parser_should_set_imdb_id():
    parsed = web.get_title_reference(imdb_id=133093)
    assert parsed.imdb_id == 133093


@mark.parametrize(("imdb_id", "title"),
                  [(133093, "The Matrix"),
                   (389150, "The Matrix Defence"),  # TV Movie
                   (109151, "Armitage III: Poly-Matrix"),  # Video
                   (390244, "The Matrix Online"),  # Video Game
                   (436992, "Doctor Who"),  # TV Series
                   (185906, "Band of Brothers"),  # TV Mini Series
                   (1000252, "Blink")])  # TV Episode
def test_title_reference_parser_should_set_title(imdb_id, title):
    parsed = web.get_title_reference(imdb_id=imdb_id)
    assert parsed.title == title


@mark.parametrize(("imdb_id", "year"),
                  [(133093, 1999),  # The Matrix
                   (436992, 2005),  # Doctor Who (2005-)
                   (185906, 2001),  # Band of Brothers (2001-2001)
                   (412142, 2004),  # House M.D. (2004-2012)
                   (3629794, None)])  # Aslan
def test_title_reference_parser_should_set_year(imdb_id, year):
    parsed = web.get_title_reference(imdb_id=imdb_id)
    assert parsed.year == year


@mark.parametrize(("imdb_id", "end_year"),
                  [(133093, None),  # The Matrix
                   (436992, None),  # Doctor Who (2005-)
                   (185906, 2001),  # Band of Brothers (2001-2001)
                   (412142, 2012)])  # House M.D. (2004-2012)
def test_title_reference_parser_should_set_end_year(imdb_id, end_year):
    parsed = web.get_title_reference(imdb_id=imdb_id)
    assert parsed.end_year == end_year
