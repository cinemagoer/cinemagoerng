import pytest

from cinemagoerng import web


@pytest.mark.parametrize(
    ("imdb_id", "n", "akas"),
    [
        (
            "tt0429489",
            3,
            [  # A Ay
                ("Луна", "SUHH", "Soviet Union", "ru", "Russian", False, []),
                (
                    "Oh, Moon!",
                    "US",
                    "United States",
                    None,
                    None,
                    True,
                    ["literal English title"],
                ),
                (
                    "Oh, Moon!",
                    "XWW",
                    "World-wide",
                    "en",
                    "English",
                    True,
                    ["complete title"],
                ),
            ],
        ),
        ("tt3629794", 0, []),  # Aslan
        ("tt0133093", 50, []),  # The Matrix
    ],
)
def test_title_akas_parser_should_set_akas(imdb_id, n, akas):
    parsed = web.get_title(imdb_id=imdb_id)
    web.update_title(parsed, page="akas", keys=["akas"])
    assert len(parsed.akas) == n
    if len(akas) > 0:
        assert [
            (
                aka.title,
                aka.country_code,
                aka.country,
                aka.language_code,
                aka.language,
                aka.is_alternative,
                aka.notes,
            )
            for aka in parsed.akas
        ] == akas


@pytest.mark.parametrize(
    ("imdb_id", "akas_count"),
    [
        ("tt0133093", 68),  # The Matrix
    ],
)
def test_title_akas_parser_pagination(imdb_id, akas_count):
    parsed = web.get_title(imdb_id=imdb_id)
    web.update_title(parsed, page="akas", keys=["akas"], paginate_result=True)
    assert len(parsed.akas) == akas_count
