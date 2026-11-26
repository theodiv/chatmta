from chatmta.exceptions import ChatMTAError


def test_root_error_is_an_exception_but_not_an_argument_error() -> None:
    assert issubclass(ChatMTAError, Exception)
    assert not issubclass(ChatMTAError, (TypeError, ValueError))
