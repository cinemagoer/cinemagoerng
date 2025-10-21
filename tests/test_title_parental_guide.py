import pytest

from cinemagoerng import web


@pytest.mark.parametrize(("imdb_id", "nudity_status"), [
    ("tt0133093", "Mild"),  # The Matrix
    ("tt0468569", "None"),  # The Dark Knight
    ("tt0903747", "Moderate"),  # Breaking Bad
])
def test_parental_guide_parser_should_set_advisories(imdb_id, nudity_status):
    parsed = web.get_title(imdb_id=imdb_id, page="parental_guide")
    assert parsed.advisories.nudity.status == nudity_status


@pytest.mark.parametrize(("imdb_id", "rating", "reason"), [
    ("tt0133093", "13+", "Rated R for sci-fi violence and brief language"),  # The Matrix
    ("tt0468569", "13+", "Rated PG-13 for intense sequences of violence and some menace"),  # The Dark Knight
])
def test_parental_guide_parser_should_set_mpa_rating_with_reason(imdb_id, rating, reason):
    parsed = web.get_title(imdb_id=imdb_id, page="parental_guide")
    assert (parsed.certification.mpa_rating, parsed.certification.mpa_rating_reason) == (rating, reason)


@pytest.mark.parametrize(("imdb_id", "country", "ratings"), [
    ("tt0436992", "United States", ["TV-PG", "Not Rated", "TV-14", "TV-Y7-FV"]),  # The Matrix
    ("tt0903747", "Argentina", ["18"]),  # Breaking Bad
])
def test_parental_guide_parser_title_should_set_country_ratings_on_update(imdb_id, country, ratings):
    parsed = web.get_title(imdb_id=imdb_id, page="reference")
    web.set_parental_guide(parsed)
    country_ratings = [cert.ratings for cert in parsed.certification.certificates if cert.country == country][0]
    assert country_ratings == ratings
