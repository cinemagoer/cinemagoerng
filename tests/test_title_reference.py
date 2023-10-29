from pytest import mark

from cinemagoerng import web


def test_title_reference_parser_should_set_imdb_id():
    parsed = web.get_title_reference(imdb_id=133093)
    assert parsed.imdb_id == 133093


@mark.parametrize(("imdb_id", "title"),
                  [(133093, "Matrix"),
                   (389150, "The Matrix Defence"),  # TV Movie
                   (109151, "Armitage III: Poly-Matrix"),  # Video
                   (390244, "The Matrix Online"),  # Video Game
                   (436992, "Doctor Who"),  # TV Series
                   (185906, "Kardeşler Takımı"),  # TV Mini Series
                   (1000252, "Blink")])  # TV Episode
def test_title_reference_parser_should_set_local_title(imdb_id, title):
    parsed = web.get_title_reference(imdb_id=imdb_id)
    assert parsed.title == title
