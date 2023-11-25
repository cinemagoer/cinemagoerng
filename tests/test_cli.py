from pytest import mark, raises

import re

from cinemagoerng import __version__, cli


def test_cli_should_report_correct_version(capsys):
    with raises(SystemExit):
        cli.main(["--version"])
    std = capsys.readouterr()
    assert std.out.strip() == __version__


@mark.live
def test_cli_get_title_should_report_error_for_nonexisting_imdb_id(capsys):
    with raises(SystemExit):
        cli.main(["get", "title", "133093133"])
    std = capsys.readouterr()
    assert std.out.strip() == "No title with this IMDb id was found."


@mark.parametrize(("imdb_id",), [
    (133093,),  # The Matrix (Movie)
    (389150,),  # The Matrix Defence (TV Movie)
    (2971344,),  # Matrix: First Dream (Short Movie)
    (365467,),  # Making 'The Matrix' (TV Short Movie)
    (109151,),  # Armitage III: Poly-Matrix (Video Movie)
    (7045440,),  # David Bowie: Ziggy Stardust (Music Video)
    (390244,),  # The Matrix Online (Video Game)
    (436992,),  # Doctor Who (TV Series)
    (185906,),  # Band of Brothers (TV Mini-Series)
    (1000252,),  # Blink (TV Episode)
    (14544192,),  # Bo Burnham: Inside (TV Special)
])
def test_cli_get_title_should_include_title_and_type(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert re.search(r"Title: (\w|\s|:|-|')+ \((\w|\s|-)+\)\n", std.out)


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
    assert re.search(r"Taglines:\n  - \w+", std.out)
