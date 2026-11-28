# Compatibility

What operators can rely on across releases.

## Versioning

Releases follow Semantic Versioning. Before 1.0.0, a minor release may break a
covered surface, and its changelog entry says so with **Breaking:**; a patch
release never breaks. From 1.0.0, only a major release breaks, after a minor
release has deprecated what it removes: the old form keeps working and warns,
naming its replacement and the release that removes it. A security fix may break
a surface in a patch release, and its changelog entry names the old and the
new behavior.

## What Is Covered

- Every name in `chatmta.__all__`, with its parameters and return values.
- The behavior these pages describe.

## What Is Not Covered

- Names that start with `_`, and behavior these pages do not describe.
- Development releases (`.devN`) and release candidates (`rcN`).

## Plugin API

The plugin API, every name in `chatmta.__all__`, stays provisional until a
release declares it stable, after a second plugin is built on it unchanged.
Until then, any minor release may change it, even after 1.0.0, and the release's
changelog entry names what a plugin must change.

`PLUGIN_API_VERSION` rises with a release that could make a plugin built for the
previous version fail: one that removes, renames, or changes the type or the
meaning of a name, a field, or a method. A release that only adds a name, a
field with a default, or an outcome keeps it.

## Python Versions

ChatMTA supports Python 3.11 to 3.15. A minor release may drop a Python version
after its end of life, and its changelog entry names it.
