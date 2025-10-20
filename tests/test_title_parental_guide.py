import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "nudity_status", "mpa_rating", "mpa_rating_reason"), [
    ("tt0133093", "Mild", "13+", "Rated R for sci-fi violence and brief language"),  # The Matrix
    ("tt0468569", "None", "13+", "Rated PG-13 for intense sequences of violence and some menace"),  # The Dark Knight
])
def test_parental_guide_parser_should_set_certifications(imdb_id, nudity_status, mpa_rating, mpa_rating_reason):
    parsed = web.get_title(imdb_id=imdb_id, page="parental_guide")
    assert parsed.advisories.nudity.status == nudity_status
    assert parsed.certification.mpa_rating == mpa_rating
    assert parsed.certification.mpa_rating_reason == mpa_rating_reason


@pytest.mark.parametrize(("imdb_id", "nudity_status", "country", "rating"), [
    ("tt0436992", "None", "United States", "TV-14"),  # The Matrix
    ("tt0903747", "Moderate", "Argentina", "18"),  # Breaking Bad
])
def test_parental_guide_parser_title_should_update_certifications(imdb_id, nudity_status, country, rating):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    web.set_parental_guide(parsed)
    assert parsed.advisories.nudity.status == nudity_status
    country_certificates = [certificate for certificate in parsed.certification.certificates
                            if certificate.country == country]
    assert country_certificates
    assert rating in country_certificates[0].ratings
