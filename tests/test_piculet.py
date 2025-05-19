import pytest

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from cinemagoerng import piculet


@pytest.fixture(scope="module")
def movie_spec():
    """Empty scraping spec for Piculet tests."""
    return {"version": "1", "url": "", "doctype": "html", "path_type": "xpath", "rules": []}


@pytest.fixture(scope="module")
def movie():
    """Example movie document for Piculet tests."""
    return Path(__file__).with_name("shining.html").read_text(encoding="utf-8")


@dataclass
class Movie:
    score: Decimal


def test_deserialize_should_support_decimal():
    movie = piculet.deserialize({"score": "9.8"}, Movie)
    assert isinstance(movie.score, Decimal) and (movie.score.as_integer_ratio() == (49, 5))


def test_serialize_should_support_decimal():
    movie = Movie(score=Decimal("9.8"))
    assert isinstance(movie.score, Decimal) and (piculet.serialize(movie) == {"score": "9.8"})


def test_load_spec_should_load_transform_from_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "/", "transforms": ["lower"]}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    assert isinstance(spec.rules[0].extractor.transforms[0], piculet.Transform)


def test_dump_spec_should_dump_transform_as_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "/", "transforms": ["lower"]}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["transforms"][0] == "lower"


def test_load_spec_should_raise_error_for_unknown_transform(movie_spec):
    rule = {"key": "k", "extractor": {"path": "/", "transforms": ["UNKNOWN"]}}
    with pytest.raises(ValueError):
        _ = piculet.load_spec(movie_spec | {"rules": [rule]})


def test_load_spec_should_load_tree_path_from_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "/"}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    assert isinstance(spec.rules[0].extractor.path, piculet.TreePath)


def test_dump_spec_should_dump_tree_path_as_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "/"}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["path"] == "/"


def test_load_spec_should_load_map_path_from_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "p"}}
    spec = piculet.load_spec(movie_spec | {"path_type": "jmespath", "rules": [rule]})
    assert isinstance(spec.rules[0].extractor.path, piculet.MapPath)


def test_dump_spec_should_dump_map_path_as_str(movie_spec):
    rule = {"key": "k", "extractor": {"path": "p"}}
    spec = piculet.load_spec(movie_spec | {"path_type": "jmespath", "rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["path"] == "p"


def test_scrape_should_produce_empty_result_for_empty_rules(movie, movie_spec):
    spec = piculet.load_spec(movie_spec)
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {}


def test_scrape_should_produce_scalar_text(movie, movie_spec):
    rule = {"key": "title", "extractor": {"path": "//title/text()"}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, rules=spec.rules, doctype="html")
    assert data == {"title": "The Shining"}


def test_scrape_should_produce_concatenated_text(movie, movie_spec):
    rule = {"key": "full_title", "extractor": {"path": "//h1//text()"}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"full_title": "The Shining (1980)"}


def test_scrape_should_produce_concatenated_text_using_given_separator(movie, movie_spec):
    rule = {"key": "cast_names", "extractor": {"path": '//table[@class="cast"]/tr/td[1]/a/text()', "sep": ", "}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"cast_names": "Jack Nicholson, Shelley Duvall"}


def test_scrape_should_transform_text(movie, movie_spec):
    rule = {"key": "year", "extractor": {"path": '//span[@class="year"]/text()', "transforms": ["int"]}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"year": 1980}


def test_scrape_should_produce_multiple_items_for_multiple_rules(movie, movie_spec):
    rules = [
        {"key": "title", "extractor": {"path": "//title/text()"}},
        {"key": "year", "extractor": {"path": '//span[@class="year"]/text()', "transforms": ["int"]}},
    ]
    spec = piculet.load_spec(movie_spec | {"rules": rules})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"title": "The Shining", "year": 1980}


def test_scrape_should_exclude_data_for_rules_with_no_result(movie, movie_spec):
    rules = [
        {"key": "title", "extractor": {"path": "//title/text()"}},
        {"key": "foo", "extractor": {"path": "//foo/text()"}},
    ]
    spec = piculet.load_spec(movie_spec | {"rules": rules})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"title": "The Shining"}


def test_scrape_should_produce_list_for_multivalued_rule(movie, movie_spec):
    rule = {"key": "genres", "extractor": {"foreach": '//ul[@class="genres"]/li', "path": "./text()"}}
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"genres": ["Horror", "Drama"]}


def test_scrape_should_transform_each_item_in_multivalued_result(movie, movie_spec):
    rule = {
        "key": "genres",
        "extractor": {
            "foreach": '//ul[@class="genres"]/li',
            "path": "./text()",
            "transforms": ["lower"],
        },
    }
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"genres": ["horror", "drama"]}


def test_scrape_should_exclude_empty_items_in_multivalued_rule_results(movie, movie_spec):
    rule = {
        "key": "foos",
        "extractor": {
            "foreach": '//ul[@class="foos"]/li',
            "path": "./text()",
        },
    }
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {}


def test_scrape_should_produce_subitems_for_subrules(movie, movie_spec):
    rule = {
        "key": "director",
        "extractor": {
            "rules": [
                {"key": "name", "extractor": {"path": '//div[@class="director"]//a/text()'}},
                {"key": "link", "extractor": {"path": '//div[@class="director"]//a/@href'}},
            ],
        },
    }
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {"director": {"link": "/people/1", "name": "Stanley Kubrick"}}


def test_scrape_should_produce_subitem_lists_for_multivalued_subrules(movie, movie_spec):
    rule = {
        "key": "cast",
        "extractor": {
            "foreach": '//table[@class="cast"]/tr',
            "rules": [
                {"key": "name", "extractor": {"path": "./td[1]/a/text()"}},
                {"key": "character", "extractor": {"path": "./td[2]/text()"}},
            ],
        },
    }
    spec = piculet.load_spec(movie_spec | {"rules": [rule]})
    data = piculet.scrape(movie, doctype=spec.doctype, rules=spec.rules)
    assert data == {
        "cast": [
            {"character": "Jack Torrance", "name": "Jack Nicholson"},
            {"character": "Wendy Torrance", "name": "Shelley Duvall"},
        ]
    }
