from pytest import mark

from cinemagoerng import model, web


def test_title_parser_should_set_imdb_id():
    parsed = web.get_title(imdb_id=133093)
    assert parsed.imdb_id == 133093


@mark.parametrize(("imdb_id", "type_"), [
    (133093, model.Movie),  # The Matrix
    (389150, model.TVMovie),  # The Matrix Defence
    (2971344, model.ShortMovie),  # Matrix: First Dream
    (365467, model.TVShortMovie),  # Making 'The Matrix'
    (109151, model.VideoMovie),  # Armitage III: Poly-Matrix
    (7045440, model.MusicVideo),  # David Bowie: Ziggy Stardust
    (390244, model.VideoGame),  # The Matrix Online
    (436992, model.TVSeries),  # Doctor Who
    (185906, model.TVMiniSeries),  # Band of Brothers
    (1000252, model.TVEpisode),  # Blink
    (14544192, model.TVSpecial),  # Bo Burnham: Inside
])
def test_title_parser_should_instantiate_correct_type(imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id)
    assert isinstance(parsed, type_)


@mark.parametrize(("imdb_id", "title"), [
    (133093, "The Matrix"),
    (389150, "The Matrix Defence"),
    (2971344, "Matrix: First Dream"),
    (365467, "Making 'The Matrix'"),
    (109151, "Armitage III: Poly-Matrix"),
    (7045440, "David Bowie: Ziggy Stardust"),
    (390244, "The Matrix Online"),
    (436992, "Doctor Who"),
    (185906, "Band of Brothers"),
    (1000252, "Blink"),
    (14544192, "Bo Burnham: Inside"),
])
def test_title_parser_should_set_title(imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.title == title


@mark.parametrize(("imdb_id", "year"), [
    (133093, 1999),  # The Matrix
    (436992, 2005),  # Doctor Who (2005-)
    (412142, 2004),  # House M.D. (2004-2012)
    (185906, 2001),  # Band of Brothers (2001-2001)
    (3629794, None),  # Aslan
])
def test_title_parser_should_set_year(imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.year == year


@mark.parametrize(("imdb_id", "end_year"), [
    (436992, None),  # Doctor Who (2005-)
    (412142, 2012),  # House M.D. (2004-2012)
    (185906, 2001),  # Band of Brothers (2001-2001) (TV Mini-Series)
])
def test_title_parser_should_set_end_year(imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.end_year == end_year


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix (Movie)
    (389150,),  # The Matrix Defence (TV Movie)
    (2971344,),  # Matrix: First Dream (Short Movie)
    (365467,),  # Making 'The Matrix' (TV Short Movie)
    (109151,),  # Armitage III: Poly-Matrix (Video Movie)
    (7045440,),  # David Bowie: Ziggy Stardust (Music Video)
    (390244,),  # The Matrix Online (Video Game)
    (1000252,),  # Blink (TV Series Episode)
    (14544192,),  # Bo Burnham: Inside
])
def test_title_parser_should_not_set_end_year_for_other_than_series(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id)
    assert not hasattr(parsed, "end_year")


@mark.parametrize(("imdb_id", "runtime"), [
    (133093, 136),  # The Matrix (Movie)
    (2971344, 28),  # Matrix: First Dream (Short Movie)
    (365467, 26),  # Making 'The Matrix' (TV Short Movie)
    (7045440, 3),  # David Bowie: Ziggy Stardust (Music Video)
    (436992, 45),  # Doctor Who (TV Series)
    (185906, 594),  # Band of Brothers (TV Mini-Series)
    (3629794, None),  # Aslan
])
def test_title_parser_should_set_runtime(imdb_id, runtime):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.runtime == runtime


@mark.parametrize(("imdb_id",), [
    (390244,),  # The Matrix Online
])
def test_title_parser_should_not_set_runtime_for_video_games(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id)
    assert not hasattr(parsed, "runtime")


@mark.parametrize(("imdb_id", "genres"), [
    (133093, ["Action", "Sci-Fi"]),  # The Matrix
    (389150, ["Documentary"]),  # The Matrix Defence
    (2971344, ["Short"]),  # Matrix: First Dream (Short Movie)
    (365467, ["Documentary", "Short", "Sci-Fi"]),  # Making 'The Matrix' (TV Short Movie)
    (109151, ["Animation", "Action", "Drama", "Sci-Fi", "Thriller"]),  # Armitage III: Poly-Matrix (Video Movie)
    (7045440, ["Short", "Music"]),  # David Bowie: Ziggy Stardust (Music Video)
    (390244, ["Action", "Adventure", "Sci-Fi"]),  # The Matrix Online (Video Game)
    (436992, ["Adventure", "Drama", "Sci-Fi"]),  # Doctor Who (TV Series)
    (185906, ["Drama", "History", "War"]),  # Band of Brothers (TV Mini-Series)
    (1000252, ["Adventure", "Drama", "Sci-Fi"]),  # Blink (TV Series Episode)
    (14544192, ["Documentary", "Comedy", "Drama", "Music"]),  # Bo Burnham: Inside
])
def test_title_parser_should_set_genres(imdb_id, genres):
    parsed = web.get_title(imdb_id=imdb_id)
    assert parsed.genres == genres
