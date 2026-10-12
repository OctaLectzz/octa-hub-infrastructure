# 01 — Architecture and Infrastructure Decisions

**Status:** Architecture agreed; application deployments not yet implemented  
**Last updated:** 2026-10-12

## 1. Goal

Rebuild Octa Hub services from scratch on Dahono VPS without restoring the previous installation. Deploy manually with Docker Compose and follow each project's official documentation and repository.

## 2. Verified VPS Baseline

- Provider: Dahono Cloud VPS (NAT).
- Hostname: `octa-hub`.
- OS: Ubuntu 24.04.5 LTS (Noble).
- Architecture: `amd64` / `x86_64`.
- Virtualization: LXC.
- CPU: 4 vCPU.
- RAM: 8 GiB; swap: 2 GiB.
- Disk: approximately 49–50 GB.
- Container IP: `<VPS_CONTAINER_IP>`; gateway: `<VPS_GATEWAY_IP>`.
- SSH public endpoint: `<SSH_PUBLIC_IP>:<SSH_FORWARD_PORT>`, forwarded to internal port 22.
- Docker Engine and Compose are installed and verified; see `06-vps-initialization-record.md`.

Because this repository is Public, consider whether operational network details should remain in this document before committing.

## 3. Services and Domains

- 9router — `https://router.octalectzz.my.id`
- Hermes Agent and dashboard — `https://hermes.octalectzz.my.id`
- n8n — `https://n8n.octalectzz.my.id`
- Obsidian Web — `https://obsidian.octalectzz.my.id`
- Octa Hub — `https://hub.octalectzz.my.id`
- SearXNG — planned internal service for Hermes and n8n; not to be exposed directly without an explicitly reviewed requirement.
- n8n Assistant sandbox/runner — planned; use official templates and compatible versions if required.

Dahono Web Ingress & Domains is the intended routing and HTTPS option, subject to verification of upstream targets, ports, TLS, and restart behavior.

## 4. Directory Layout

Created on the VPS:

```text
/opt/octa/
├── .git/
├── .gitignore
├── README.md
├── stacks/
│   ├── router/.env.example
│   ├── hermes/.env.example
│   ├── n8n/.env.example
│   ├── obsidian/.env.example
│   └── octa-hub/.env.example
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

Service `compose.yaml` files and actual application `.env` files have not yet been created. Add supporting directories such as SearXNG, PostgreSQL, sandbox/runner, or backup only when justified by verified official requirements and final architecture.

## 5. Principles

- Separate deployment configuration from persistent data.
- Use internal Docker networks for service-to-service communication where appropriate.
- Do not expose internal SearXNG, sandbox APIs, or runners directly to the internet.
- Do not give Octa Hub direct Docker socket access or root privileges just for monitoring.
- Apply least privilege to users, volumes, networks, and credentials.
- Use HTTPS through the ingress mechanism after its behavior is verified.
- Vault read/write access must not allow unapproved deletion.
- Follow supported component combinations in official templates rather than independently pinning every image to `latest`.

## 6. Version Policy

Check current stable/LTS releases and compatibility requirements during each installation session. The versions recorded in the initialization record are historical observations, not claims about current releases.

## 7. Status

OS baseline, Docker, directory setup, and initial GitHub push are complete. 9Router is deployed and its basic health endpoint is verified. Its ingress security review and version check remain open; other application deployments are pending.
