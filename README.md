# Octa Hub Infrastructure Documentation

**Last updated:** 2026-10-12  
**Project phase:** VPS initialization and baseline setup  
**Status:** VPS baseline setup completed; application installations not started.

## Documentation Index

1. `01-architecture-and-decisions.md` — architecture, services, domains, directory layout, and decisions.
2. `02-backup-and-restore.md` — backup policy, retention, encryption, and recovery.
3. `03-security-and-access.md` — SSH, ingress, networking, vault access, and administrative controls.
4. `04-installation-and-verification-runbook.md` — installation sequence and verification procedures.
5. `05-open-items-and-verification.md` — unresolved items and verification checklist.
6. `06-vps-initialization-record.md` — completed VPS initialization, OS maintenance, Docker installation, directory setup, and GitHub setup.

## Project Rules

- Follow the official documentation and official repository for each application.
- Check the latest stable/LTS release and compatibility requirements at implementation time.
- Use modular Docker Compose stacks.
- Treat this repository as infrastructure documentation and configuration source control, not as a place for credentials or persistent application data.
- Keep repository files in English.
- Keep real `.env` files, private keys, tokens, passwords, database dumps, backups, and persistent application data out of Git.
- Record actual verification results; distinguish completed, planned, and unverified work.
- Complete and verify one application in a dedicated session before starting the next application in a new session.

## Current Status

The VPS baseline work recorded in `06-vps-initialization-record.md` has been performed and verified based on terminal output supplied during the session. No application stack (9router, Hermes, n8n, Obsidian Web, or Octa Hub) has been installed in this phase.

The GitHub repository is:
https://github.com/OctaLectzz/octa-hub-infrastructure

Repository visibility was intentionally left **Public** by user decision on 2026-10-12. Review every staged change for sensitive information before pushing.

## Source of Truth

These documents are a record of decisions and reported verification. When a document differs from actual VPS output, verify the live system and update the record rather than assuming the document is correct.
