import pytest

from decimal import Decimal

from cinemagoerng import model, web


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
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


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id",), [
    ("tt0133093",),  # The Matrix
])
def test_title_parser_should_set_imdb_id(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.imdb_id == imdb_id


@pytest.mark.parametrize(("page",), [("reference", ), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "title"), [
    ("tt0133093", "The Matrix"),
])
def test_title_parser_should_set_title_from_original_title(page, imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.title == title


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "primary_image"), [
    ("tt0133093",  # The Matrix
     "https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_.jpg"),
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_primary_image(page, imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "year"), [
    ("tt0133093", 1999),  # The Matrix
    ("tt7587890", 2018),  # The Rookie (2018-)
    ("tt0412142", 2004),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001)
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_year(page, imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.year == year


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "end_year"), [
    ("tt7587890", None),  # The Rookie (2018-)
    ("tt0412142", 2012),  # House M.D. (2004-2012)
    ("tt0185906", 2001),  # Band of Brothers (2001-2001) (TV Mini-Series)
])
def test_title_parser_should_set_series_end_year(page, imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.end_year == end_year


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "runtime"), [
    ("tt0133093", 136),  # The Matrix (Movie)
    ("tt2971344", 28),  # Matrix: First Dream (Short Movie)
    ("tt7045440", 3),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0436992", 45),  # Doctor Who (TV Series)
    ("tt0185906", 60),  # Band of Brothers (TV Mini-Series)
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_runtime(page, imdb_id, runtime):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.runtime == runtime


# TODO: find a movie with no genres
@pytest.mark.parametrize(("page",), [("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "genres"), [
    ("tt0133093", ["Action", "Sci-Fi"]),  # The Matrix
    ("tt0389150", ["Documentary"]),  # The Matrix Defence
    ("tt2971344", ["Short"]),  # Matrix: First Dream (Short Movie)
    ("tt0365467", ["Documentary", "Short", "Sci-Fi"]),  # Making 'The Matrix' (TV Short Movie)
    ("tt0109151", ["Animation", "Action", "Drama"]),  # Armitage III: Poly-Matrix (Video Movie)
    ("tt7045440", ["Music"]),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0390244", ["Action", "Adventure", "Sci-Fi"]),  # The Matrix Online (Video Game)
    ("tt0436992", ["Adventure", "Drama", "Sci-Fi"]),  # Doctor Who (TV Series)
    ("tt0185906", ["Action", "Drama", "History"]),  # Band of Brothers (TV Mini-Series)
    ("tt1000252", ["Adventure", "Drama", "Sci-Fi"]),  # Blink (TV Series Episode)
    ("tt0261024", ["Documentary", "Music"]),  # Live Aid (TV Special)
])
def test_title_parser_should_set_first_three_genres(page, imdb_id, genres):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.genres == genres


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "plot", "lang"), [
    ("tt0133093", "When a beautiful stranger", "en-US"),  # The Matrix
    ("tt0436992", "Continuing on from Doctor Who (1963)", "en-US"),  # Doctor Who
    ("tt0390244", "Set after 'The Matrix Revolutions'", "en-US"),  # The Matrix Online (Video Game)
    ("tt3629794", "Plot undisclosed.", "en-US"),  # Aslan
])
def test_title_parser_should_set_plot(page, imdb_id, plot, lang):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.plot[lang].startswith(plot)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "rating"), [
    ("tt0133093", Decimal("8.7")),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_parser_should_set_rating(page, imdb_id, rating):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (abs(parsed.rating - rating) < Decimal("0.3")) if rating is not None else (parsed.rating is None)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "votes"), [
    ("tt0133093", 2_000_000),  # The Matrix
    ("tt3629794", 0),  # Aslan
])
def test_title_parser_should_set_vote_count(page, imdb_id, votes):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (parsed.vote_count >= votes) if votes > 0 else (parsed.vote_count == 0)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "series_type", "series_imdb_id", "series_title"), [
    ("tt1000252", model.TVSeries, "tt0436992", "Doctor Who"),  # Doctor Who: Blink
    ("tt9256656", model.TVSeries, "tt7587890", "The Rookie"),  # The Rookie: Greenlight
    ("tt1247466", model.TVMiniSeries, "tt0185906", "Band of Brothers"),  # Band of Brothers: Points
])
def test_title_parser_should_set_series_for_episode(page, imdb_id, series_type, series_imdb_id, series_title):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    series = parsed.series
    if page in {"taglines", "parental_guide"}:
        # XXX: this will hopefully get fixed
        assert isinstance(series, model.TVSeries)
    else:
        assert isinstance(series, series_type)
    assert (series.imdb_id, series.title) == (series_imdb_id, series_title)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "series_year", "series_end_year"), [
    ("tt1000252", 2005, 2022),  # Doctor Who: Blink
    ("tt9256656", 2018, None),  # The Rookie: Greenlight
    ("tt1247466", 2001, 2001),  # Band of Brothers: Points
])
def test_title_parser_should_set_series_years_for_episode(page, imdb_id, series_year, series_end_year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (parsed.series.year, parsed.series.end_year) == (series_year, series_end_year)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(("imdb_id", "season", "episode"), [
    ("tt1000252", "3", "10"),  # Doctor Who: Blink
])
def test_title_parser_should_set_season_and_episode_numbers_for_episode(page, imdb_id, season, episode):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert (parsed.season, parsed.episode) == (season, episode)


@pytest.mark.parametrize(("imdb_id", "prev_id", "next_id"), [
    ("tt1000252", "tt1000256", "tt1000259"),  # Doctor Who: Blink
    ("tt0562992", None, "tt0562997"),  # Doctor Who: Rose
    ("tt2121965", "tt2121964", None),  # House M.D.: Everybody Dies
])
def test_title_parser_should_set_previous_and_next_episodes_for_episode(imdb_id, prev_id, next_id):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert (parsed.previous_episode_id, parsed.next_episode_id) == (prev_id, next_id)
