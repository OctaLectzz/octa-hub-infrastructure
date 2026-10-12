# 05 — Open Items and Verification Checklist

**Status:** Active work list  
**Last updated:** 2026-10-12

## A. Completed VPS Baseline Items

- [x] Confirmed Ubuntu 24.04.5 LTS (Noble).
- [x] Completed OS package upgrades and rebooted.
- [x] Confirmed SSH connectivity after reboot.
- [x] Installed Docker Engine and Compose plugin from the official Docker repository.
- [x] Verified Docker and containerd services and the `hello-world` test.
- [x] Created `/opt/octa` directory structure and five `.env.example` placeholders.
- [x] Created `.gitignore` and `README.md`.
- [x] Initialized local Git repository on `main`.
- [x] Created GitHub SSH key and verified GitHub SSH authentication.
- [x] Added SSH remote and pushed the initial commit to GitHub.

## B. GitHub and Repository

- [x] Repository: https://github.com/OctaLectzz/octa-hub-infrastructure
- [x] Branch `main` pushed and tracking `origin/main`.
- [x] Repository visibility intentionally left Public by user decision.
- [ ] Review actual `.gitignore` and root `README.md` on VPS against this policy.
- [ ] Verify the updated documentation files are committed and pushed.
- [ ] Review all staged/committed content for secrets and public-disclosure risks.

## C. Dahono VPS and Network

- [x] Record OS, CPU, memory, disk, container IP, and SSH endpoint.
- [ ] Review current SSH effective configuration and authentication logs.
- [ ] Verify Dahono NAT and port-forwarding details.
- [ ] Verify Dahono Web Ingress upstream target, required ports, TLS, and restart behavior.
- [ ] Verify recovery-console availability and restore behavior.
- [ ] Verify scope, retention, and cost of Dahono `Backup to KVM`.
- [ ] Recheck current firewall and listening ports before exposing applications.

## D. Security

- [ ] Evaluate password strength and login rate-limiting controls.
- [ ] Review UFW, nftables, Docker-published ports, and provider ingress together.
- [ ] Define authentication requirements for each public dashboard.
- [ ] Design a deletion-approval mechanism that cannot be bypassed for the Obsidian vault.
- [ ] Define Octa Hub's administrative action allowlist, additional authorization, and audit trail.
- [ ] Review GitHub content for public-disclosure risks before every push.

## E. Backup and Storage

- [ ] Check Cloudflare R2 capacity and usage.
- [ ] Check Dahono S3 plan, capacity, endpoint, and S3 API compatibility.
- [ ] Measure persistent-data size and local staging needs.
- [ ] Select and test Restic or an alternative against both destinations.
- [ ] Define consistent database backups and partial-destination failure handling.
- [ ] Store recovery key material outside the VPS.
- [ ] Configure daily backup at 05:00 WIB only after all applications are installed.
- [ ] Enforce three valid generations per destination without deleting the last valid backup.
- [ ] Test restoration in staging.

## F. Application and Integration

- [ ] Verify official repository and deployment procedure for 9router.
- [ ] Verify official Hermes Agent and dashboard documentation.
- [ ] Verify official n8n documentation, sandbox/runner template, and compatible versions.
- [ ] Confirm whether PostgreSQL is required and finalize database design.
- [ ] Verify Obsidian Web deployment option and security requirements.
- [ ] Verify internal SearXNG deployment and integrations.
- [ ] Determine Octa Hub build/deployment requirements.
- [ ] Measure resource usage with all services running.

## G. Confirmed Decisions

- Rebuild from scratch without restoring the old application installation.
- Use modular Docker Compose.
- Target Ubuntu 24.04 LTS.
- Follow official documentation and use current stable/LTS versions where applicable.
- Keep SSH password authentication for now; do not alter SSH/firewall before reviewing recovery access.
- Use Dahono Web Ingress for domains if verification confirms suitability.
- Hermes and n8n are intended to read and write the Obsidian vault.
- All vault deletion requires explicit owner/designated-administrator approval.
- Octa Hub uses tiered authorization for risky operations and avoids direct Docker socket/root access.
- First backup only after all applications are installed.
- Daily backup policy: 05:00 WIB to Cloudflare R2 and Dahono S3, encrypted, at most three valid generations per destination.
- Test restore in staging.
- Repository files are written in English.
- Store actual secrets in per-service `.env`; commit `.env.example` only.
- GitHub repository is Public for now, by user decision.

## H. Next Step

Finish reviewing and pushing the documentation layout. Then begin 9router in a separate session, reviewing official documentation before creating its Compose configuration.
