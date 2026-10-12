# 04 — Installation and Verification Runbook

**Status:** VPS baseline and Docker installation completed; application installation pending  
**Last updated:** 2026-10-12

## 1. Scope

This runbook tracks baseline setup and the workflow for future application installations. It does not imply that 9router, Hermes, n8n, Obsidian Web, or Octa Hub is installed.

## 2. Completed OS Maintenance

- Ubuntu 24.04.5 LTS (Noble) was updated.
- The VPS was rebooted through the Dahono dashboard after package updates.
- A new SSH connection succeeded after reboot.
- Post-reboot checks reported SSH and `ssh.socket` active, no failed systemd units, no pending APT upgrades, and an empty `dpkg --audit`.

## 3. Completed Docker Installation

Official documentation followed:
https://docs.docker.com/engine/install/ubuntu/

Docker's official APT source was configured for Ubuntu Noble, stable component, amd64, signed by `/etc/apt/keyrings/docker.asc`, with source file `/etc/apt/sources.list.d/docker.sources`.

Packages installed:
- `docker-ce`
- `docker-ce-cli`
- `containerd.io`
- `docker-buildx-plugin`
- `docker-compose-plugin`

Versions observed at installation:
- Docker Engine: `29.9.0`
- Docker Compose: `v5.6.0`
- containerd.io: `2.4.1-2~ubuntu.24.04~noble`
- Docker Buildx plugin: `0.38.0-1~ubuntu.24.04~noble`

Verification:
- Docker service was active.
- containerd service was active.
- `docker run --rm hello-world` succeeded.
- The one-shot test container was removed after completion.

These versions are historical observations, not a claim about the latest versions currently available.

## 4. Completed Directory and Git Initialization

- Created `/opt/octa` with stack directories for `router`, `hermes`, `n8n`, `obsidian`, and `octa-hub`.
- Created matching persistent-data directories.
- Created `backups`, `logs`, and documentation subdirectories.
- Created empty `.env.example` files for the five planned services.
- Created `.gitignore` and `README.md`.
- Initialized Git on branch `main`.
- Initial commit: `cef90d26a56f09c3b04b4a47e17acec74da7c97a`.
- Added GitHub SSH remote: `git@github.com:OctaLectzz/octa-hub-infrastructure.git`.
- Verified GitHub SSH authentication and pushed `main`.
- Last reported Git status was clean and up to date.

## 5. Environment Template Workflow

For each service:
1. Review the official repository and installation documentation.
2. Determine supported environment variables and required persistent mounts.
3. Add only verified variables to `.env.example` with safe placeholders.
4. Create the actual `.env` on the VPS and set restrictive permissions.
5. Validate Compose configuration before starting the service.
6. Verify health, logs, persistence, and network exposure.

Example after the official configuration is ready:

```bash
cd /opt/octa/stacks/<service>
cp .env.example .env
chmod 600 .env
nano .env
```

Do not use guessed environment variables or unverified Compose templates.

## 6. Future Application Session Workflow

For each application:
1. Verify the official repository and documentation.
2. Check the latest stable/LTS version and compatibility constraints.
3. Review dependencies and public ingress requirements.
4. Create Compose configuration and environment template from official guidance.
5. Deploy incrementally.
6. Verify container health, logs, persistence, authentication, and network exposure.
7. Test domain routing and HTTPS after provider ingress is understood.
8. Update relevant documentation and the open-items list.
9. Review staged files for secrets, commit, and push.
10. When the installation is healthy and no questions remain, close the session and start a new session for the next application.

## 7. Safety Notes

- Do not change SSH or firewall settings without reviewing NAT and recovery access.
- UFW was inactive during an earlier audit; recheck current state before changes.
- Docker-published ports may not be blocked as expected by UFW alone.
- Do not assume Dahono Web Ingress behavior until verified.
- Do not report success without supporting verification output.
