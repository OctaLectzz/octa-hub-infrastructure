# 06 — VPS Initialization Record

**Date:** 2026-10-12  
**Status:** Baseline tasks completed; documentation layout update remains to be committed and pushed.

## 1. VPS Baseline

| Item | Observed value |
|---|---|
| Provider | Dahono Cloud VPS (NAT) |
| Hostname | `octa-hub` |
| OS | Ubuntu 24.04.5 LTS (Noble) |
| Architecture | `amd64` / `x86_64` |
| Virtualization | LXC |
| Kernel | `7.0.2-6-pve` (from login banner) |
| CPU | 4 vCPU |
| RAM | 8 GiB |
| Swap | 2 GiB |
| Disk | approximately 49–50 GB |
| Container IP | `<VPS_CONTAINER_IP>` |
| Gateway | `<VPS_GATEWAY_IP>` |
| SSH endpoint | `<SSH_PUBLIC_IP>:<SSH_FORWARD_PORT>`, forwarded to internal port 22 |

The repository is Public. Review whether operational network details should remain publicly visible before committing this record.

## 2. OS Update and Reboot

- `apt update` and package upgrades were performed.
- The VPS was rebooted using the Dahono dashboard.
- SSH connectivity succeeded from a new connection after reboot.
- Post-reboot checks showed SSH and `ssh.socket` active.
- `dpkg --audit` returned no findings.
- No APT packages were pending upgrade at that check.
- `systemctl --failed --no-pager` reported no failed units.
- The reboot-required package list was empty after reboot.

## 3. Docker Installation

Docker was installed using the official instructions:
https://docs.docker.com/engine/install/ubuntu/

Official APT repository:
- URI: `https://download.docker.com/linux/ubuntu`
- Suite: `noble`
- Component: `stable`
- Architecture: `amd64`
- Signing key: `/etc/apt/keyrings/docker.asc`
- Source file: `/etc/apt/sources.list.d/docker.sources`

Packages installed:
- `docker-ce`
- `docker-ce-cli`
- `containerd.io`
- `docker-buildx-plugin`
- `docker-compose-plugin`

Versions observed during installation:
- Docker Engine `29.9.0`, build `f415da8`.
- Docker Compose `v5.6.0`.
- `containerd.io` `2.4.1-2~ubuntu.24.04~noble`.
- Docker Buildx plugin `0.38.0-1~ubuntu.24.04~noble`.

Verification reported:
- Docker service: `active`.
- containerd service: `active`.
- `docker run --rm hello-world`: successful.
- `docker ps -a`: empty after the one-shot test container exited and was removed.

These versions are historical observations, not a claim about the latest versions currently available.

## 4. Directory Layout and Environment Templates

Created:
- `/opt/octa/stacks/{router,hermes,n8n,obsidian,octa-hub}`
- `/opt/octa/data/{router,hermes,n8n,obsidian,octa-hub}`
- `/opt/octa/backups`
- `/opt/octa/logs`
- `/opt/octa/docs/{architecture,runbooks,changelog}`
- Empty `.env.example` files for `router`, `hermes`, `n8n`, `obsidian`, and `octa-hub`.
- `/opt/octa/.gitignore`
- `/opt/octa/README.md`

No service `compose.yaml` or actual application `.env` files have been created. Review the actual `.gitignore` and README content on the VPS before claiming their exact rules have been verified.

## 5. Git and GitHub

- Local Git repository initialized at `/opt/octa`.
- Branch: `main`.
- Initial commit: `cef90d26a56f09c3b04b4a47e17acec74da7c97a` (`docs: initialize Octa Hub infrastructure`).
- GitHub repository: https://github.com/OctaLectzz/octa-hub-infrastructure
- Remote: `git@github.com:OctaLectzz/octa-hub-infrastructure.git`.
- Ed25519 key pair created at `/root/.ssh/id_ed25519` and `/root/.ssh/id_ed25519.pub`.
- GitHub SSH authentication succeeded with `ssh -T git@github.com`.
- Initial push of `main` succeeded; local branch tracks `origin/main`.
- Last reported `git status`: clean and up to date.
- Repository visibility: Public by user decision for now.

The private key must never be committed or shared. The GitHub SSH key is separate from the VPS SSH password-login policy.

## 6. Not Yet Installed or Configured

- 9router
- Hermes Agent and dashboard
- n8n
- Obsidian Web
- Octa Hub
- SearXNG
- n8n sandbox/runner
- PostgreSQL (dependency still to be confirmed)
- Domain ingress and application HTTPS routing
- Application authentication and integrations
- Automated backup to Cloudflare R2 and Dahono S3

## 7. Next Session Handoff

The VPS baseline is usable: Ubuntu updated, Docker installed and verified, planned directory layout created, and initial GitHub push completed. Before the documentation closeout, review the public-disclosure implications of committing VPS IP/network details and verify `.gitignore`, root `README.md`, and current Git state.

9Router has since been deployed in a separate session. See docs/07-router-installation-record.md and docs/08-router-security-and-open-items.md. Its ingress exposure, published-version discrepancy, and restore test remain open. Do not assume other applications are installed until their health and access have been verified.
