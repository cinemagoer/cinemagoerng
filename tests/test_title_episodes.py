from datetime import date
from decimal import Decimal

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
    assert all(isinstance(episode, model.TVEpisode) for episode in parsed.episodes["1"].values())


@pytest.mark.parametrize(("imdb_id", "season", "episode_count", "episode_data"), [
    ("tt0436992", "1", 13, [  # Doctor Who
        ("1", "1", "Rose", 2006, date(2006, 3, 17)),
        ("1", "13", "The Parting of the Ways", 2006, date(2006, 6, 9)),
    ]),
    ("tt0436992", "3", 14, [  # Doctor Who
        ("3", "10", "Blink", 2007, date(2007, 6, 9)),
    ]),
    ("tt0185906", "1", 10, [  # Band of Brothers (Mini-Series)
        ("1", "1", "Currahee", 2005, date(2005, 3, 25)),
        ("1", "10", "Points", 2005, date(2005, 5, 20)),
    ]),
])
def test_title_episodes_parser_should_set_basic_episode_info(imdb_id, season, episode_count, episode_data):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    assert len(parsed.episodes[season]) == episode_count
    for item in episode_data:
        episode = parsed.episodes[season][item[1]]
        assert (episode.season, episode.episode, episode.title, episode.year, episode.release_date) == item


@pytest.mark.parametrize(("imdb_id", "season", "episode", "rating"), [
    ("tt0436992", "3", "10", Decimal("9.8")),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_episode_rating(imdb_id, season, episode, rating):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert abs(episode.rating - rating) <= Decimal("0.3")


@pytest.mark.parametrize(("imdb_id", "season", "episode", "vote_count"), [
    ("tt0436992", "3", "10", 23500),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_vote_count(imdb_id, season, episode, vote_count):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert episode.vote_count >= vote_count


@pytest.mark.parametrize(("imdb_id", "season", "episode", "plot"), [
    ("tt0436992", "3", "10", "Sally Sparrow receives a cryptic message"),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_plot(imdb_id, season, episode, plot):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert episode.plot["en-US"].startswith(plot)


@pytest.mark.parametrize(("imdb_id", "episode_counts"), [
    ("tt0436992", [  # Doctor Who
        ("1", 13),
        ("3", 14),
        ("12", 10),
    ]),
])
def test_updating_episodes_should_accumulate_seasons(imdb_id, episode_counts):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    for i, (season, episode_count) in enumerate(episode_counts):
        assert len(parsed.episodes) == i
        assert season not in parsed.episodes
        web.update_title(parsed, page="episodes", keys=["episodes"], season=str(season))
        assert len(parsed.episodes) == i + 1
        assert len(parsed.episodes[season]) == episode_count
