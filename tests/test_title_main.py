import pytest

from cinemagoerng import model, web


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id",),
    [
        ("tt0133093",),  # The Matrix
    ],
)
def test_title_parser_should_set_imdb_id(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.imdb_id == imdb_id


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id", "type_"),
    [
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
    ],
)
def test_title_parser_should_instantiate_correct_type(page, imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert isinstance(parsed, type_)


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id", "title"),
    [
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
    ],
)
def test_title_parser_should_set_title_from_original_title(page, imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.title == title


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id", "primary_image"),
    [
        (
            "tt0133093",
            "https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_.jpg",
        ),  # The Matrix
        ("tt3629794", None),  # Aslan
    ],
)
def test_title_parser_should_set_primary_image(page, imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id", "year"),
    [
        ("tt0133093", 1999),  # The Matrix
        ("tt7587890", 2018),  # The Rookie (2018-)
        ("tt0412142", 2004),  # House M.D. (2004-2012)
        ("tt0185906", 2001),  # Band of Brothers (2001-2001)
        ("tt3629794", None),  # Aslan
    ],
)
def test_title_parser_should_set_year(page, imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.year == year


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id", "end_year"),
    [
        ("tt7587890", None),  # The Rookie (2018-)
        ("tt0412142", 2012),  # House M.D. (2004-2012)
        ("tt0185906", 2001),  # Band of Brothers (2001-2001) (TV Mini-Series)
    ],
)
def test_title_parser_should_set_end_year(page, imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert parsed.end_year == end_year


@pytest.mark.parametrize(("page",), [("reference",), ("taglines",), ("parental_guide",)])
@pytest.mark.parametrize(
    ("imdb_id",),
    [
        ("tt0133093",),  # The Matrix (Movie)
        ("tt0389150",),  # The Matrix Defence (TV Movie)
        ("tt2971344",),  # Matrix: First Dream (Short Movie)
        ("tt0365467",),  # Making 'The Matrix' (TV Short Movie)
        ("tt0109151",),  # Armitage III: Poly-Matrix (Video Movie)
        ("tt7045440",),  # David Bowie: Ziggy Stardust (Music Video)
        ("tt0390244",),  # The Matrix Online (Video Game)
        ("tt1000252",),  # Blink (TV Series Episode)
        ("tt0261024",),  # Live Aid
    ],
)
def test_title_parser_should_not_set_end_year_for_other_than_series(page, imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page=page)
    assert not hasattr(parsed, "end_year")
