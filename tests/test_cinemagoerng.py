from importlib import metadata

import cinemagoerng


def test_installed_version_should_match_tested_version():
    assert metadata.version("cinemagoerng") == cinemagoerng.__version__
