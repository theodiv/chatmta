# Library

Every name in `chatmta.__all__`, with its parameters, return value, and
exceptions. Every class but `Contents` and `Plugin` is a frozen dataclass that
takes keyword arguments only.

## `Attachment`

A file a mail carries, an inline image included, described without its bytes,
which `Contents.data` reads by `section`.

- `section` — the MIME section path of the file, such as `2`.
- `name` — the file name the mail gives, or `None` when it gives none.
- `content_type` — the MIME type, such as `image/png`.
- `size` — the decoded size in bytes.
- `content_id` — the `Content-ID` that HTML in the mail refers to, without its
  angle brackets, or `None`; default `None`.

## `Body`

The part of a mail chosen as the text to show.

- `section` — the MIME section path of the part, such as `1` or `1.1`.
- `subtype` — `"plain"` for text to show as written, `"html"` for HTML source.
- `text` — the decoded text.

## `Choices`

What the rule that chose a destination asks of the delivery.

- `silent` — whether the destination's readers get no notification of the mail;
  default `False`.
- `style` — how to set off the body, `"plain"`, `"quote"`, or `"code"`, each in
  the plugin's own way, or `None` when the rule names no style, so a plugin can
  tell its own default from an explicit `"plain"`; default `None`.

## `Contents`

What each job hands a plugin to read a mail's decoded body and files back by
MIME section path, so a part can name one and leave its text and bytes in the
mail as received.

```python
data(section: str) -> bytes | None
text(section: str) -> str | None
```

- `data` — returns the bytes of `section`, its transfer encoding undone, or
  `None` for a section the mail lacks.
- `text` — returns the text of `section`, decoded with the charset it declares,
  or `None` for a section the mail lacks or one that holds no text.

## `CredentialUnavailable`

The outcome of a credential the account running the plugin cannot use, though
another account may: a sender may lack read access to a token file that the
account that delivers can read.

- `reason` — which credential, and why, naming its path but never its content.

## `DeliveryJob`

One part for one destination, which `Plugin.deliver` sends.

- `part` — the part, as `Plugin.render` returned it.
- `destination` — the destination, its options holding the value of a kept
  `Moved` outcome in place of the option that outcome names.
- `refs` — the `Sent.ref` of each earlier part of the same mail and destination,
  in order.
- `now` — the current time, an aware `datetime` in UTC.
- `time_left` — seconds until the attempt is stopped; a plugin keeps its
  timeouts within them, so it gives up first.
- `contents` — the mail's body and files, read back by section path.

## `Destination`

A destination as the plugin that delivers it sees it.

- `name` — the destination's name in the configuration.
- `options` — the destination's keys other than `type`, as a read-only copy,
  each value typed `object` for the plugin to narrow.

## `Failed`

The outcome of a part the platform refused for good.

- `reason` — why, in one sentence that holds no credential, such as the
  platform's own description.

## `Finding`

One problem or remark that `Plugin.validate` reports about a destination.

- `level` — `"error"`, `"warning"`, or `"note"`.
- `about` — `"option"` or `"credential"`: an error about an option means the
  destination cannot work as configured, while a finding about a credential
  describes what the account that ran the check can use, which may differ from
  what the account that delivers can.
- `message` — the finding in full sentences, naming the option or the
  credential's path, never the credential itself.

## `Mail`

One mail, decoded, as a plugin renders it.

- `outbox_id` — the ID the outbox gave the mail.
- `envelope_sender` — the envelope sender.
- `envelope_recipients` — every envelope recipient, including those no header
  names (`Bcc:`).
- `sender` — the sender to show, from the `From:` header or, when the mail has
  none, the name `-F` gave.
- `subject` — the decoded subject, or an empty string when the mail has none.
- `body` — the text to show, a `Body`, or `None` when the mail has none.
- `attachments` — the files the mail carries, each an `Attachment`, in their
  order in the mail.
- `host` — the name of the host the mail comes from.
- `received` — when the outbox received the mail, an aware `datetime` in UTC.
- `bytes_cut` — how many bytes of the mail the outbox left out past its size
  limit; default `0`.

## `Moved`

The outcome of a destination the platform moved: one option needs a new value.

- `option` — the option the platform replaced, such as `chat`.
- `value` — its new value, a `str` or an `int`.

## `Outcome`

What `Plugin.deliver` returns: a `Sent`, `RetryLater`, `Failed`, `Moved`,
or `CredentialUnavailable`.

## `Part`

One piece of a rendered mail, as plain data: strings alone, which name the body
or a file by section path instead of copying its text or bytes.

- `format` — the plugin's own label for the part's layout; a plugin reads every
  format its earlier releases wrote under the same `API_VERSION`, and fails a
  part whose format it does not know, naming it.
- `text` — the part's text, as the plugin rendered it; default `""`.
- `fields` — other string values the plugin needs at delivery, as a read-only
  copy; default empty.
- `sections` — the MIME section paths of the body or the files the part sends;
  default empty.

## `Plugin`

What a plugin's entry point names: an API version and three methods, on any
object that has them, without deriving from `Plugin`.

```python
api_version: int
validate(options: Mapping[str, object]) -> tuple[Finding, ...]
render(job: RenderJob) -> tuple[Part, ...]
deliver(job: DeliveryJob) -> Outcome
```

- `api_version` — the `API_VERSION` the plugin is built for, read-only.
- `validate` — returns a `Finding` for each problem in a destination's options
  or credential; it opens no connection, so it gives the same answer with the
  network down.
- `render` — returns the parts that send the job's mail to its destination,
  in order.
- `deliver` — sends the job's part to its destination and returns the outcome.

## `RenderJob`

One mail for one destination, which `Plugin.render` turns into parts.

- `mail` — the mail.
- `destination` — the destination the parts go to.
- `choices` — what the rule that chose the destination asks of the delivery.
- `contents` — the mail's body and files, read back by section path.

## `RetryLater`

The outcome of a part that may succeed later, such as after a timeout.

- `reason` — what went wrong, in one sentence that holds no credential.
- `delay` — seconds the platform asked to wait before the next attempt, or
  `None` when it named none; default `None`.

## `Sent`

The outcome of a part the platform accepted.

- `ref` — the platform's reference to the sent message, such as its ID, which
  the later parts of the same mail receive in `DeliveryJob.refs`, or `None` when
  the platform returns none; default `None`.

## Constants

- `API_VERSION` — the version of the plugin API this release implements, `1`;
  [Compatibility](compatibility.md#plugin-api) says when it rises.
