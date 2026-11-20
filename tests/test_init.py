import importlib
import re
import sys

import pytest

import chatmta
from chatmta import __version__
from chatmta.model import api


def test_version_reads_release_or_release_candidate() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+(?:rc\d+)?", __version__) is not None


@pytest.mark.parametrize("name", chatmta.__all__)
def test_every_public_name_is_the_one_the_plugin_api_defines(name: str) -> None:
    assert getattr(chatmta, name) is getattr(api, name)


def test_import_loads_the_plugin_api_and_nothing_else_of_the_package(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in [name for name in sys.modules if _in_package(name)]:
        monkeypatch.delitem(sys.modules, name)

    importlib.import_module("chatmta")

    assert {name for name in sys.modules if _in_package(name)} == {
        "chatmta",
        "chatmta.model",
        "chatmta.model.api",
    }


def _in_package(name: str) -> bool:
    """Return whether `name` is the package or one of its modules."""
    return name == "chatmta" or name.startswith("chatmta.")
