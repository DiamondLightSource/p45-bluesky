import subprocess
import sys

from p45_bluesky import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "p45_bluesky", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
