import dataclasses
import inspect
from collections.abc import Mapping
from datetime import UTC, datetime

import pytest

from chatmta.model import api
from chatmta.model.api import (
    API_VERSION,
    Attachment,
    Body,
    Choices,
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

_RECEIVED = datetime(2026, 11, 20, 6, 25, tzinfo=UTC)


class _Contents:
    def __init__(self, sections: Mapping[str, bytes]) -> None:
        self._sections = dict(sections)

    def data(self, section: str) -> bytes | None:
        return self._sections.get(section)

    def text(self, section: str) -> str | None:
        data = self._sections.get(section)
        return None if data is None else data.decode()


class _FilePlugin:
    api_version = API_VERSION

    def validate(self, options: Mapping[str, object]) -> tuple[Finding, ...]:
        return ()

    def render(self, job: RenderJob) -> tuple[Part, ...]:
        return tuple(
            Part(
                format="file",
                fields={"name": attachment.name or "attachment"},
                sections=(attachment.section,),
            )
            for attachment in job.mail.attachments
        )

    def deliver(self, job: DeliveryJob) -> Outcome:
        data = job.contents.data(job.part.sections[0])
        if data is None:
            return Failed(reason="The mail no longer holds the file.")
        return Sent(ref=f"{job.part.fields['name']}:{len(data)}")


def _attachment() -> Attachment:
    return Attachment(section="2", name="df.txt", content_type="text/plain", size=10)


def _mail(*, attachments: tuple[Attachment, ...] = ()) -> Mail:
    return Mail(
        outbox_id="3f9c2a7b1d8e4f6a0c5b",
        envelope_sender="root",
        envelope_recipients=("root",),
        sender="Cron Daemon <root@backup01>",
        subject="Cron <root@backup01> /usr/local/bin/backup",
        body=Body(section="1", subtype="plain", text="Disk full\n"),
        attachments=attachments,
        host="backup01",
        received=_RECEIVED,
    )


def _every_value() -> list[object]:
    destination = Destination(name="ops", options={"chat": -100123})
    part = Part(format="message", text="Disk full")
    contents = _Contents({})
    return [
        _attachment(),
        Body(section="1", subtype="plain", text="Disk full\n"),
        Choices(),
        CredentialUnavailable(reason="The token file cannot be read."),
        DeliveryJob(
            part=part,
            destination=destination,
            refs=(),
            now=_RECEIVED,
            time_left=10.0,
            contents=contents,
        ),
        destination,
        Failed(reason="Bad Request: chat not found"),
        Finding(
            level="note", about="credential", message="The token is not checkable."
        ),
        _mail(),
        Moved(option="chat", value=-100999),
        part,
        RenderJob(
            mail=_mail(), destination=destination, choices=Choices(), contents=contents
        ),
        RetryLater(reason="The server returned 502."),
        Sent(ref="42"),
    ]


def test_mappings_ignore_later_changes_to_the_dicts_passed_in() -> None:
    options: dict[str, object] = {"chat": -100123}
    fields = {"entities": "[]"}
    destination = Destination(name="ops", options=options)
    part = Part(format="message", fields=fields)

    options["chat"] = -100999
    fields["entities"] = '[{"type": "bold"}]'

    assert destination.options == {"chat": -100123}
    assert part.fields == {"entities": "[]"}


def test_mappings_refuse_item_assignment() -> None:
    destination = Destination(name="ops", options={"chat": -100123})
    part = Part(format="message", fields={"entities": "[]"})

    with pytest.raises(TypeError):
        destination.options["chat"] = 0  # type: ignore[index]  # read-only mapping
    with pytest.raises(TypeError):
        part.fields["entities"] = ""  # type: ignore[index]  # read-only mapping


@pytest.mark.parametrize(
    "value", _every_value(), ids=lambda value: type(value).__name__
)
def test_takes_keyword_arguments_only(value: object) -> None:
    parameters = inspect.signature(type(value)).parameters.values()
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters
    )


@pytest.mark.parametrize(
    "value", _every_value(), ids=lambda value: type(value).__name__
)
def test_refuses_attribute_assignment(value: object) -> None:
    first = next(iter(inspect.signature(type(value)).parameters))
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(value, first, None)


def test_the_type_checks_reach_every_dataclass_of_the_api() -> None:
    every_dataclass = {
        value
        for value in vars(api).values()
        if isinstance(value, type) and dataclasses.is_dataclass(value)
    }
    assert {type(value) for value in _every_value()} == every_dataclass


def test_choices_leave_silence_off_and_the_style_unset() -> None:
    choices = Choices()
    assert choices.silent is False
    assert choices.style is None


def test_optional_fields_start_empty() -> None:
    part = Part(format="message")
    assert (part.text, dict(part.fields), part.sections) == ("", {}, ())
    assert Sent().ref is None
    assert RetryLater(reason="The server returned 502.").delay is None
    assert _attachment().content_id is None
    assert _mail().bytes_cut == 0


def test_a_plugin_reads_a_file_back_by_section_when_it_delivers() -> None:
    plugin: Plugin = _FilePlugin()
    destination = Destination(name="ops", options={"chat": -100123})
    contents = _Contents({"2": b"Disk full\n"})
    job = RenderJob(
        mail=_mail(attachments=(_attachment(),)),
        destination=destination,
        choices=Choices(),
        contents=contents,
    )

    (part,) = plugin.render(job)
    outcome = plugin.deliver(
        DeliveryJob(
            part=part,
            destination=destination,
            refs=(),
            now=_RECEIVED,
            time_left=10.0,
            contents=contents,
        )
    )

    assert plugin.api_version == API_VERSION
    assert plugin.validate(destination.options) == ()
    assert outcome == Sent(ref="df.txt:10")
