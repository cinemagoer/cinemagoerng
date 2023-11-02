from pytest import mark, raises

import re

from cinemagoerng import __version__, cli


def test_cli_should_report_correct_version(capsys):
    with raises(SystemExit):
        cli.main(["--version"])
    std = capsys.readouterr()
    assert std.out.strip() == __version__


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_title_and_type(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Title: (\w|\s)+ \(Movie\)\n", std.out)


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_year(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Year: [12]\d{3}\n", std.out)


@mark.parametrize(("imdb_id",), [
    (3629794,),  # Aslan
])
def test_cli_get_title_should_exclude_year_if_missing(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Year:" not in std.out


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_runtime(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Runtime: \d+ min\n", std.out)


@mark.parametrize(("imdb_id",), [
    (3629794,),  # Aslan
])
def test_cli_get_title_should_exclude_runtime_if_missing(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Runtime:" not in std.out


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_rating(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Rating: \d+\.\d+ \(\d+ votes\)\n", std.out)


@mark.parametrize(("imdb_id",), [
    (3629794,),  # Aslan
])
def test_cli_get_title_should_exclude_rating_if_missing(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Rating:" not in std.out


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_genres(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Genres: [\w]+(, [\w-]+)*\n", std.out)


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_plot(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Plot:\n  [\w]+", std.out)


@mark.parametrize(("imdb_id",), [
    (3629794,),  # Aslan
])
def test_cli_get_title_should_exclude_plot_if_missing(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Plot:" not in std.out


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_exclude_taglines_by_default(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Taglines:" not in std.out


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix
])
def test_cli_get_title_should_include_taglines_if_requested(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id), "--taglines"])
    std = capsys.readouterr()
    assert re.search(r"Taglines:\n  \w+", std.out)
