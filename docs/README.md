# Octa Hub Documentation Index

This directory contains documentation for Octa Hub infrastructure, including architecture, installation, security, operations, and service recovery on the VPS.

## Architecture and Infrastructure

- [Architecture and Decisions](01-architecture-and-decisions.md) — Infrastructure architecture and design decisions.
- [Backup and Restore](02-backup-and-restore.md) — Backup and recovery policies.
- [Security and Access](03-security-and-access.md) — Security controls and access policies.
- [Installation and Verification Runbook](04-installation-and-verification-runbook.md) — Installation and verification procedures.
- [Open Items and Verification](05-open-items-and-verification.md) — Outstanding tasks and verification requirements.
- [VPS Initialization Record](06-vps-initialization-record.md) — VPS initialization history.
- [9Router Installation Record](07-router-installation-record.md) — 9Router installation and deployment record.
- [9Router Security and Open Items](08-router-security-and-open-items.md) — 9Router security findings and outstanding tasks.
- [Next Session Handoff](09-next-session-handoff.md) — Project status and instructions for continuing the work.

## Hermes Agent

- [Hermes Deployment](10-hermes-deployment.md) — Deployment configuration and verification results.
- [Hermes Security Review](11-hermes-security.md) — Authentication, API access, networking, terminal backend, and security findings.
- [Hermes Operations and Troubleshooting](12-hermes-operations.md) — Operational commands and troubleshooting procedures.
- [Hermes Obsidian Memory Plugin](14-hermes-obsidian-memory.md) — Runtime vault configuration, automatic refresh, graph labels, verification, and maintenance notes.

## n8n and Integrations

- [n8n Deployment and Hermes Integration](13-n8n-deployment-and-hermes-integration.md) — Deployment facts, test workflows, REST plugin, MCP status, and remaining checks.

## Project Principles

- Follow the official documentation and repository of each application.
- Verify versions and configuration before making changes.
- Never commit credentials, real `.env` files, or runtime data to Git.
- Mark work as complete only after verification.
- Clearly separate deployment, documentation, and security review activities.

## Documentation Rules

- All repository documentation must be written in English.
- Clearly distinguish planned work from verified work.
- Follow official application documentation and repositories.
- Update relevant documentation when deployment decisions or live configuration change.
- Review public disclosure risks before committing because this repository is public.
- Never commit real `.env` files, passwords, API tokens, encryption keys, private keys, or other secrets.
