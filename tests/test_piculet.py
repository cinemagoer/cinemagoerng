import pytest

from dataclasses import dataclass
from decimal import Decimal

from cinemagoerng import piculet

MOVIE_XML_SPEC = {
    "version": "1",
    "url": "",
    "doctype": "xml",
    "path_type": "xpath",
}

MOVIE_XML = """
<html>
<head>
  <title>The Shining</title>
</head>
<body>
  <h1>The Shining (<span class="year">1980</span>)</h1>
  <ul class="genres">
    <li>Horror</li>
    <li>Drama</li>
  </ul>
  <div class="director">
    <h3>Director:</h3>
    <p><a href="/people/1">Stanley Kubrick</a></p>
  </div>
  <table class="cast">
    <tr>
      <td><a href="/people/2">Jack Nicholson</a></td>
      <td>Jack Torrance</td>
    </tr>
    <tr>
      <td><a href="/people/3">Shelley Duvall</a></td>
      <td>Wendy Torrance</td>
    </tr>
    </table>
  <div class="info">
    <h3>Country</h3>
    <p>United States</p>
  </div>
  <div class="info">
    <h3>Language</h3>
    <p>English</p>
  </div>
</body>
</html>
"""

MOVIE_JSON_SPEC = {
    "version": "1",
    "url": "",
    "doctype": "json",
    "path_type": "jmespath",
}

MOVIE_JSON = """
{
  "title": "The Shining",
  "year": 1980,
  "genres": [
    {"name": "Horror"},
    {"name": "Drama"}
  ],
  "director": {
    "id": 1,
    "name": "Stanley Kubrick"
  },
  "cast": [
    {
      "id": 2,
      "name": "Jack Nicholson",
      "character": "Jack Torrance"
    },
    {
      "id": 3,
      "name": "Shelley Duvall",
      "character": "Wendy Torrance"
    }
  ],
  "info": {
    "production": [
      {
        "name": "Country",
        "value": "United States"
      },
      {
        "name": "Language",
        "value": "English"
      }
    ],
    "info": {
      "runtime": 144
    }
  }
}
"""

piculet.preprocessors.update(
    {
        "nothing": lambda x: x,
        "first_subtree": lambda x: x.xpath('./*[1]')[0],
        "first_submap": lambda x: x.get("info", {}),
        "empty_tree": lambda _: piculet._PARSERS["xml"]("<root/>"),
        "empty_map": lambda _: {},
    }
)

piculet.postprocessors.update(
    {
        "nothing": lambda x: x,
        "shorten": lambda x: {k[:-1]: v[:-1] for k, v in x.items()},
    }
)


@dataclass
class Movie:
    score: Decimal


def test_deserialize_should_support_decimal():
    movie = piculet.deserialize({"score": "9.8"}, Movie)
    assert isinstance(movie.score, Decimal) and (movie.score.as_integer_ratio() == (49, 5))


def test_serialize_should_support_decimal():
    movie = Movie(score=Decimal("9.8"))
    assert isinstance(movie.score, Decimal) and (piculet.serialize(movie) == {"score": "9.8"})


def test_load_spec_should_load_preprocess_from_str():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"pre": ["nothing"], "rules": []})
    assert isinstance(spec.pre[0], piculet.Preprocess)


def test_dump_spec_should_dump_preprocess_as_str():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"pre": ["nothing"], "rules": []})
    assert piculet.dump_spec(spec)["pre"][0] == "nothing"


def test_load_spec_should_raise_error_for_unknown_preprocess():
    with pytest.raises(ValueError):
        _ = piculet.load_spec(MOVIE_XML_SPEC | {"pre": ["UNKNOWN"], "rules": []})


def test_load_spec_should_load_postprocess_from_str():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"post": ["nothing"], "rules": []})
    assert isinstance(spec.post[0], piculet.Postprocess)


def test_dump_spec_should_dump_postprocess_as_str():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"post": ["nothing"], "rules": []})
    assert piculet.dump_spec(spec)["post"][0] == "nothing"


def test_load_spec_should_raise_error_for_unknown_postprocess():
    with pytest.raises(ValueError):
        _ = piculet.load_spec(MOVIE_XML_SPEC | {"post": ["UNKNOWN"], "rules": []})


def test_load_spec_should_load_transform_from_str():
    rule = {"key": "k", "extractor": {"path": '/', "transforms": ["strip"]}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    assert isinstance(spec.rules[0].extractor.transforms[0], piculet.Transform)


def test_dump_spec_should_dump_transform_as_str():
    rule = {"key": "k", "extractor": {"path": '/', "transforms": ["strip"]}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["transforms"][0] == "strip"


def test_load_spec_should_raise_error_for_unknown_transform():
    rule = {"key": "k", "extractor": {"path": '/', "transforms": ["UNKNOWN"]}}
    with pytest.raises(ValueError):
        _ = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})


def test_load_spec_should_load_xml_path_from_str():
    rule = {"key": "k", "extractor": {"path": '/'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    assert isinstance(spec.rules[0].extractor.path, piculet.XMLPath)


def test_dump_spec_should_dump_xml_path_as_str():
    rule = {"key": "k", "extractor": {"path": '/'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["path"] == "/"


def test_load_spec_should_load_json_path_from_str():
    rule = {"key": "k", "extractor": {"path": 'p'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    assert isinstance(spec.rules[0].extractor.path, piculet.JSONPath)


def test_dump_spec_should_dump_json_path_as_str():
    rule = {"key": "k", "extractor": {"path": 'p'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    assert piculet.dump_spec(spec)["rules"][0]["extractor"]["path"] == "p"


def test_scrape_xml_should_produce_empty_result_for_empty_rules():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": []})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {}


def test_scrape_json_should_produce_empty_result_for_empty_rules():
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": []})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {}


def test_scrape_xml_should_produce_scalar_text():
    rule = {"key": "title", "extractor": {"path": '//title/text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "The Shining"}


def test_scrape_xml_should_support_string_join():
    rule = {"key": "full_title", "extractor": {"path": 'string-join(//h1//text(), "")'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"full_title": "The Shining (1980)"}


def test_scrape_xml_should_support_string_join_using_given_separator():
    rule = {"key": "cast_names", "extractor": {"path": 'string-join(//table[@class="cast"]/tr/td[1]/a/text(), ", ")'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"cast_names": "Jack Nicholson, Shelley Duvall"}


def test_scrape_json_should_produce_scalar_text():
    rule = {"key": "title", "extractor": {"path": 'title'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"title": "The Shining"}


def test_scrape_xml_should_transform_text():
    rule = {"key": "title", "extractor": {"path": '//title/text()'}, "transforms": ["lower"]}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "the shining"}


def test_scrape_json_should_transform_text():
    rule = {"key": "title", "extractor": {"path": 'title'}, "transforms": ["lower"]}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"title": "the shining"}


def test_scrape_xml_should_produce_multiple_items_for_multiple_rules():
    rules = [
        {"key": "title", "extractor": {"path": '//title/text()'}},
        {"key": "year", "extractor": {"path": '//span[@class="year"]/text()', "transforms": ["int"]}},
    ]
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": rules})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "The Shining", "year": 1980}


def test_scrape_json_should_produce_multiple_items_for_multiple_rules():
    rules = [
        {"key": "title", "extractor": {"path": 'title'}},
        {"key": "year", "extractor": {"path": 'year'}},
    ]
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": rules})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"title": "The Shining", "year": 1980}


def test_scrape_xml_should_exclude_data_for_rules_with_no_result():
    rules = [
        {"key": "title", "extractor": {"path": '//title/text()'}},
        {"key": "foo", "extractor": {"path": '//foo/text()'}},
    ]
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": rules})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "The Shining"}


def test_scrape_json_should_exclude_data_for_rules_with_no_result():
    rules = [
        {"key": "title", "extractor": {"path": 'title'}},
        {"key": "foo", "extractor": {"path": 'foo'}},
    ]
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": rules})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"title": "The Shining"}


def test_scrape_xml_should_produce_list_for_multivalued_rule():
    rule = {"key": "genres", "extractor": {"foreach": '//ul[@class="genres"]/li', "path": './text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"genres": ["Horror", "Drama"]}


def test_scrape_json_should_produce_list_for_multivalued_rule():
    rule = {"key": "genres", "extractor": {"foreach": 'genres[*]', "path": 'name'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"genres": ["Horror", "Drama"]}


def test_scrape_xml_should_transform_each_item_in_multivalued_result():
    rule = {
        "key": "genres",
        "extractor": {
            "foreach": '//ul[@class="genres"]/li',
            "path": './text()',
            "transforms": ["lower"],
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"genres": ["horror", "drama"]}


def test_scrape_json_should_transform_each_item_in_multivalued_result():
    rule = {
        "key": "genres",
        "extractor": {
            "foreach": 'genres[*]',
            "path": 'name',
            "transforms": ["lower"],
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"genres": ["horror", "drama"]}


def test_scrape_xml_should_exclude_empty_items_in_multivalued_rule_results():
    rule = {
        "key": "foos",
        "extractor": {
            "foreach": '//ul[@class="foos"]/li',
            "path": './text()',
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {}


def test_scrape_json_should_exclude_empty_items_in_multivalued_rule_results():
    rule = {
        "key": "foos",
        "extractor": {
            "foreach": 'foos[*]',
            "path": 'text',
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {}


def test_scrape_xml_should_produce_subitems_for_subrules():
    rule = {
        "key": "director",
        "extractor": {
            "rules": [
                {"key": "link", "extractor": {"path": '//div[@class="director"]//a/@href'}},
                {"key": "name", "extractor": {"path": '//div[@class="director"]//a/text()'}},
            ],
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"director": {"link": "/people/1", "name": "Stanley Kubrick"}}


def test_scrape_json_should_produce_subitems_for_subrules():
    rule = {
        "key": "director",
        "extractor": {
            "rules": [
                {"key": "id", "extractor": {"path": 'director.id'}},
                {"key": "name", "extractor": {"path": 'director.name'}},
            ],
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"director": {"id": 1, "name": "Stanley Kubrick"}}


def test_scrape_xml_should_produce_subitem_lists_for_multivalued_subrules():
    rule = {
        "key": "cast",
        "extractor": {
            "foreach": '//table[@class="cast"]/tr',
            "rules": [
                {"key": "name", "extractor": {"path": './td[1]/a/text()'}},
                {"key": "character", "extractor": {"path": './td[2]/text()'}},
            ],
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {
        "cast": [
            {"name": "Jack Nicholson", "character": "Jack Torrance"},
            {"name": "Shelley Duvall", "character": "Wendy Torrance"},
        ]
    }


def test_scrape_json_should_produce_subitem_lists_for_multivalued_subrules():
    rule = {
        "key": "cast",
        "extractor": {
            "foreach": 'cast[*]',
            "rules": [
                {"key": "name", "extractor": {"path": 'name'}},
                {"key": "character", "extractor": {"path": 'character'}},
            ],
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {
        "cast": [
            {"name": "Jack Nicholson", "character": "Jack Torrance"},
            {"name": "Shelley Duvall", "character": "Wendy Torrance"},
        ]
    }


def test_scrape_xml_should_produce_multiple_data_for_multiple_sections():
    rule = {
        "foreach": '//div[@class="info"]',
        "key": {
            "path": './h3/text()'
        },
        "extractor": {
            "path": './p/text()'
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {
        "Country": "United States",
        "Language": "English"
    }


def test_scrape_json_should_produce_multiple_data_for_multiple_sections():
    rule = {
        "foreach": 'info.production[*]',
        "key": {
            "path": 'name'
        },
        "extractor": {
            "path": 'value'
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {
        "Country": "United States",
        "Language": "English"
    }


def test_scrape_xml_should_transform_key_for_section():
    rule = {
        "foreach": '//div[@class="info"]',
        "key": {
            "path": './h3/text()',
            "transforms": ["lower"]
        },
        "extractor": {
            "path": './p/text()'
        },
    }
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {
        "country": "United States",
        "language": "English"
    }


def test_scrape_json_should_transform_key_for_section():
    rule = {
        "foreach": 'info.production[*]',
        "key": {
            "path": 'name',
            "transforms": ["lower"]
        },
        "extractor": {
            "path": 'value'
        },
    }
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {
        "country": "United States",
        "language": "English"
    }


def test_scrape_xml_should_apply_preprocess():
    rule = {"key": "title", "extractor": {"path": './title/text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"pre": ["first_subtree"], "rules": [rule]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "The Shining"}


def test_scrape_json_should_apply_preprocess():
    rule = {"key": "country", "extractor": {"path": 'production[0].value'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"pre": ["first_submap"], "rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"country": "United States"}


def test_scrape_xml_should_apply_multiple_preprocesses():
    rule = {"key": "title", "extractor": {"path": './text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule], "pre": ["first_subtree", "first_subtree"]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"title": "The Shining"}


def test_scrape_json_should_apply_multiple_preprocesses():
    rule = {"key": "runtime", "extractor": {"path": 'runtime'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"pre": ["first_submap", "first_submap"], "rules": [rule]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"runtime": 144}


def test_scrape_xml_should_apply_postprocess():
    rule = {"key": "title", "extractor": {"path": '//title/text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule], "post": ["shorten"]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"titl": "The Shinin"}


def test_scrape_json_should_apply_postprocess():
    rule = {"key": "title", "extractor": {"path": 'title'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule], "post": ["shorten"]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"titl": "The Shinin"}


def test_scrape_xml_should_apply_multiple_postprocesses():
    rule = {"key": "title", "extractor": {"path": '//title/text()'}}
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"rules": [rule], "post": ["shorten", "shorten"]})
    data = piculet.scrape(MOVIE_XML, spec)
    assert data == {"tit": "The Shini"}


def test_scrape_json_should_apply_multiple_postprocesses():
    rule = {"key": "title", "extractor": {"path": 'title'}}
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"rules": [rule], "post": ["shorten", "shorten"]})
    data = piculet.scrape(MOVIE_JSON, spec)
    assert data == {"tit": "The Shini"}


def test_preprocess_should_produce_compatible_node_for_xml_spec():
    spec = piculet.load_spec(MOVIE_XML_SPEC | {"pre": ["empty_map"], "rules": []})
    with pytest.raises(TypeError):
        _ = piculet.scrape(MOVIE_XML, spec)


def test_preprocess_should_produce_compatible_node_for_json_spec():
    spec = piculet.load_spec(MOVIE_JSON_SPEC | {"pre": ["empty_tree"], "rules": []})
    with pytest.raises(TypeError):
        _ = piculet.scrape(MOVIE_JSON, spec)
