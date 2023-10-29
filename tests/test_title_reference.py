from cinemagoerng import web


def test_title_reference_should_set_imdb_id():
    title = web.get_title_reference(imdb_id=133093)
    assert title.imdb_id == 133093


def test_title_reference_should_set_title():
    title = web.get_title_reference(imdb_id=133093)
    assert title.title == "The Matrix"
