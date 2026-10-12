# 01 — Architecture and Infrastructure Decisions

**Status:** Architecture agreed; application deployments not yet implemented  
**Last updated:** 2026-10-12

## 1. Goal

Rebuild the Octa Hub services from scratch on Dahono VPS without restoring the previous installation. Deploy manually with Docker Compose and follow each project's official documentation and repository.

## 2. Verified VPS Baseline

- Provider: Dahono Cloud VPS (NAT).
- Hostname: `octa-hub`.
- OS: Ubuntu 24.04.5 LTS (Noble).
- Architecture: `amd64` / `x86_64`.
- Virtualization: LXC.
- CPU: 4 vCPU.
- RAM: 8 GiB.
- Swap: 2 GiB.
- Disk: approximately 49–50 GB.
- Container IP: `10.10.0.238`.
- Gateway: `10.10.0.1`.
- SSH public endpoint: `143.20.199.50:33822`, forwarded to internal port 22.
- Docker Engine and Compose are installed; see `06-vps-initialization-record.md` for observed versions and verification.

Do not expose private credentials in documentation. Network and provider behavior must be rechecked before changing ingress, firewall, or SSH settings.

## 3. Services and Domains

- 9router — `https://router.octalectzz.my.id`
- Hermes Agent and dashboard — `https://hermes.octalectzz.my.id`
- n8n — `https://n8n.octalectzz.my.id`
- Obsidian Web — `https://obsidian.octalectzz.my.id`
- Octa Hub — `https://hub.octalectzz.my.id`
- SearXNG — planned internal service for Hermes and n8n; do not expose directly unless a reviewed requirement explicitly changes this.
- n8n Assistant sandbox — planned; use the official template and compatible versions if required.

Dahono Web Ingress & Domains is the intended routing and HTTPS option, subject to verification of supported upstream targets, ports, TLS behavior, and restart behavior.

## 4. Directory Layout

Created on the VPS:

```text
/opt/octa/
├── .git/
├── .gitignore
├── README.md
├── stacks/
│   ├── router/
│   │   ├── .env.example
│   │   └── (compose.yaml to be added after official documentation review)
│   ├── hermes/
│   │   └── .env.example
│   ├── n8n/
│   │   └── .env.example
│   ├── obsidian/
│   │   └── .env.example
│   └── octa-hub/
│       └── .env.example
├── data/
│   ├── router/
│   ├── hermes/
│   ├── n8n/
│   ├── obsidian/
│   └── octa-hub/
├── backups/
├── logs/
└── docs/
    ├── architecture/
    ├── runbooks/
    └── changelog/
```

The base directories and empty `.env.example` files were created. Service Compose files and actual service `.env` files have not been created. Additional directories such as SearXNG, PostgreSQL, n8n sandbox, or backup stack should be added only when confirmed by the official setup requirements and final architecture.

## 5. Architecture Principles

- Keep deployment configuration separate from persistent data.
- Use internal Docker networks for service-to-service communication where appropriate.
- Do not expose internal SearXNG, sandbox APIs, or runners directly to the internet.
- Do not give Octa Hub direct Docker socket access or root privileges just for monitoring.
- Apply least privilege to users, volumes, networks, and credentials.
- Provide HTTPS through the verified ingress mechanism.
- Filesystem read/write access to the Obsidian vault must not permit unapproved deletion.
- Use version combinations supported by official templates; do not independently pin every component to `latest` when compatibility is constrained.

## 6. Application Version Policy

Check the current stable/latest or LTS version and the project's compatibility guidance during each installation session. Historical Docker package versions must not be treated as current release recommendations.

## 7. Current Status

The OS baseline and Docker installation are complete. Application deployments and service-domain routing remain pending.
