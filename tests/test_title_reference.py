import pytest

from datetime import date

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "country_codes"), [
    ("tt0133093", ["US", "AU"]),  # The Matrix
    ("tt0389150", ["GB"]),  # The Matrix Defence
])
def test_title_reference_parser_should_set_country_codes(imdb_id, country_codes):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.country_codes == country_codes


@pytest.mark.parametrize(("imdb_id", "language_codes"), [
    ("tt0133093", ["en"]),  # The Matrix
    ("tt0429489", ["tr", "en", "it"]),  # A Ay
    ("tt2971344", ["zxx"]),  # Matrix: First Dream (language: None)
])
def test_title_reference_parser_should_set_language_codes(imdb_id, language_codes):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.language_codes == language_codes


# TODO: find a movie with no genres
@pytest.mark.parametrize(("imdb_id", "genres"), [
    ("tt0133093", ["Action", "Sci-Fi"]),  # The Matrix (Movie)
    ("tt0389150", ["Documentary"]),  # The Matrix Defence (TV Movie)
    ("tt2971344", ["Short"]),  # Matrix: First Dream (Short Movie)
    ("tt0365467", ["Documentary", "Short", "Sci-Fi"]),  # Making 'The Matrix' (TV Short Movie)
    ("tt0109151", ["Animation", "Action", "Drama", "Sci-Fi", "Thriller"]),  # Armitage III: Poly-Matrix (Video Movie)
    ("tt7045440", ["Music"]),  # David Bowie: Ziggy Stardust (Music Video)
    ("tt0390244", ["Action", "Adventure", "Sci-Fi"]),  # The Matrix Online (Video Game)
    ("tt0436992", ["Adventure", "Drama", "Sci-Fi"]),  # Doctor Who (TV Series)
    ("tt0185906", ["Action", "Drama", "History", "War"]),  # Band of Brothers (TV Mini-Series)
    ("tt1000252", ["Adventure", "Drama", "Sci-Fi"]),  # Blink (TV Series Episode)
    ("tt0261024", ["Documentary", "Music"]),  # Live Aid (TV Special)
])
def test_title_reference_parser_should_set_all_genres(imdb_id, genres):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.genres == genres


@pytest.mark.parametrize(("imdb_id", "taglines"), [
    ("tt0133093", ["Free your mind"]),  # The Matrix
    ("tt3629794", []),  # Aslan
])
def test_title_reference_parser_should_set_first_tagline(imdb_id, taglines):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.taglines == taglines


@pytest.mark.parametrize(("imdb_id", "plot", "lang"), [
    ("tt0133093", "Thomas A. Anderson is a man living two lives.", "en-US"),  # The Matrix
    ("tt3629794", None, None),  # Aslan
])
def test_title_reference_parser_should_set_first_plot_summary(imdb_id, plot, lang):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    if plot is None:
        assert parsed.plot_summaries == {}
    else:
        assert parsed.plot_summaries[lang][0].startswith(plot)


@pytest.mark.parametrize(("imdb_id", "rank"), [
    ("tt0133093", 16),  # The Matrix
    ("tt3629794", None),  # Aslan
])
def test_title_reference_parser_should_set_top_ranking(imdb_id, rank):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert (abs(parsed.top_ranking - rank) < 10) if rank is not None else (parsed.top_ranking is None)


@pytest.mark.parametrize(("imdb_id", "n", "cast"), [
    ("tt7045440", 1, [  # David Bowie: Ziggy Stardust
        ("nm0000309", "David Bowie", ["Self"], []),
    ]),
    ("tt0101597", 2, [  # Closet Land
        ("nm0000614", "Alan Rickman", ["Interrogator"], []),
        ("nm0000656", "Madeleine Stowe", ["Victim"], [])
    ]),
    ("tt0069281", 6, [  # Sleuth
        ("nm0000059", "Laurence Olivier", ["Andrew Wyke"], []),
        ("nm0000323", "Michael Caine", ["Milo Tindle", "Inspector Doppler"], []),
        ("nm0147250", "Alec Cawthorne", ["Inspector Doppler"], ["credit only"]),
        ("nm0560064", "John Matthews", ["Detective Sergeant Tarrant"], ["credit only"]),
        ("nm0151920", "Eve Channing", ["Marguerite Wyke"], ["credit only"]),
        ("nm0553117", "Teddy Martin", ["Police Constable Higgs"], ["credit only"]),
    ]),
    ("tt1000252", 12, [  # Blink
        ("nm0855039", "David Tennant", ["The Doctor"], []),
        ("nm1303956", "Freema Agyeman", ["Martha Jones"], []),
        ("nm1659547", "Carey Mulligan", ["Sally Sparrow"], []),
        ("nm1164725", "Lucy Gaskell", ["Kathy Nightingale"], []),
        ("nm1015511", "Finlay Robertson", ["Larry Nightingale"], []),
        ("nm0134458", "Richard Cant", ["Malcolm Wainwright"], []),
        ("nm0643394", "Michael Obiora", ["Billy Shipton"], []),
        ("nm0537158", "Louis Mahoney", ["Old Billy"], []),
        ("nm1631281", "Thomas Nelstrop", ["Ben Wainwright"], []),
        ("nm2286323", "Ian Boldsworth", ["Banto"], []),
        ("nm0768205", "Raymond Sawyer", ["Desk Sergeant"], ["as Ray Sawyer"]),
        ("nm4495179", "Elen Thomas", ["Weeping Angel"], ["uncredited"]),
    ]),
    ("tt0133093", 41, []),  # The Matrix
    ("tt3629794", 0, []),  # Aslan
])
def test_title_reference_parser_should_set_all_cast(imdb_id, n, cast):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.cast) == n
    if len(cast) > 0:
        assert [(credit.imdb_id, credit.name, credit.characters, credit.notes) for credit in parsed.cast] == cast


@pytest.mark.parametrize(("imdb_id", "n", "directors"), [
    ("tt1000252", 1, [  # Blink
        ("nm0531751", "Hettie Macdonald", None, [])
    ]),
    ("tt0133093", 2, [  # The Matrix
        ("nm0905154", "Lana Wachowski", None, ["as The Wachowski Brothers"]),
        ("nm0905152", "Lilly Wachowski", None, ["as The Wachowski Brothers"]),
    ]),
    ("tt0092580", 10, [  # Aria
        ("nm0000265", "Robert Altman", None, ['segment "Les Boréades"']),
        ("nm0000915", "Bruce Beresford", None, ['segment "Die tote Stadt"']),
        ("nm0117317", "Bill Bryden", None, ['segment "I pagliacci"']),
        ("nm0000419", "Jean-Luc Godard", None, ['segment "Armide"']),
        ("nm0418746", "Derek Jarman", None, ['segment "Depuis le jour"']),
        ("nm0734466", "Franc Roddam", None, ['segment "Liebestod"']),
        ("nm0001676", "Nicolas Roeg", None, ['segment "Un ballo in maschera"']),
        ("nm0001692", "Ken Russell", None, ['segment "Nessun dorma"']),
        ("nm0836430", "Charles Sturridge", None, ['segment "La virgine degli angeli"']),
        ("nm0854697", "Julien Temple", None, ['segment "Rigoletto"']),
    ]),
    ("tt3629794", 0, []),  # Aslan
])
def test_title_reference_parser_should_set_all_directors(imdb_id, n, directors):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.directors) == n
    if len(directors) > 0:
        assert [(credit.imdb_id, credit.name, credit.job, credit.notes) for credit in parsed.directors] == directors


@pytest.mark.parametrize(("imdb_id", "n", "writers"), [
    ("tt7045440", 1, [  # David Bowie: Ziggy Stardust
        ("nm0000309", "David Bowie", None, [])
    ]),
    ("tt0133093", 2, [  # The Matrix
        ("nm0905152", "Lilly Wachowski", "written by", ["as The Wachowski Brothers"]),
        ("nm0905154", "Lana Wachowski", "written by", ["as The Wachowski Brothers"]),
    ]),
    ("tt0076786", 3, [  # Suspiria
        ("nm0000783", "Dario Argento", "screenplay and", []),
        ("nm0630453", "Daria Nicolodi", "screenplay", []),
        ("nm0211063", "Thomas De Quincey", 'book "Suspiria de Profundis"', ["uncredited"]),
    ]),
    ("tt0092580", 10, []),  # Aria
    ("tt0365467", 0, []),  # Making 'The Matrix'
])
def test_title_reference_parser_should_set_all_writers(imdb_id, n, writers):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.writers) == n
    if len(writers) > 0:
        assert [(credit.imdb_id, credit.name, credit.job, credit.notes) for credit in parsed.writers] == writers


@pytest.mark.parametrize(("imdb_id", "release_date"), [
    ("tt1000252", date(2007, 6, 9)),  # Doctor Who: Blink
])
def test_title_reference_parser_should_set_release_date_for_episode(imdb_id, release_date):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert parsed.release_date == release_date


@pytest.mark.skip(reason="series reference page parser not done yet")
@pytest.mark.parametrize(("imdb_id", "n", "creators"), [
    ("tt0436992", 1, [  # Doctor Who
        ("nm0628285", "Sydney Newman", None, [])
    ]),
    ("tt0445114", 2, [  # Extras
        ("nm0315041", "Ricky Gervais", None, []),
        ("nm0580351", "Stephen Merchant", None, []),
    ]),
    ("tt0185906", 0, []),  # Band of Brothers (Mini-Series)
])
def test_title_reference_parser_should_set_all_creators_for_series(imdb_id, n, creators):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    assert len(parsed.creators) == n
    if len(creators) > 0:
        assert [(credit.imdb_id, credit.name, credit.job, credit.notes) for credit in parsed.creators] == creators


@pytest.mark.parametrize(("imdb_id", "n", "crew"), [
    ("tt1000252", 4, [  # Blink
        ("nm2289913", "Charlotte Mitchell", "costume supervisor", []),
        ("nm2939651", "Sara Morgan", "costume assistant", []),
        ("nm1574636", "Bobbie Peach", "costume assistant", ["as Bobby Peach"]),
        ("nm1834907", "Stephen Kill", "costume prop maker", ["uncredited"]),
    ]),
])
def test_title_reference_parser_should_set_all_crew_members(imdb_id, n, crew):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    parsed_crew = parsed.costume_department
    assert len(parsed_crew) == n
    if len(crew) > 0:
        assert [(credit.imdb_id, credit.name, credit.job, credit.notes) for credit in parsed_crew] == crew
