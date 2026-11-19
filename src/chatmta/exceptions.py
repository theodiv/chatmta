"""Exception hierarchy rooted at `ChatMTAError`."""


class ChatMTAError(Exception):
    """Root of the exceptions the package defines.

    Each exception class the package defines derives from it, so one `except` clause
    catches them all.
    """
