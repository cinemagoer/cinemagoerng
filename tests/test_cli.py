from pytest import mark, raises

from cinemagoerng import __version__, cli


def test_cli_should_report_correct_version(capsys):
    with raises(SystemExit):
        cli.main(["--version"])
    std = capsys.readouterr()
    assert std.out.strip() == __version__


@mark.parametrize(("imdb_id", "title", "type_name"), [
    (133093, "The Matrix", "Movie"),
    (389150, "The Matrix Defence", "TV Movie"),
    (2971344, "Matrix: First Dream", "Short Movie"),
    (365467, "Making 'The Matrix'", "TV Short Movie"),
    (109151, "Armitage III: Poly-Matrix", "Video Movie"),
    (7045440, "David Bowie: Ziggy Stardust", "Music Video"),
    (390244, "The Matrix Online", "Video Game"),
    (436992, "Doctor Who", "TV Series"),
    (185906, "Band of Brothers", "TV Mini-Series"),
    (1000252, "Blink", "TV Series Episode"),
    (14544192, "Bo Burnham: Inside", "TV Special"),
])
def test_cli_get_title_should_include_title_and_type(capsys, imdb_id, title, type_name):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert f"Title: {title} ({type_name})" in std.out


@mark.parametrize(("imdb_id", "year"), [
    (133093, 1999),  # The Matrix
])
def test_cli_get_title_should_include_year(capsys, imdb_id, year):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert f"Year: {year}" in std.out


@mark.parametrize(("imdb_id",), [
    (3629794,),  # Aslan
])
def test_cli_get_title_should_exclude_year_if_missing(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Year:" not in std.out


@mark.parametrize(("imdb_id", "runtime"), [
    (133093, 136),  # The Matrix
])
def test_cli_get_title_should_include_runtime(capsys, imdb_id, runtime):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert f"Runtime: {runtime} min" in std.out


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
def test_cli_get_title_should_exclude_taglines_by_default(capsys, imdb_id):
    cli.main(["get", "title", str(imdb_id)])
    std = capsys.readouterr()
    assert "Taglines:" not in std.out


@mark.parametrize(("imdb_id", "tagline"), [
    (133093, "Free your mind"),  # The Matrix
])
def test_cli_get_title_should_include_taglines_if_requested(capsys, imdb_id, tagline):
    cli.main(["get", "title", str(imdb_id), "--taglines"])
    std = capsys.readouterr()
    assert f"Taglines:\n  {tagline}" in std.out
