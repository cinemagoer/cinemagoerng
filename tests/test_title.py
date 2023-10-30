from pytest import mark

from cinemagoerng import model, web


def test_title_parser_should_set_imdb_id():
    parsed = web.get_title(imdb_id=133093)
    assert parsed.imdb_id == 133093


@mark.parametrize(("imdb_id", "type_"),
                  [(133093, model.Movie),  # The Matrix
                   (389150, model.TVMovie),  # The Matrix Defence
                   (109151, model.Video),  # Armitage III: Poly-Matrix
                   (390244, model.VideoGame),  # The Matrix Online
                   (436992, model.TVSeries),  # Doctor Who
                   (185906, model.TVMiniSeries),  # Band of Brothers
                   (1000252, model.TVEpisode)])  # Blink
def test_title_parser_should_instantiate_correct_type(imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id)
    assert isinstance(parsed, type_)


@mark.parametrize(("imdb_id", "title"),
                  [(133093, "The Matrix"),
                   (389150, "The Matrix Defence"),
                   (109151, "Armitage III: Poly-Matrix"),
                   (390244, "The Matrix Online"),
                   (436992, "Doctor Who"),
                   (185906, "Band of Brothers"),
                   (1000252, "Blink")])
def test_title_parser_should_set_title(imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.title == title


@mark.parametrize(("imdb_id", "year"),
                  [(133093, 1999),  # The Matrix
                   (436992, 2005),  # Doctor Who (2005-)
                   (185906, 2001),  # Band of Brothers (2001-2001)
                   (412142, 2004),  # House M.D. (2004-2012)
                   (3629794, None)])  # Aslan
def test_title_parser_should_set_year(imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.year == year


@mark.parametrize(("imdb_id", "end_year"),
                  [(436992, None),  # Doctor Who (2005-)
                   (185906, 2001),  # Band of Brothers (2001-2001)
                   (412142, 2012)])  # House M.D. (2004-2012)
def test_title_parser_should_set_end_year(imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.end_year == end_year


@mark.parametrize(("imdb_id",),
                  [(133093,),  # The Matrix
                   (389150,)])  # The Matrix Defence
def test_title_parser_should_set_end_year_only_for_series(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id)
    assert not hasattr(parsed, "end_year")
