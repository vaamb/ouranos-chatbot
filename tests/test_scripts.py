from __future__ import annotations

from pathlib import Path
import typing as t
from unittest import TestCase

from ouranos_chatbot import __version__

if t.TYPE_CHECKING:
    import re


def _get_var_value(var_name: str, script_path: Path) -> str:
    with open(script_path, "r") as f:
        for line in f:
            if f"{var_name}=" in line or f"{var_name} = " in line:
                return line.split("=", 1)[1].strip().strip('"')
    raise ValueError(f"Variable {var_name} not found in {script_path}")


def _get_pattern(script_path: Path, pattern: re.Pattern) -> str:
    with open(script_path, "r") as f:
        script_text = f.read()

    search = pattern.search(script_text)
    if search is not None:
        return search.group(0)
    raise ValueError(f"Pattern {pattern} not found in {script_path}")


class TestInstallScript(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).parents[1]
        cls.scripts_dir = cls.root_dir / "scripts"
        cls.install_script_path = cls.scripts_dir / "install.sh"
        cls.update_script_path = cls.scripts_dir / "update.sh"

    def test_chatbot_version(self):
        # Sync the version between ouranos-chatbot and install.sh
        install_version = _get_var_value("OURANOS_CHATBOT_VERSION", self.install_script_path)

        assert install_version == __version__
