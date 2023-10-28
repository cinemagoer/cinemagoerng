from cinemagoerng import web


def test_title_reference_should_parse_title():
    title = web.get_title_reference(imdb_id=133093)
    assert title.title == "The Matrix"
