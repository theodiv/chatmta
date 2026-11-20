"""Plugin API: what a platform plugin implements, and the values it reads and returns.

Every value type is a frozen dataclass with keyword-only fields, and each plugin method
takes one argument, so a release can add a field with a default without changing the
meaning of a call a plugin makes. A mapping field holds a read-only copy of the mapping
passed in, so a dict the caller keeps never changes it. The module imports only the
standard library: `chatmta` re-exports every name it defines, and a plugin's
`import chatmta` loads nothing else of the package.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Final, Literal, Protocol, TypeAlias

# Rises only with a release that could make a plugin built for the previous
# version fail.
API_VERSION: Final = 1


@dataclass(frozen=True, kw_only=True)
class Destination:
    """A destination as the plugin that delivers it sees it.

    Attributes:
        name: The destination's name in the configuration.
        options: The destination's keys other than `type`, as a read-only copy, each
            value typed `object` for the plugin to narrow.
    """

    name: str
    options: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))


@dataclass(frozen=True, kw_only=True)
class Choices:
    """What the rule that chose a destination asks of the delivery.

    A rule that names no style leaves `style` unset, so a plugin can tell its own
    default from an explicit `"plain"`.

    Attributes:
        silent: Whether the destination's readers get no notification of the mail.
        style: How to set off the body, `"plain"`, `"quote"`, or `"code"`, each in the
            plugin's own way; `None` when the rule names no style.
    """

    silent: bool = False
    style: Literal["plain", "quote", "code"] | None = None


@dataclass(frozen=True, kw_only=True)
class Body:
    """The part of a mail chosen as the text to show.

    Attributes:
        section: The MIME section path of the part, such as `1` or `1.1`.
        subtype: `"plain"` for text to show as written, `"html"` for HTML source.
        text: The decoded text.
    """

    section: str
    subtype: Literal["plain", "html"]
    text: str


@dataclass(frozen=True, kw_only=True)
class Attachment:
    """A file a mail carries, an inline image included, described without its bytes.

    A plugin reads the bytes through `Contents`, by `section`, when it sends the file.

    Attributes:
        section: The MIME section path of the file, such as `2`.
        name: The file name the mail gives, or `None` when it gives none.
        content_type: The MIME type, such as `image/png`.
        size: The decoded size in bytes.
        content_id: The `Content-ID` that HTML in the mail refers to, without its angle
            brackets, or `None`.
    """

    section: str
    name: str | None
    content_type: str
    size: int
    content_id: str | None = None


@dataclass(frozen=True, kw_only=True)
class Mail:
    """One mail, decoded, as a plugin renders it.

    Attributes:
        outbox_id: The ID the outbox gave the mail.
        envelope_sender: The envelope sender.
        envelope_recipients: Every envelope recipient, including those no header
            names (`Bcc:`).
        sender: The sender to show, from the `From:` header or, when the mail has none,
            the name `-F` gave.
        subject: The decoded subject, or an empty string when the mail has none.
        body: The text to show, or `None` when the mail has none.
        attachments: The files the mail carries, in their order in the mail.
        host: The name of the host the mail comes from.
        received: When the outbox received the mail, an aware `datetime` in UTC.
        bytes_cut: How many bytes of the mail the outbox left out past its size
            limit, or `0`.
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
    """Reads the decoded parts of one mail back by MIME section path.

    Every job carries one, so a part can name a body or a file by its section path and
    leave the text and the bytes in the mail as received.
    """

    def data(self, section: str) -> bytes | None:
        """Return the bytes of `section`, its transfer encoding undone.

        `None` stands for a section the mail lacks.
        """

    def text(self, section: str) -> str | None:
        """Return the text of `section`, decoded with the charset it declares.

        `None` stands for a section the mail lacks or one that holds no text.
        """


@dataclass(frozen=True, kw_only=True)
class RenderJob:
    """One mail for one destination, which `Plugin.render` turns into parts.

    Attributes:
        mail: The mail.
        destination: The destination the parts go to.
        choices: What the rule that chose the destination asks of the delivery.
        contents: The mail's body and files, read back by section path.
    """

    mail: Mail
    destination: Destination
    choices: Choices
    contents: Contents


@dataclass(frozen=True, kw_only=True)
class Part:
    """One piece of a rendered mail, as plain data.

    A part holds strings alone, so it outlives a wait between attempts and an upgrade of
    ChatMTA or the plugin, and it names the body or a file by section path instead of
    copying its text or bytes. A plugin reads every format its earlier releases wrote
    under the same `API_VERSION`, and fails a part whose format it does not know,
    naming it.

    Attributes:
        format: The plugin's own label for the part's layout.
        text: The part's text, as the plugin rendered it.
        fields: Other string values the plugin needs at delivery, as a read-only copy.
        sections: The MIME section paths of the body or the files the part sends.
    """

    format: str
    text: str = ""
    fields: Mapping[str, str] = field(default_factory=dict)
    sections: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))


@dataclass(frozen=True, kw_only=True)
class DeliveryJob:
    """One part for one destination, which `Plugin.deliver` sends.

    Attributes:
        part: The part, as `Plugin.render` returned it.
        destination: The destination, its options holding the value of a kept `Moved`
            outcome in place of the option that outcome names.
        refs: The `Sent.ref` of each earlier part of the same mail and destination,
            in order.
        now: The current time, an aware `datetime` in UTC.
        time_left: Seconds until the attempt is stopped; a plugin keeps its timeouts
            within them, so it gives up first.
        contents: The mail's body and files, read back by section path.
    """

    part: Part
    destination: Destination
    refs: tuple[str | None, ...]
    now: datetime
    time_left: float
    contents: Contents


@dataclass(frozen=True, kw_only=True)
class Finding:
    """One problem or remark that `Plugin.validate` reports about a destination.

    An error about an option means the destination cannot work as configured. A finding
    about a credential describes what the account that ran the check can use, which may
    differ from what the account that delivers can.

    Attributes:
        level: `"error"`, `"warning"`, or `"note"`.
        about: `"option"` or `"credential"`.
        message: The finding in full sentences, naming the option or the credential's
            path, never the credential itself.
    """

    level: Literal["error", "warning", "note"]
    about: Literal["option", "credential"]
    message: str


@dataclass(frozen=True, kw_only=True)
class Sent:
    """The outcome of a part the platform accepted.

    Attributes:
        ref: The platform's reference to the sent message, such as its ID, which the
            later parts of the same mail receive in `DeliveryJob.refs`; `None` when the
            platform returns none.
    """

    ref: str | None = None


@dataclass(frozen=True, kw_only=True)
class RetryLater:
    """The outcome of a part that may succeed later, such as after a timeout.

    Attributes:
        reason: What went wrong, in one sentence that holds no credential.
        delay: Seconds the platform asked to wait before the next attempt, or `None`
            when it named none.
    """

    reason: str
    delay: float | None = None


@dataclass(frozen=True, kw_only=True)
class Failed:
    """The outcome of a part the platform refused for good.

    Attributes:
        reason: Why, in one sentence that holds no credential, such as the platform's
            own description.
    """

    reason: str


@dataclass(frozen=True, kw_only=True)
class Moved:
    """The outcome of a destination the platform moved: one option needs a new value.

    The plugin knows what the option means and ChatMTA does not, so the outcome names
    the option and its new value and nothing else.

    Attributes:
        option: The option the platform replaced, such as `chat`.
        value: Its new value.
    """

    option: str
    value: str | int


@dataclass(frozen=True, kw_only=True)
class CredentialUnavailable:
    """The outcome of a credential the account running the plugin cannot use.

    Another account may still use it: a sender may lack read access to a token file that
    the account that delivers can read.

    Attributes:
        reason: Which credential, and why, naming its path but never its content.
    """

    reason: str


Outcome: TypeAlias = Sent | RetryLater | Failed | Moved | CredentialUnavailable


class Plugin(Protocol):
    """What a plugin's entry point names: an API version and three methods.

    Any object with these members qualifies, without deriving from `Plugin`.
    """

    @property
    def api_version(self) -> int:
        """The `API_VERSION` the plugin is built for."""

    def validate(self, options: Mapping[str, object]) -> tuple[Finding, ...]:
        """Return a finding for each problem in a destination's options or credential.

        Validation opens no connection, so it gives the same answer with the
        network down.
        """

    def render(self, job: RenderJob) -> tuple[Part, ...]:
        """Return the parts that send the job's mail to its destination, in order."""

    def deliver(self, job: DeliveryJob) -> Outcome:
        """Send the job's part to its destination and return the outcome."""
