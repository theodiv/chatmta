import dataclasses
from datetime import UTC, datetime
from typing import ClassVar

import pytest

from chatmta.model.plugin_api import (
    PLUGIN_API_VERSION,
    Attachment,
    Body,
    ChatMessage,
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

_RECEIVED = datetime(2026, 11, 28, 6, 25, tzinfo=UTC)


class _NoContents:
    def data(self, section: str) -> bytes | None:
        return None

    def text(self, section: str) -> str | None:
        return None


class _Echo:
    api_version: ClassVar[int] = 1

    def validate(self, job: ValidationJob) -> tuple[Finding, ...]:
        return (Finding(level="note", about="option", message=job.destination.name),)

    def render(self, job: RenderJob) -> tuple[ChatMessage, ...]:
        text = job.mail.subject
        return (ChatMessage(kind="text", text=text, fields={}, sections=()),)

    def deliver(self, job: DeliveryJob) -> Outcome:
        return Sent(ref=job.chat_message.text)


def _destination() -> Destination:
    return Destination(name="ops", options={"chat": "-100"})


def _mail() -> Mail:
    return Mail(
        outbox_id="a1",
        envelope_sender="root@host",
        envelope_recipients=(),
        sender="root@host",
        subject="Cron <root@host> backup",
        body=Body(section="1", text="done\n", html=None),
        attachments=(
            Attachment(
                section="2",
                name="log.txt",
                content_type="text/plain",
                size=4,
                content_id=None,
            ),
        ),
        host="host",
        received=_RECEIVED,
    )


def _chat_message() -> ChatMessage:
    return ChatMessage(kind="text", fields={"parse_mode": "none"}, sections=("2",))


def _values() -> tuple[object, ...]:
    return (
        _destination(),
        _mail(),
        ValidationJob(destination=_destination()),
        RenderJob(
            mail=_mail(), destination=_destination(), contents=_NoContents(), style=None
        ),
        DeliveryJob(
            chat_message=_chat_message(),
            destination=_destination(),
            refs=("7", None),
            now=_RECEIVED,
            time_left=30.0,
            contents=_NoContents(),
        ),
        Finding(level="error", about="option", message="The `chat` option is empty."),
        _chat_message(),
        Sent(ref=None),
        RetryLater(reason="The platform is busy.", delay=None),
        Failed(reason="Bad Request: chat not found"),
        Moved(option="chat", value=-100),
        CredentialUnavailable(reason="/etc/chatmta/ops.token is not readable."),
    )


@pytest.mark.parametrize("value", _values(), ids=lambda value: type(value).__name__)
def test_value_refuses_positional_fields(value: object) -> None:
    fields = dataclasses.fields(value)  # type: ignore[arg-type]  # a dataclass
    with pytest.raises(TypeError):
        type(value)(*(getattr(value, each.name) for each in fields))


@pytest.mark.parametrize("value", _values(), ids=lambda value: type(value).__name__)
def test_value_refuses_assignment(value: object) -> None:
    name = dataclasses.fields(value)[0].name  # type: ignore[arg-type]  # a dataclass
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(value, name, None)


@pytest.mark.parametrize("value", _values(), ids=lambda value: type(value).__name__)
def test_value_hashes_as_its_equal_copy_does(value: object) -> None:
    copy = dataclasses.replace(value)  # type: ignore[type-var]  # a dataclass
    assert copy == value
    assert hash(copy) == hash(value)


def test_destination_options_are_a_read_only_copy() -> None:
    options: dict[str, object] = {"chat": "-100"}
    destination = Destination(name="ops", options=options)
    options["chat"] = "-200"

    assert destination.options == {"chat": "-100"}
    with pytest.raises(TypeError):
        destination.options["chat"] = "-200"  # type: ignore[index]  # read-only


def test_chat_message_fields_are_a_read_only_copy() -> None:
    fields = {"parse_mode": "none"}
    message = ChatMessage(kind="text", fields=fields, sections=())
    fields["parse_mode"] = "html"

    assert message.fields == {"parse_mode": "none"}
    with pytest.raises(TypeError):
        message.fields["parse_mode"] = "html"  # type: ignore[index]  # read-only


def test_defaults_are_those_documented() -> None:
    render = RenderJob(
        mail=_mail(), destination=_destination(), contents=_NoContents(), style=None
    )

    assert _mail().bytes_cut == 0
    assert render.silent is False
    assert _chat_message().text == ""


def test_plugin_api_version_is_one() -> None:
    assert PLUGIN_API_VERSION == 1


def test_class_that_does_not_derive_from_plugin_meets_it() -> None:
    # The Types gate checks this assignment; the calls show the protocol's shape.
    plugin: Plugin = _Echo()
    validation = ValidationJob(destination=_destination())
    render = RenderJob(
        mail=_mail(), destination=_destination(), contents=_NoContents(), style=None
    )
    delivery = DeliveryJob(
        chat_message=ChatMessage(kind="text", text="hi", fields={}, sections=()),
        destination=_destination(),
        refs=(),
        now=_RECEIVED,
        time_left=1.0,
        contents=_NoContents(),
    )

    assert plugin.api_version == PLUGIN_API_VERSION
    assert plugin.validate(validation)[0].message == "ops"
    assert plugin.render(render)[0].text == "Cron <root@host> backup"
    assert plugin.deliver(delivery) == Sent(ref="hi")
