"""The calls a platform plugin implements and the values they exchange with the core.

It imports the standard library alone, so a plugin's `import chatmta` loads no other
module of the package.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import ClassVar, Final, Literal, Protocol, TypeAlias

PLUGIN_API_VERSION: Final = 1


@dataclass(frozen=True, kw_only=True)
class Destination:
    """A destination the configuration names, as its plugin receives it.

    Attributes:
        name: The destination's name in the configuration.
        options: The destination's keys other than `type`, for the plugin to narrow; a
            read-only copy of the mapping passed in.
    """

    name: str
    # Left out of the hash, since the dict a `MappingProxyType` wraps has none.
    options: Mapping[str, object] = field(hash=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))


@dataclass(frozen=True, kw_only=True)
class Body:
    """The part of a mail that a plugin shows as its text.

    Attributes:
        section: The part's MIME section path, such as `1` or `1.1`.
        text: The body as plain text, also for a mail whose body is HTML alone.
        html: The source of the HTML part, or `None` when the mail has none.
    """

    section: str
    text: str
    html: str | None


@dataclass(frozen=True, kw_only=True)
class Attachment:
    """A part of a mail that a plugin may send as a file.

    Attributes:
        section: The part's MIME section path, such as `2` or `1.2`.
        name: The file name the mail gives the part, or `None` when it gives none.
        content_type: The part's MIME type, such as `image/png`.
        size: The part's size in bytes once its transfer encoding is undone.
        content_id: The part's `Content-ID` without its angle brackets, or `None` when
            it has none.
    """

    section: str
    name: str | None
    content_type: str
    size: int
    content_id: str | None


@dataclass(frozen=True, kw_only=True)
class Mail:
    """A mail as a plugin renders it, without the bytes of its parts.

    Attributes:
        outbox_id: The mail's identifier in the outbox.
        envelope_sender: The envelope sender, as submitted.
        envelope_recipients: The envelope recipients that no header of the mail names.
        sender: The sender the mail's headers name.
        subject: The subject, empty when the mail has none.
        body: The body, or `None` when the mail has none.
        attachments: The attachments, in the mail's order.
        host: The host the mail was submitted on.
        received: When ChatMTA received the mail, an aware UTC `datetime`.
        bytes_cut: The bytes cut from the end of a mail past the size limit, `0` when
            none were.
    """

    outbox_id: str
    envelope_sender: str
    envelope_recipients: tuple[str, ...]
    sender: str
    subject: str
    body: Body | None
    attachments: tuple[Attachment, ...]
    host: str
    received: datetime
    bytes_cut: int = 0


class Contents(Protocol):
    """The decoded parts of one mail, read only when a plugin needs them."""

    def data(self, section: str) -> bytes | None:
        """Return the bytes of `section` with its transfer encoding undone.

        Returns:
            The bytes, or `None` when the mail has no such section.
        """

    def text(self, section: str) -> str | None:
        """Return the text of `section`, decoded with its charset.

        Returns:
            The text, or `None` when the mail has no such section.
        """


@dataclass(frozen=True, kw_only=True)
class ValidationJob:
    """What `Plugin.validate` checks.

    Attributes:
        destination: The destination to check.
    """

    destination: Destination


@dataclass(frozen=True, kw_only=True)
class RenderJob:
    """What `Plugin.render` turns into chat messages.

    Attributes:
        mail: The mail to render.
        destination: The destination the mail goes to.
        contents: The mail's decoded parts.
        silent: Whether the rule asks for delivery without a notification.
        style: The body style the rule names, `"plain"`, `"quote"`, or `"code"`, or
            `None` when it names none, so the plugin's own default applies.
    """

    mail: Mail
    destination: Destination
    contents: Contents
    silent: bool = False
    style: Literal["plain", "quote", "code"] | None


@dataclass(frozen=True, kw_only=True)
class Finding:
    """A problem or a remark that `Plugin.validate` reports about a destination.

    Attributes:
        level: How much it matters: `"error"`, `"warning"`, or `"note"`.
        about: What it concerns: `"option"` or `"credential"`.
        message: Full sentences naming the option or the credential's path, never
            the credential.
    """

    level: Literal["error", "warning", "note"]
    about: Literal["option", "credential"]
    message: str


@dataclass(frozen=True, kw_only=True)
class ChatMessage:
    """One chat message that `Plugin.render` returns for `Plugin.deliver` to send.

    Attributes:
        kind: The plugin's label for the message's layout.
        text: The message's text.
        fields: The other strings the plugin needs to send the message; a read-only copy
            of the mapping passed in.
        sections: The section paths of the mail's parts the message sends.
    """

    kind: str
    text: str = ""
    # Left out of the hash, since the dict a `MappingProxyType` wraps has none.
    fields: Mapping[str, str] = field(hash=False)
    sections: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))


@dataclass(frozen=True, kw_only=True)
class DeliveryJob:
    """What `Plugin.deliver` sends.

    Attributes:
        chat_message: The chat message to send.
        destination: The destination to send to.
        refs: The `Sent.ref` of each earlier chat message of the same mail and
            destination, in order.
        now: The time of the attempt, an aware UTC `datetime`.
        time_left: The seconds the plugin has left for the attempt.
        contents: The mail's decoded parts.
    """

    chat_message: ChatMessage
    destination: Destination
    refs: tuple[str | None, ...]
    now: datetime
    time_left: float
    contents: Contents


@dataclass(frozen=True, kw_only=True)
class Sent:
    """The outcome of a chat message the platform accepted.

    Attributes:
        ref: The platform's reference to the message, or `None` when it returns none.
    """

    ref: str | None


@dataclass(frozen=True, kw_only=True)
class RetryLater:
    """The outcome of a chat message that a later attempt may deliver.

    Attributes:
        reason: One sentence on why, which holds no credential.
        delay: The seconds the platform asks to wait, or `None` when it names none.
    """

    reason: str
    delay: float | None


@dataclass(frozen=True, kw_only=True)
class Failed:
    """The outcome of a chat message that no later attempt would deliver.

    Attributes:
        reason: Why, such as the platform's own description.
    """

    reason: str


@dataclass(frozen=True, kw_only=True)
class Moved:
    """The outcome when the platform reports the conversation under a new value.

    A plugin returns it only when the conversation stays the same and only its address
    changed, such as a group that became a supergroup.

    Attributes:
        option: The option whose value moved, such as `chat`.
        value: The option's new value.
    """

    option: str
    value: str | int


@dataclass(frozen=True, kw_only=True)
class CredentialUnavailable:
    """The outcome when the running account may not read the credential it needs.

    Attributes:
        reason: Why, naming the credential's path, never its content.
    """

    reason: str


Outcome: TypeAlias = Sent | RetryLater | Failed | Moved | CredentialUnavailable


class Plugin(Protocol):
    """The class a `chatmta.platforms` entry point names.

    A class meets it without deriving from it.

    Attributes:
        api_version: The `PLUGIN_API_VERSION` the plugin is built for.
    """

    api_version: ClassVar[int]

    def validate(self, job: ValidationJob) -> tuple[Finding, ...]:
        """Return the findings about `job.destination`, opening no connection."""

    def render(self, job: RenderJob) -> tuple[ChatMessage, ...]:
        """Return the chat messages for `job.mail`, in the order they are sent."""

    def deliver(self, job: DeliveryJob) -> Outcome:
        """Send `job.chat_message` and return what became of it."""
