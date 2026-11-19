# Security Policy

## Supported Versions

Only the latest released version of ChatMTA receives security fixes. Older
releases are not patched.

## Reporting a Vulnerability

Report vulnerabilities privately; never open a public issue for one.

- **GitHub private vulnerability reporting** (preferred): open a draft advisory
  on the [security advisories page](https://github.com/theodiv/chatmta/security/advisories/new).
- **Email**: `theodiv@gmail.com`.

## Disclosure Process

1. The maintainer acknowledges the report within **72 hours**.
2. The maintainer confirms or declines the report and assesses its severity
   within **7 days** of receiving it.
3. The fix is developed and tested in the advisory's temporary private fork.
4. Disclosure is coordinated with the reporter, targeting **30 days** from
   confirmation; complex issues may take longer.
5. The patched release and the advisory are published together.
6. The advisory credits the reporter unless anonymity is requested.

## Out of Scope

- The operator's own files and code: the configuration, the mail the host's
  programs hand to ChatMTA, and the chats that mail reaches.
