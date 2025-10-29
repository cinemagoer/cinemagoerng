import pytest

from datetime import date
from decimal import Decimal

from cinemagoerng import web as imdb


@pytest.mark.parametrize(("imdb_id", "season", "n"), [
    ("tt0436992", "1", 13),  # Doctor Who
    ("tt0436992", "7", 15),  # Doctor Who
    ("tt0185906", "1", 10),  # Band of Brothers (Mini-Series)
])
def test_title_episodes_parser_should_set_episodes_for_season(imdb_id, season, n):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    assert len(parsed.episodes[season]) == n


@pytest.mark.parametrize(("imdb_id", "season", "episode", "series"), [
    ("tt0436992", "1", "1", "Doctor Who"),
    ("tt0185906", "1", "1", "Band of Brothers"),
])
def test_title_episodes_parser_should_set_season_and_series(imdb_id, season, episode, series):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    ep = parsed.episodes[season][episode]
    assert (ep.season, ep.series.imdb_id, ep.series.title) == (season, imdb_id, series)


@pytest.mark.parametrize(("imdb_id", "season", "episodes"), [
    ("tt0436992", "1", [  # Doctor Who
        ("1", "tt0562992", "Rose"),
        ("13", "tt0563000", "The Parting of the Ways"),
    ]),
    ("tt0436992", "3", [  # Doctor Who
        ("10", "tt1000252", "Blink"),
    ]),
    ("tt0185906", "1", [  # Band of Brothers (Mini-Series)
        ("1", "tt1245384", "Currahee"),
        ("10", "tt1247466", "Points"),
    ]),
])
def test_title_episodes_parser_should_set_imdb_id_and_title(imdb_id, season, episodes):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    for ep in episodes:
        episode = parsed.episodes[season][ep[0]]
        assert (episode.episode, episode.imdb_id, episode.title) == ep


@pytest.mark.parametrize(("imdb_id", "season", "episodes"), [
    ("tt0436992", "1", [  # Doctor Who
        # ("1", 2006, date(2006, 3, 17)),  # XXX: page contains incorrect data
        # ("13", 2006, date(2006, 6, 9)),  # XXX: page contains incorrect data
    ]),
    ("tt0436992", "3", [  # Doctor Who
        ("10", 2007, date(2007, 6, 9)),
    ]),
    ("tt0185906", "1", [  # Band of Brothers (Mini-Series)
        ("1", 2001, date(2001, 9, 9)),
        ("10", 2001, date(2001, 11, 4)),
    ]),
])
def test_title_episodes_parser_should_set_release_dates(imdb_id, season, episodes):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    for ep in episodes:
        episode = parsed.episodes[season][ep[0]]
        assert (episode.episode, episode.year, episode.release_date) == ep


@pytest.mark.parametrize(("imdb_id", "season", "episode", "rating"), [
    ("tt0436992", "3", "10", Decimal("9.8")),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_episode_rating(imdb_id, season, episode, rating):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    episode = parsed.episodes[season][episode]
    assert abs(episode.rating - rating) <= Decimal("0.3")


@pytest.mark.parametrize(("imdb_id", "season", "episode", "vote_count"), [
    ("tt0436992", "3", "10", 23500),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_vote_count(imdb_id, season, episode, vote_count):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    episode = parsed.episodes[season][episode]
    assert episode.vote_count >= vote_count


@pytest.mark.parametrize(("imdb_id", "season", "episode", "plot"), [
    ("tt0436992", "3", "10", "Sally Sparrow receives a cryptic message"),  # Doctor Who: Blink
])
def test_title_episodes_parser_should_set_plot(imdb_id, season, episode, plot):
    parsed = imdb.get_title(imdb_id=imdb_id)
    imdb.set_episodes(parsed, season=season)
    episode = parsed.episodes[season][episode]
    assert episode.plot["en-US"].startswith(plot)
