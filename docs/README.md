# Octa Hub Documentation

This directory contains the architecture decisions, security policy, backup/restore plan, operational runbooks, verification checklist, and VPS initialization record for Octa Hub.

## Documents

1. [`01-architecture-and-decisions.md`](01-architecture-and-decisions.md) — architecture, services, domains, directory layout, and implementation decisions.
2. [`02-backup-and-restore.md`](02-backup-and-restore.md) — backup destinations, encryption, retention, validation, and restore testing.
3. [`03-security-and-access.md`](03-security-and-access.md) — SSH, firewall/ingress, vault deletion approvals, Octa Hub permissions, and secret handling.
4. [`04-installation-and-verification-runbook.md`](04-installation-and-verification-runbook.md) — baseline setup and future installation/verification workflow.
5. [`05-open-items-and-verification.md`](05-open-items-and-verification.md) — completed baseline items, unresolved checks, and future work.
6. [`06-vps-initialization-record.md`](06-vps-initialization-record.md) — recorded OS updates, Docker installation, directory setup, and GitHub setup.
7. [`07-router-installation-record.md`](07-router-installation-record.md) — verified 9Router deployment details and test results.
8. [`08-router-security-and-open-items.md`](08-router-security-and-open-items.md) — 9Router security review and unresolved checks.
9. [`09-next-session-handoff.md`](09-next-session-handoff.md) — handoff notes and rules for the next Project session.

## Documentation Rules

- Repository files must be written in English.
- Distinguish planned work from work verified on the VPS.
- Follow official application documentation and repositories.
- Update relevant documents when decisions or live configuration change.
- Review public-disclosure risks before committing because the GitHub repository is currently Public.
- Never include real `.env` contents, passwords, API tokens, encryption keys, private keys, or other secrets.
