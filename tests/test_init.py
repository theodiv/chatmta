import importlib
import re
import sys

import pytest

import chatmta
from chatmta import __version__


def test_version_reads_release_or_release_candidate() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:rc\d+)?", __version__) is not None


def test_every_name_in_all_resolves() -> None:
    assert all(hasattr(chatmta, name) for name in chatmta.__all__)


def test_import_loads_the_plugin_api_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in [name for name in sys.modules if _is_package_module(name)]:
        monkeypatch.delitem(sys.modules, name)

    importlib.import_module("chatmta")

    assert {name for name in sys.modules if _is_package_module(name)} == {
        "chatmta",
        "chatmta.model",
        "chatmta.model.plugin_api",
    }


def _is_package_module(name: str) -> bool:
    return name == "chatmta" or name.startswith("chatmta.")
