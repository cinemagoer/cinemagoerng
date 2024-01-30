import pytest

from cinemagoerng import model, web


@pytest.mark.parametrize(("imdb_id",), [
    ("tt0436992",),  # Doctor Who
    ("tt0185906",),  # Band of Brothers (Mini-Series)
])
def test_title_episodes_parser_should_set_imdb_id(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.imdb_id == imdb_id


@pytest.mark.parametrize(("imdb_id", "type_"), [
    ("tt0436992", model.TVSeries),  # Doctor Who
    ("tt0185906", model.TVMiniSeries),  # Band of Brothers
])
def test_title_episodes_parser_should_instantiate_correct_type(imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert isinstance(parsed, type_)


@pytest.mark.parametrize(("imdb_id", "title"), [
    ("tt0436992", "Doctor Who"),
])
def test_title_episodes_parser_should_set_title_from_original_title(imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.title == title


@pytest.mark.parametrize(("imdb_id", "primary_image"), [
    ("tt0436992", "https://m.media-amazon.com/images/M/MV5BNjBkMWJkNTYtYjMwYy00ZjZiLWIwYmEtNzMyOTJjODRhNTlhXkEyXkFqcGdeQXVyMTUzMTg2ODkz._V1_.jpg"),  # Doctor Who
])
def test_title_episodes_parser_should_set_primary_image(imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(("imdb_id", "year"), [
    ("tt0436992", 2005),  # Doctor Who
    ("tt0412142", 2004),  # House M.D.
    ("tt0185906", 2001),  # Band of Brothers (Mini-Series)
])
def test_title_episodes_parser_should_set_year(imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.year == year


@pytest.mark.parametrize(("imdb_id", "end_year"), [
    ("tt0436992", None),  # Doctor Who
    ("tt0412142", 2012),  # House M.D.
    ("tt0185906", 2001),  # Band of Brothers (Mini-Series)
])
def test_title_parser_should_set_end_year(imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.end_year == end_year


@pytest.mark.parametrize(("imdb_id",), [
    ("tt0436992",),  # Doctor Who
    ("tt0185906",),  # Band of Brothers (Mini-Series)
])
def test_title_episodes_parser_should_instantiate_episodes(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert all(isinstance(episode, model.TVEpisode) for episode in parsed.episodes)


@pytest.mark.parametrize(("imdb_id", "season", "episode_count", "episode_data"), [
    ("tt0436992", 1, 13, [  # Doctor Who
        (0, "1", "1", "Rose"),
        (12, "1", "13", "The Parting of the Ways"),
    ]),
    ("tt0436992", 3, 14, [  # Doctor Who
        (10, "3", "10", "Blink"),
    ]),
    ("tt0185906", 1, 10, [  # Band of Brothers (Mini-Series)
        (0, "1", "1", "Currahee"),
        (9, "1", "10", "Points"),
    ]),
])
def test_title_episodes_parser_should_set_episode_info(imdb_id, season, episode_count, episode_data):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=str(season))
    assert len(parsed.episodes) == episode_count
    for item in episode_data:
        episode = parsed.episodes[item[0]]
        assert (episode.season, episode.episode, episode.title) == item[1:]


@pytest.mark.parametrize(("imdb_id", "season_data"), [
    ("tt0436992", [  # Doctor Who
        ("1", 13),
    ]),
    ("tt0185906", [  # Band of Brothers (Mini-Series)
        ("1", 10),
    ]),
])
def test_updating_episodes_should_set_all_seasons(imdb_id, season_data):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    for season in range(1, parsed.season_count + 1):
        web.update_title(parsed, page="episodes", keys=["episodes"],
                         season=str(season))
    for season, episode_count in season_data:
        assert len([episode for episode in parsed.episodes if episode.season == season]) == episode_count
