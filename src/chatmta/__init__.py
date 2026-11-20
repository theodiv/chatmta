"""Sendmail-compatible MTA that delivers cron and system mail to chat apps.

Public surface
--------------
- `API_VERSION`: the version of the plugin API this release implements.
- `Attachment`: a file a mail carries, described without its bytes.
- `Body`: the part of a mail chosen as the text to show.
- `Choices`: what the rule that chose a destination asks of the delivery.
- `Contents`: reads a mail's body and files back by MIME section path.
- `CredentialUnavailable`: the outcome of a credential the running account cannot use.
- `DeliveryJob`: one part for one destination, which `Plugin.deliver` sends.
- `Destination`: a destination as the plugin that delivers it sees it.
- `Failed`: the outcome of a part the platform refused for good.
- `Finding`: one problem or remark that `Plugin.validate` reports.
- `Mail`: one mail, decoded, as a plugin renders it.
- `Moved`: the outcome of a destination the platform moved.
- `Outcome`: any of the five outcomes `Plugin.deliver` returns.
- `Part`: one piece of a rendered mail, as plain data.
- `Plugin`: what a plugin's entry point names.
- `RenderJob`: one mail for one destination, which `Plugin.render` turns into parts.
- `RetryLater`: the outcome of a part that may succeed later.
- `Sent`: the outcome of a part the platform accepted.
"""

from chatmta.model.api import (
    API_VERSION,
    Attachment,
    Body,
    Choices,
    Contents,
    CredentialUnavailable,
    DeliveryJob,
    Destination,
    Failed,
    Finding,
    Mail,
    Moved,
    Outcome,
    Part,
    Plugin,
    RenderJob,
    RetryLater,
    Sent,
)

__version__ = "0.0.0"

__all__ = [
    "API_VERSION",
    "Attachment",
    "Body",
    "Choices",
    "Contents",
    "CredentialUnavailable",
    "DeliveryJob",
    "Destination",
    "Failed",
    "Finding",
    "Mail",
    "Moved",
    "Outcome",
    "Part",
    "Plugin",
    "RenderJob",
    "RetryLater",
    "Sent",
]
