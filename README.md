# Octa Hub Infrastructure

Infrastructure repository for the Octa Hub self-hosted environment. This repository documents the architecture, configuration conventions, operational runbooks, security controls, and recovery procedures for services deployed on a Dahono Cloud VPS.

> **Current phase:** VPS baseline completed. 9Router and Hermes Agent are deployed. The 9Router ingress security review and Hermes security closeout remain pending. n8n, Obsidian Web, and the Octa Hub dashboard remain planned.

## Architecture Overview

### Public Services

| Service | Repository directory | Public URL | Status |
|---|---|---|---|
| 9router | `stacks/router/` | https://router.octalectzz.my.id | Deployed; basic health verified; security review pending |
| Hermes Agent and dashboard | `stacks/hermes/` | https://hermes.octalectzz.my.id | Deployed; OAuth and Basic Auth login verified; API security review pending |
| n8n | `stacks/n8n/` | https://n8n.octalectzz.my.id | Planned |
| Obsidian Web | `stacks/obsidian/` | https://obsidian.octalectzz.my.id | Planned |
| Octa Hub dashboard | `stacks/octa-hub/` | https://hub.octalectzz.my.id | Planned |

Potential supporting components include internal SearXNG, an n8n sandbox/runner, and a database service if required by the official deployment guidance. These are not considered installed or finalized until their requirements are verified.

### VPS Baseline

- Provider: Dahono Cloud VPS (NAT)
- Hostname: `octa-hub`
- Operating system: Ubuntu 24.04.5 LTS (Noble)
- Virtualization: LXC
- Architecture: `amd64`
- Resources: 4 vCPU, 8 GiB RAM, 2 GiB swap, approximately 49–50 GB disk
- Container IP: `<VPS_CONTAINER_IP>`
- Docker Engine and Docker Compose plugin: installed and verified
- GitHub remote: `git@github.com:OctaLectzz/octa-hub-infrastructure.git`
- Default branch: `main`

The repository is currently Public by user decision. Treat all committed content as publicly visible. Do not commit secrets or details that should not be disclosed.

## Repository Architecture

```text
.
├── README.md                         # Repository overview and architecture
├── .gitignore                        # Excludes local secrets and generated data
├── stacks/                           # Per-service Docker Compose configuration
│   ├── router/
│   │   ├── compose.yaml              # Existing deployment configuration
│   │   ├── .env                      # Local only; never commit
│   │   └── .env.example              # Safe template; commit when documented
│   ├── hermes/
│   │   ├── compose.yaml
│   │   ├── .env
│   │   └── .env.example
│   ├── n8n/
│   │   ├── compose.yaml
│   │   ├── .env
│   │   └── .env.example
│   ├── obsidian/
│   │   ├── compose.yaml
│   │   ├── .env
│   │   └── .env.example
│   └── octa-hub/
│       ├── compose.yaml
│       ├── .env
│       └── .env.example
└── docs/                             # Project documentation
    ├── README.md                     # Documentation index
    ├── 01-architecture-and-decisions.md
    ├── 02-backup-and-restore.md
    ├── 03-security-and-access.md
    ├── 04-installation-and-verification-runbook.md
    ├── 05-open-items-and-verification.md
    └── 06-vps-initialization-record.md
    ├── 07-router-installation-record.md
    ├── 08-router-security-and-open-items.md
    ├── 09-next-session-handoff.md
    ├── 10-hermes-deployment.md
    ├── 11-hermes-security.md
    └── 12-hermes-operations.md
```

The tree shows the repository structure and planned locations for service configuration files. Compose files currently exist for 9Router and Hermes Agent; Compose files for other planned services may not exist yet. Actual `.env` files and persistent application data remain on the VPS and must never be committed to Git. Runtime data is kept under `/opt/octa/data/`, outside the repository. Local backup artifacts and operational logs are also excluded from version control.

## Directory Responsibilities

- `stacks/<service>/`: Docker Compose files and service-specific environment templates.
- `data/<service>/` on the VPS: persistent application data and mounted volumes.
- `docs/`: architecture decisions, security policy, backup/restore procedures, runbooks, and session handoffs.
- `.env`: real configuration and credentials, local to the VPS and never committed.
- `.env.example`: documented variable names with safe placeholders, suitable for Git after review.
- `.gitignore`: excludes secrets, persistent data, backups, logs, and temporary artifacts.

## Operating Principles

1. Follow each application's official documentation and official repository.
2. Verify current stable/LTS versions and compatibility at installation time.
3. Deploy one application at a time with modular Docker Compose.
4. Verify container health, logs, persistence, authentication, network exposure, and domain routing before marking an installation complete.
5. Do not expose internal dependencies such as SearXNG or sandbox/runner APIs directly to the internet without an explicitly reviewed requirement.
6. Do not give Octa Hub direct Docker socket or root access just for monitoring.
7. Hermes and n8n may read and write the Obsidian vault, but every deletion must require explicit authenticated approval from the system owner or designated administrator, with audit logging and no bypass path.
8. Keep real secrets out of Git and logs. Review every staged change before committing.
9. Configure the first automated backup only after all application installations are complete, as agreed. Backups are intended for Cloudflare R2 and Dahono S3, encrypted client-side, daily at 05:00 WIB, with at most three valid generations per destination and restore tests in staging.
10. Each application installation is handled in its own session. After successful verification, update the documentation, commit and push, then start a new session for the next application.

## Documentation

Start at [`docs/README.md`](docs/README.md) for the documentation index.

- [Architecture and Decisions](docs/01-architecture-and-decisions.md)
- [Backup and Restore](docs/02-backup-and-restore.md)
- [Security and Access](docs/03-security-and-access.md)
- [Installation and Verification Runbook](docs/04-installation-and-verification-runbook.md)
- [Open Items and Verification](docs/05-open-items-and-verification.md)
- [VPS Initialization Record](docs/06-vps-initialization-record.md)
- [9Router Installation Record](docs/07-router-installation-record.md)
- [9Router Security and Open Items](docs/08-router-security-and-open-items.md)
- [Next Session Handoff](docs/09-next-session-handoff.md)
- [Hermes Deployment](docs/10-hermes-deployment.md)
- [Hermes Security Review](docs/11-hermes-security.md)
- [Hermes Operations and Troubleshooting](docs/12-hermes-operations.md)

## Git Safety

Review changes before committing:

```bash
git status
git diff
git diff --cached
```

Never commit `.env`, private keys, access tokens, passwords, database dumps, backups, or persistent application data. `.gitignore` is a guardrail, not a substitute for reviewing staged content.
