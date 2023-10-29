from pytest import mark

from cinemagoerng import web


def test_title_reference_parser_should_set_imdb_id():
    parsed = web.get_title_reference(imdb_id=133093)
    assert parsed.imdb_id == 133093


@mark.parametrize(("imdb_id", "title"),
                  [(133093, "The Matrix"),
                   (389150, "The Matrix Defence"),
                   (109151, "Armitage III: Poly-Matrix"),
                   (390244, "The Matrix Online"),
                   (436992, "Doctor Who"),
                   (185906, "Band of Brothers"),
                   (1000252, "Blink")])
def test_title_reference_parser_should_set_title(imdb_id, title):
    parsed = web.get_title_reference(imdb_id=imdb_id)
    assert parsed.title == title
