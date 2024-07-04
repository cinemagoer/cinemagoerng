import pytest

from cinemagoerng import web


@pytest.mark.parametrize(
    ("imdb_id", "nudity_status", "mpaa_rating"),
    [
        (
            "tt0133093",  # The Matrix
            "Mild",
            "Rated R for sci-fi violence and brief language",
        ),
        (
            "tt0468569",  # The Dark Knight
            "None",
            "Rated PG-13 for intense sequences of violence and some menace",
        ),
    ],
)
def test_title_parser_should_set_parentalguide(imdb_id, nudity_status, mpaa_rating):
    parsed = web.get_title(imdb_id=imdb_id, page="parental_guide")

    assert parsed.advisories.nudity.status == nudity_status
    assert parsed.certification.mpaa == mpaa_rating


@pytest.mark.parametrize(
    ("imdb_id", "nudity_status", "certificate_data"),
    [
        (
            "tt0436992",  # The Matrix
            "None",
            ["United States", "TV-PG"],
        ),
        (
            "tt0903747",  # Breaking Bad
            "Moderate",
            ["Argentina", "18"],
        ),
    ],
)
def test_title_update_certificate(imdb_id, nudity_status, certificate_data):
    parsed = web.get_title(imdb_id=imdb_id)
    web.update_title(parsed, page="parental_guide", keys=["certification", "advisories"])

    assert parsed.advisories.nudity.status == nudity_status
    us_certificates = [
        certificate for certificate in parsed.certification.certificates if certificate.country == certificate_data[0]
    ]
    assert us_certificates[0].certificate == certificate_data[1]
