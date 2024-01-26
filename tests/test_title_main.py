from decimal import Decimal

import pytest

from cinemagoerng import model, web


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
def test_title_parser_should_set_imdb_id(page):
    parsed = web.get_title(imdb_id="tt0133093", page=page)
    assert parsed.imdb_id == "tt0133093"


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id", "type_"), [
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


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id", "title"), [
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


@pytest.mark.parametrize(("page",), [("main",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id", "primary_image"), [
    ("tt0133093", "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg"),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_primary_image(page, imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id", "year"), [
    ("tt0133093", 1999),  # The Matrix
    ("tt0436992", 2005),  # Doctor Who (2005-)
    ("tt0412142", 2004),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001)
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_year(page, imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.year == year


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id", "end_year"), [
    ("tt0436992", None),  # Doctor Who (2005-)
    ("tt0412142", 2012),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001) (TV Mini-Series)
])
def test_title_parser_should_set_end_year(page, imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.end_year == end_year


@pytest.mark.parametrize(("page",), [("main",), ("reference",), ("taglines",)])
@pytest.mark.parametrize(("imdb_id",), [
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


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "country_codes"), [
    ("tt0133093", ["US", "AU"]),  # The Matrix
    ("tt0389150", ["GB"]),  # The Matrix Defence
])
def test_title_parser_should_set_country_codes(page, imdb_id, country_codes):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.country_codes == country_codes


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "language_codes"), [
    ("tt0133093", ["en"]),  # The Matrix
    ("tt0429489", ["tr", "en", "it"]),  # A Ay
    ("tt2971344", ["zxx"]),  # Matrix: First Dream (language: None)
])
def test_title_parser_should_set_language_codes(page, imdb_id, language_codes):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.language_codes == language_codes


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "runtime"), [
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


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id",), [
    ("tt0390244",),  # The Matrix Online
])
def test_title_parser_should_not_set_runtime_for_video_games(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert not hasattr(parsed, "runtime")


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "genres"), [
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


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "rating"), [
    ("tt0133093", Decimal("8.7")),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_rating(page, imdb_id, rating):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (abs(parsed.rating - rating) < Decimal("0.3")) if rating is not None else (parsed.rating is None)


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "votes"), [
    ("tt0133093", 2_000_000),  # The Matrix
    ("tt3629794", 0),  # Aslan
])
def test_title_parser_should_set_number_of_votes(page, imdb_id, votes):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (parsed.vote_count >= votes) if votes > 0 else (parsed.vote_count == 0)


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "rank"), [
    ("tt0133093", 16),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_top_ranking(page, imdb_id, rank):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (abs(parsed.top_ranking - rank) < 10) if rank is not None else (parsed.top_ranking is None)


@pytest.mark.parametrize(("page",), [("main",), ("reference",)])
@pytest.mark.parametrize(("imdb_id", "plot", "lang"), [
    ("tt0133093", "When a beautiful stranger", "en-US"),  # The Matrix
    ("tt3629794", "Plot undisclosed.", "en-US"),  # Aslan
])
def test_title_parser_should_set_plot(page, imdb_id, plot, lang):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.plot[lang].startswith(plot)


@pytest.mark.parametrize(("imdb_id", "n", "cast"), [
    ("tt7045440", 1, [  # David Bowie: Ziggy Stardust
        ("nm0000309", "David Bowie", "David Bowie", []),
    ]),
    ("tt0101597", 2, [  # Closet Land
        ("nm0000656", "Madeleine Stowe", "Victim", []),
        ("nm0000614", "Alan Rickman", "Interrogator", []),
    ]),
    ("tt1000252", 12, [  # Blink
        ("nm0855039", "David Tennant", "The Doctor", []),
        ("nm1303956", "Freema Agyeman", "Martha Jones", []),
        ("nm1659547", "Carey Mulligan", "Sally Sparrow", []),
        ("nm1164725", "Lucy Gaskell", "Kathy Nightingale", []),
        ("nm1015511", "Finlay Robertson", "Larry Nightingale", []),
        ("nm0134458", "Richard Cant", "Malcolm Wainwright", []),
        ("nm0643394", "Michael Obiora", "Billy Shipton", []),
        ("nm0537158", "Louis Mahoney", "Old Billy", []),
        ("nm1631281", "Thomas Nelstrop", "Ben Wainwright", []),
        ("nm2286323", "Ian Boldsworth", "Banto", []),
        ("nm0768205", "Raymond Sawyer", "Desk Sergeant", ["as Ray Sawyer"]),
        ("nm4495179", "Elen Thomas", "Weeping Angel", ["uncredited"]),
    ]),
    ("tt0133093", 18, []),  # The Matrix
    ("tt3629794", 0, []),  # Aslan
])
def test_title_parser_should_set_main_cast(imdb_id, n, cast):
    parsed = web.get_title(imdb_id=imdb_id, page="main")
    assert len(parsed.cast) == n
    if len(cast) > 0:
        assert [(credit.imdb_id, credit.name, credit.role, credit.notes)
                for credit in parsed.cast] == cast


@pytest.mark.parametrize(("imdb_id", "n", "directors"), [
    ("tt1000252", 1, [  # Blink
        ("nm0531751", "Hettie Macdonald", None, []),
    ]),
    ("tt0133093", 2, [  # The Matrix
        ("nm0905154", "Lana Wachowski", None, []),
        ("nm0905152", "Lilly Wachowski", None, []),
    ]),
    ("tt0092580", 3, [  # Aria
        ("nm0000265", "Robert Altman", None, []),
        ("nm0000915", "Bruce Beresford", None, []),
        ("nm0117317", "Bill Bryden", None, []),
    ]),
    ("tt3629794", 0, []),  # Aslan
])
def test_title_main_parser_should_set_main_directors(imdb_id, n, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="main")
    assert len(parsed.directors) == n
    if len(directors) > 0:
        assert [(credit.imdb_id, credit.name, credit.role, credit.notes)
                for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "n", "writers"), [
    ("tt7045440", 1, [  # David Bowie: Ziggy Stardust
        ("nm0000309", "David Bowie", None, [])
    ]),
    ("tt0133093", 2, [  # The Matrix
        ("nm0905152", "Lilly Wachowski", None, []),
        ("nm0905154", "Lana Wachowski", None, []),
    ]),
    ("tt0076786", 3, [  # Suspiria
        ("nm0000783", "Dario Argento", None, []),
        ("nm0630453", "Daria Nicolodi", None, []),
        ("nm0211063", "Thomas De Quincey", None, []),
    ]),
    ("tt0092580", 3, []),  # Aria
    ("tt0365467", 0, []),  # Making 'The Matrix'
])
def test_title_main_parser_should_set_main_writers(imdb_id, n, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="main")
    assert len(parsed.writers) == n
    if len(writers) > 0:
        assert [(credit.imdb_id, credit.name, credit.role, credit.notes)
                for credit in parsed.writers] == writers
