"""Sendmail-compatible MTA that delivers cron and system mail to chat apps."""

from chatmta.model.plugin_api import (
    PLUGIN_API_VERSION,
    Attachment,
    Body,
    ChatMessage,
    Contents,
    CredentialUnavailable,
    DeliveryJob,
    Destination,
    Failed,
    Finding,
    Mail,
    Moved,
    Outcome,
    Plugin,
    RenderJob,
    RetryLater,
    Sent,
    ValidationJob,
)

__version__ = "0.0.0"

__all__ = [
    "PLUGIN_API_VERSION",
    "Attachment",
    "Body",
    "ChatMessage",
    "Contents",
    "CredentialUnavailable",
    "DeliveryJob",
    "Destination",
    "Failed",
    "Finding",
    "Mail",
    "Moved",
    "Outcome",
    "Plugin",
    "RenderJob",
    "RetryLater",
    "Sent",
    "ValidationJob",
]
