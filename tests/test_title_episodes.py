import pytest

from datetime import date
from decimal import Decimal

from cinemagoerng import model, web


@pytest.mark.parametrize(
    ("imdb_id",),
    [
        ("tt0436992",),  # Doctor Who
        ("tt0185906",),  # Band of Brothers (Mini-Series)
    ],
)
def test_title_episodes_parser_should_set_imdb_id(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.imdb_id == imdb_id


@pytest.mark.parametrize(
    ("imdb_id", "type_"),
    [
        ("tt0436992", model.TVSeries),  # Doctor Who
        ("tt0185906", model.TVMiniSeries),  # Band of Brothers
    ],
)
def test_title_episodes_parser_should_instantiate_correct_type(imdb_id, type_):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert isinstance(parsed, type_)


@pytest.mark.parametrize(
    ("imdb_id", "title"),
    [
        ("tt0436992", "Doctor Who"),
    ],
)
def test_title_episodes_parser_should_set_title_from_original_title(imdb_id, title):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.title == title


@pytest.mark.parametrize(
    ("imdb_id", "primary_image"),
    [
        (
            "tt0412142",
            "https://m.media-amazon.com/images/M/MV5BMjgxYjAwNmMtYTAwZC00YmQxLWJlOTMtMWM0NGJmNDE0YmI2XkEyXkFqcGc@._V1_.jpg",
        ),  # House M.D.
    ],
)
def test_title_episodes_parser_should_set_primary_image(imdb_id, primary_image):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.primary_image == primary_image


@pytest.mark.parametrize(
    ("imdb_id", "year"),
    [
        ("tt7587890", 2018),  # The Rookie
        ("tt0412142", 2004),  # House M.D.
        ("tt0185906", 2001),  # Band of Brothers (Mini-Series)
    ],
)
def test_title_episodes_parser_should_set_year(imdb_id, year):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.year == year


@pytest.mark.parametrize(
    ("imdb_id", "end_year"),
    [
        ("tt7587890", None),  # The Rookie
        ("tt0412142", 2012),  # House M.D.
        ("tt0185906", 2001),  # Band of Brothers (Mini-Series)
    ],
)
def test_title_parser_should_set_end_year(imdb_id, end_year):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.end_year == end_year


@pytest.mark.parametrize(
    ("imdb_id",),
    [
        ("tt0436992",),  # Doctor Who
        ("tt0185906",),  # Band of Brothers (Mini-Series)
    ],
)
def test_title_episodes_parser_should_instantiate_episodes(imdb_id):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert all(isinstance(episode, model.TVEpisode) for episode in parsed.episodes["1"].values())


@pytest.mark.parametrize(
    ("imdb_id", "season", "episode_count", "episode_data"),
    [
        (
            "tt0436992",
            "1",
            13,
            [  # Doctor Who
                # ("1", "tt0562992", "Rose", 2006, date(2006, 3, 17)),  # XXX: page contains incorrect data
                # ("13", "tt0563000", "The Parting of the Ways", 2006, date(2006, 6, 9)),  # XXX: page contains incorrect data  # noqa: E501
            ],
        ),
        (
            "tt0436992",
            "3",
            14,
            [  # Doctor Who
                ("10", "tt1000252", "Blink", 2007, date(2007, 6, 9)),
            ],
        ),
        (
            "tt0185906",
            "1",
            10,
            [  # Band of Brothers (Mini-Series)
                ("1", "tt1245384", "Currahee", 2001, date(2001, 9, 9)),
                ("10", "tt1247466", "Points", 2001, date(2001, 11, 4)),
            ],
        ),
    ],
)
def test_title_episodes_parser_should_set_basic_episode_info(imdb_id, season, episode_count, episode_data):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    assert len(parsed.episodes[season]) == episode_count
    for item in episode_data:
        ep = parsed.episodes[season][item[0]]
        assert (ep.season, ep.episode, ep.imdb_id, ep.title, ep.year, ep.release_date) == (season,) + item


@pytest.mark.parametrize(
    ("imdb_id", "season", "episode", "rating"),
    [
        ("tt0436992", "3", "10", Decimal("9.8")),  # Doctor Who: Blink
    ],
)
def test_title_episodes_parser_should_set_episode_rating(imdb_id, season, episode, rating):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert abs(episode.rating - rating) <= Decimal("0.3")


@pytest.mark.parametrize(
    ("imdb_id", "season", "episode", "vote_count"),
    [
        ("tt0436992", "3", "10", 23500),  # Doctor Who: Blink
    ],
)
def test_title_episodes_parser_should_set_vote_count(imdb_id, season, episode, vote_count):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert episode.vote_count >= vote_count


@pytest.mark.parametrize(
    ("imdb_id", "season", "episode", "plot"),
    [
        ("tt0436992", "3", "10", "Sally Sparrow receives a cryptic message"),  # Doctor Who: Blink
    ],
)
def test_title_episodes_parser_should_set_plot(imdb_id, season, episode, plot):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season=season)
    episode = parsed.episodes[season][episode]
    assert episode.plot["en-US"].startswith(plot)


@pytest.mark.parametrize(
    ("imdb_id", "episode_count"),
    [
        ("tt0412142", 176),  # House M.D.
        ("tt0185906", 10),  # Band of Brothers (Mini-Series)
    ],
)
def test_title_episodes_parser_should_set_episode_count(imdb_id, episode_count):
    parsed = web.get_title(imdb_id=imdb_id, page="episodes", season="1")
    assert parsed.episode_count == episode_count


@pytest.mark.parametrize(
    ("imdb_id", "episode_counts"),
    [
        (
            "tt0436992",
            [  # Doctor Who
                ("1", 13),
                ("3", 14),
                ("12", 10),
            ],
        ),
        (
            "tt0185906",
            [  # Band of Brothers (Mini-Series)
                ("1", 10),
            ],
        ),
        (
            "tt0185103",
            [  # WWE
                ("27", 50)
            ],
        ),
    ],
)
def test_updating_episodes_should_accumulate_seasons(imdb_id, episode_counts):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    for i, (season, episode_count) in enumerate(episode_counts):
        assert len(parsed.episodes) == i
        assert season not in parsed.episodes
        web.update_title(parsed, page="episodes", keys=["episodes"], season=str(season))
        assert len(parsed.episodes) == i + 1
        assert len(parsed.episodes[season]) == episode_count


@pytest.mark.parametrize(
    ("imdb_id", "episode_counts"),
    [
        (
            "tt0185103",
            [  # WWE
                ("16", 52),
                ("27", 52),
            ],
        ),
    ],
)
def test_updating_episodes_should_accumulate_seasons_with_pagination(imdb_id, episode_counts):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    for i, (season, episode_count) in enumerate(episode_counts):
        assert len(parsed.episodes) == i
        assert season not in parsed.episodes
        web.update_title(
            parsed,
            page="episodes_with_pagination",
            keys=["episodes"],
            season=str(season),
            paginate=True,
        )
        assert len(parsed.episodes) == i + 1
        assert len(parsed.episodes[season]) == episode_count


@pytest.mark.parametrize(
    ("imdb_id", "episode_count_data"),
    [
        (
            "tt0185103",
            [  # WWE
                (2016, 2017, 52, 52, 104),
                (2022, 2022, 52, 52, 156),
            ],
        ),
        (
            "tt0903747",
            [  # Breaking Bad
                (2008, 2013, 7, 8, 62),
            ],
        ),
        (
            "tt2659152",
            [  # WWE
                (2024, 2024, 0, 0, 0),
                (2023, 2023, 1, 1, 1),
            ],
        ),
    ],
)
def test_updating_episodes_should_accumulate_year_with_pagination(imdb_id, episode_count_data):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    for count_data in episode_count_data:
        start_year, end_year, start_year_episode_count, end_year_episode_count, total_episode_count = count_data
        assert parsed.get_episodes_by_year(start_year) == []
        assert parsed.get_episodes_by_year(end_year) == []
        web.update_title(
            parsed,
            page="episodes_with_pagination",
            keys=["episodes"],
            filter_type="year",
            start_year=start_year,
            end_year=end_year,
            paginate=True,
        )
        assert len(parsed.get_episodes_by_year(start_year)) == start_year_episode_count
        assert len(parsed.get_episodes_by_year(end_year)) == end_year_episode_count
        assert len([ep for season in parsed.episodes.values() for ep in season.values()]) == total_episode_count
