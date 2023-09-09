import subprocess
import sys
from pathlib import Path

import cinemagoerng


cli = Path(sys.executable).with_name("cinemagoerng")


def test_installation_should_create_cli_script():
    assert cli.exists()


def test_cli_should_report_correct_version(capfd):
    subprocess.run([cli] + ["--version"])
    std = capfd.readouterr()
    assert std.out.strip() == cinemagoerng.__version__
