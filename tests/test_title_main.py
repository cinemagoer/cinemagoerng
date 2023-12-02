from pytest import mark

from decimal import Decimal

from cinemagoerng import model, web


def test_title_parser_should_set_imdb_id():
    parsed = web.get_title(imdb_id="tt0133093")
    assert parsed.imdb_id == "tt0133093"


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "type_"), [
    ("tt0133093", model.Movie),  # The Matrix
    ("tt0389150", model.TVMovie),  # The Matrix Defence
    ("tt2971344", model.ShortMovie),  # Matrix: First Dream
    ("tt0365467", model.TVShortMovie),  # Making 'The Matrix'
    ("tt0109151", model.VideoMovie),  # Armitage III: Poly-Matrix
    ("tt7045440", model.MusicVideo),  # David Bowie: Ziggy Stardust
    ("tt0390244", model.VideoGame),  # The Matrix Online
    ("tt0436992", model.TVSeries),  # Doctor Who
    ("tt0185906", model.TVMiniSeries),  # Band of Brothers
    ("tt1000252", model.TVEpisode),  # Blink
    ("tt0261024", model.TVSpecial),  # Live Aid
])
def test_title_parser_should_instantiate_correct_type(page, imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert isinstance(parsed, type_)


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "title"), [
    ("tt0133093", "The Matrix"),
    ("tt0389150", "The Matrix Defence"),
    ("tt2971344", "Matrix: First Dream"),
    ("tt0365467", "Making 'The Matrix'"),
    ("tt0109151", "Armitage III: Poly-Matrix"),
    ("tt7045440", "David Bowie: Ziggy Stardust"),
    ("tt0390244", "The Matrix Online"),
    ("tt0436992", "Doctor Who"),
    ("tt0810788", "Burn Notice"),
    ("tt0185906", "Band of Brothers"),
    ("tt1000252", "Blink"),
    ("tt0261024", "Live Aid"),
])
def test_title_parser_should_set_title_from_original_title(page, imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.title == title


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "year"), [
    ("tt0133093", 1999),  # The Matrix
    ("tt0436992", 2005),  # Doctor Who (2005-)
    ("tt0412142", 2004),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001)
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_year(page, imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.year == year


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "end_year"), [
    ("tt0436992", None),  # Doctor Who (2005-)
    ("tt0412142", 2012),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001) (TV Mini-Series)
])
def test_title_parser_should_set_end_year(page, imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.end_year == end_year


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id",), [
    ("tt0133093",),  # The Matrix (Movie)
    ("tt0389150",),  # The Matrix Defence (TV Movie)
    ("tt2971344",),  # Matrix: First Dream (Short Movie)
    ("tt0365467",),  # Making 'The Matrix' (TV Short Movie)
    ("tt0109151",),  # Armitage III: Poly-Matrix (Video Movie)
    ("tt7045440",),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0390244",),  # The Matrix Online (Video Game)
    ("tt1000252",),  # Blink (TV Series Episode)
    ("tt0261024",),  # Live Aid
])
def test_title_parser_should_not_set_end_year_for_other_than_series(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert not hasattr(parsed, "end_year")


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "runtime"), [
    ("tt0133093", 136),  # The Matrix (Movie)
    ("tt2971344", 28),  # Matrix: First Dream (Short Movie)
    ("tt0365467", 26),  # Making 'The Matrix' (TV Short Movie)
    ("tt7045440", 3),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0436992", 45),  # Doctor Who (TV Series)
    ("tt0185906", 594),  # Band of Brothers (TV Mini-Series)
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_runtime(page, imdb_id, runtime):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.runtime == runtime


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id",), [
    ("tt0390244",),  # The Matrix Online
])
def test_title_parser_should_not_set_runtime_for_video_games(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert not hasattr(parsed, "runtime")


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "rating"), [
    ("tt0133093", Decimal("8.7")),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_rating(page, imdb_id, rating):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (abs(parsed.rating) - rating < Decimal("0.3")) if rating is not None else (parsed.rating is None)


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "votes"), [
    ("tt0133093", 2_000_000),  # The Matrix
    ("tt3629794", 0),  # Aslan
])
def test_title_parser_should_set_number_of_votes(page, imdb_id, votes):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (parsed.vote_count >= votes) if votes > 0 else (parsed.vote_count == 0)


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "genres"), [
    ("tt0133093", ["Action", "Sci-Fi"]),  # The Matrix
    ("tt0389150", ["Documentary"]),  # The Matrix Defence
    ("tt2971344", ["Short"]),  # Matrix: First Dream (Short Movie)
    ("tt0365467", ["Documentary", "Short", "Sci-Fi"]),  # Making 'The Matrix' (TV Short Movie)
    ("tt0109151", ["Animation", "Action", "Drama", "Sci-Fi", "Thriller"]),  # Armitage III: Poly-Matrix (Video Movie)
    ("tt7045440", ["Short", "Music"]),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0390244", ["Action", "Adventure", "Sci-Fi"]),  # The Matrix Online (Video Game)
    ("tt0436992", ["Adventure", "Drama", "Sci-Fi"]),  # Doctor Who (TV Series)
    ("tt0185906", ["Drama", "History", "War"]),  # Band of Brothers (TV Mini-Series)
    ("tt1000252", ["Adventure", "Drama", "Sci-Fi"]),  # Blink (TV Series Episode)
    ("tt0261024", ["Documentary", "Music"]),  # Live Aid
])
def test_title_parser_should_set_genres(page, imdb_id, genres):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.genres == genres


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "plot", "lang"), [
    ("tt0133093", "When a beautiful stranger", "en-US"),  # The Matrix
    ("tt3629794", "Plot undisclosed.", "en-US"),  # Aslan
])
def test_title_parser_should_set_plot(page, imdb_id, plot, lang):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.plot[lang].startswith(plot)


@mark.parametrize(("page",), [("main",), ("reference",)])
@mark.parametrize(("imdb_id", "directors"), [
    ("tt0133093", [("nm0905154", "Lana Wachowski"), ("nm0905152", "Lilly Wachowski"),]),  # The Matrix
    ("tt1000252", [("nm0531751", "Hettie Macdonald")]),  # Blink
    ("tt3629794", []),  # Aslan
])
def test_title_parser_should_set_directors(page, imdb_id, directors):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert [(d.imdb_id, d.name) for d in parsed.directors] == directors
