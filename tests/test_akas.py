import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "expected_akas"), [
    ("tt0133093", [  # The Matrix
        {
            "title": "The Matrix",
            "country": "Australia",
            "language": None,
            "is_alternative": False,
        },
    ]),
    ("tt0185103", [  # WWE Raw
        {
            "title": "WWE・ロウ",
            "country": "Japan",
            "language": "Japanese",
            "is_alternative": False,
        },
    ]),
])
def test_title_parser_should_set_akas(imdb_id, expected_akas):
    parsed = web.get_title(imdb_id=imdb_id)
    web.update_title(parsed, page="akas", keys=["akas"])

    expected_akas_countries = [aka["country"] for aka in expected_akas]
    validate_akas = [aka for aka in parsed.akas if aka.country in expected_akas_countries]

    assert len(validate_akas) == len(expected_akas)
    for i, expected_aka in enumerate(expected_akas):
        validate_aka = validate_akas[i]
        assert validate_aka.title == expected_aka["title"]
        assert validate_aka.country == expected_aka["country"]
        assert validate_aka.language == expected_aka.get("language")
        assert validate_aka.is_alternative == expected_aka.get("is_alternative")
