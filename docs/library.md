# Library

Every name in `chatmta.__all__`, with its parameters, return value, and
exceptions. Each class but `Contents` and `Plugin` is a frozen dataclass whose
fields are keyword-only.

## `Attachment`

A part of a mail that a plugin may send as a file.

- `section` — the part's MIME section path, such as `2` or `1.2`.
- `name` — the file name the mail gives the part, or `None` when it gives none.
- `content_type` — the part's MIME type, such as `image/png`.
- `size` — the part's size in bytes once its transfer encoding is undone.
- `content_id` — the part's `Content-ID` without its angle brackets, or `None`
  when it has none.

## `Body`

The part of a mail that a plugin shows as its text.

- `section` — the part's MIME section path, such as `1` or `1.1`.
- `text` — the body as plain text, also for a mail whose body is HTML alone.
- `html` — the source of the HTML part, or `None` when the mail has none.

## `ChatMessage`

One chat message that `Plugin.render` returns for `Plugin.deliver` to send.

- `kind` — the plugin's label for the message's layout.
- `text` — the message's text; default `""`.
- `fields` — the other strings the plugin needs to send the message, a read-only
  copy of the mapping passed in.
- `sections` — the section paths of the mail's parts the message sends.

## `Contents`

The decoded parts of one mail, read only when a plugin needs them.

```python
data(section: str) -> bytes | None
text(section: str) -> str | None
```

`data` returns the bytes of `section` with its transfer encoding undone, and
`text` returns its text, decoded with its charset. Each returns `None` when the
mail has no such section.

## `CredentialUnavailable`

The outcome when the running account may not read the credential it needs.

- `reason` — why, naming the credential's path, never its content.

## `DeliveryJob`

What `Plugin.deliver` sends.

- `chat_message` — the chat message to send.
- `destination` — the destination to send to.
- `refs` — the `Sent.ref` of each earlier chat message of the same mail and
  destination, in order.
- `now` — the time of the attempt, an aware UTC `datetime`.
- `time_left` — the seconds the plugin has left for the attempt.
- `contents` — the mail's decoded parts.

## `Destination`

A destination the configuration names, as its plugin receives it.

- `name` — the destination's name in the configuration.
- `options` — the destination's keys other than `type`, for the plugin to
  narrow, a read-only copy of the mapping passed in.

## `Failed`

The outcome of a chat message that no later attempt would deliver.

- `reason` — why, such as the platform's own description.

## `Finding`

A problem or a remark that `Plugin.validate` reports about a destination.

- `level` — how much it matters: `"error"`, `"warning"`, or `"note"`.
- `about` — what it concerns: `"option"` or `"credential"`.
- `message` — full sentences naming the option or the credential's path, never
  the credential.

## `Mail`

A mail as a plugin renders it, without the bytes of its parts.

- `outbox_id` — the mail's identifier in the outbox.
- `envelope_sender` — the envelope sender, as submitted.
- `envelope_recipients` — the envelope recipients that no header of the
  mail names.
- `sender` — the sender the mail's headers name.
- `subject` — the subject, empty when the mail has none.
- `body` — the body, a `Body`, or `None` when the mail has none.
- `attachments` — the attachments, each an `Attachment`, in the mail's order.
- `host` — the host the mail was submitted on.
- `received` — when ChatMTA received the mail, an aware UTC `datetime`.
- `bytes_cut` — the bytes cut from the end of a mail past the size limit;
  default `0`.

## `Moved`

The outcome when the platform reports the conversation under a new value. A
plugin returns it only when the conversation stays the same and only its address
changed, such as a group that became a supergroup.

- `option` — the option whose value moved, such as `chat`.
- `value` — the option's new value, a `str` or an `int`.

## `Outcome`

What `Plugin.deliver` returns: one of the five outcomes.

```python
Outcome = Sent | RetryLater | Failed | Moved | CredentialUnavailable
```

## `Plugin`

The protocol a platform plugin's class meets, without deriving from it.

```python
api_version: ClassVar[int]
validate(job: ValidationJob) -> tuple[Finding, ...]
render(job: RenderJob) -> tuple[ChatMessage, ...]
deliver(job: DeliveryJob) -> Outcome
```

- `api_version` — the `PLUGIN_API_VERSION` the plugin is built for.

`validate` returns the findings about `job.destination` and opens no connection.
`render` returns the chat messages for `job.mail`, in the order they are sent.
`deliver` sends `job.chat_message` and returns what became of it.

## `RenderJob`

What `Plugin.render` turns into chat messages.

- `mail` — the mail to render.
- `destination` — the destination the mail goes to.
- `contents` — the mail's decoded parts.
- `silent` — whether the rule asks for delivery without a notification;
  default `False`.
- `style` — the body style the rule names, `"plain"`, `"quote"`, or `"code"`, or
  `None` when it names none, so the plugin's own default applies.

## `RetryLater`

The outcome of a chat message that a later attempt may deliver.

- `reason` — one sentence on why, which holds no credential.
- `delay` — the seconds the platform asks to wait, or `None` when it names none.

## `Sent`

The outcome of a chat message the platform accepted.

- `ref` — the platform's reference to the message, or `None` when it
  returns none.

## `ValidationJob`

What `Plugin.validate` checks.

- `destination` — the destination to check.

## Constants

- `PLUGIN_API_VERSION` — the version of the plugin API, `1`; how it
  changes: [Compatibility](compatibility.md).
