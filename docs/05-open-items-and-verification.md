# 05 — Open Items and Verification Checklist

**Status:** Active work list  
**Last updated:** 2026-10-13

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
- [x] Inspect UFW, nftables, Docker-published ports, and host firewall rules during the initial Hermes audit.
- [ ] Determine external reachability of published application ports from additional networks where appropriate.
- [ ] Verify Dahono ingress upstream targets, required ports, TLS, and source addresses.
- [ ] Define authentication requirements for each public dashboard.
- [ ] Review Hermes API authentication and network access; the unauthenticated `/v1/models` test returned HTTP `401`.
- [ ] Review Hermes terminal backend isolation; the current backend is `local` and does not provide sandbox isolation.
- [ ] Review trusted-proxy settings against official Hermes documentation.
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

- [x] Review the official 9Router repository and Docker guide.
- [x] Deploy 9Router image `ghcr.io/decolua/9router:0.5.95` using Docker Compose.
- [x] Verify Compose configuration, container running state, HTTPS login page, and API health endpoint.
- [x] Create and validate a local archive of 9Router persistent data.
- [x] Commit and push 9Router Compose configuration and safe environment template (`f5d7891`).
- [ ] Review direct exposure of port 20128 and confirm Dahono ingress/network behavior.
- [ ] Resolve the dashboard `0.5.99` notice against official published image tags.
- [ ] Perform a staging restore test for the 9Router backup.
- [x] Review official Hermes Agent Docker and dashboard documentation.
- [x] Deploy Hermes Agent and dashboard with Docker Compose using `nousresearch/hermes-agent:stable`.
- [x] Verify dashboard access through Dahono Web Ingress at `https://hermes.octalectzz.my.id`.
- [x] Verify Nous OAuth and Basic Auth login through the public HTTPS domain.
- [x] Verify that API port `8642` is not published as a host port in the Hermes Compose configuration.
- [x] Document observed Hermes container settings, network membership, runtime file permissions, and host firewall state.
- [ ] Finalize the public dashboard authentication policy and trusted-proxy review.
- [ ] Determine whether direct access to dashboard port `9119` can be restricted without breaking Dahono ingress.
- [ ] Review Hermes API network access and terminal backend isolation before adding more services to `octa-hub`.
- [x] Deploy n8n and verify its public HTTPS endpoint and API access.
- [ ] Finish reviewing Hermes documentation, then commit and push the verified changes.
- [x] Review official n8n Docker Compose guidance and verify the deployed external runner with a test workflow.
- [ ] Re-check the latest stable versions and compatibility before planned upgrades.
- [x] Select and deploy PostgreSQL as the n8n database; verify the database container health.
- [ ] Verify PostgreSQL backup/restore, permissions, and recovery procedures.
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

Complete the Hermes security review and documentation closeout. Commit and push only after reviewing the complete diff and confirming that no secrets or runtime data are staged. Then begin the next application in a separate session, following its official installation documentation.

## I. n8n and Hermes Integration

- [x] Authenticated n8n REST API request returned HTTP 200.
- [x] External runner test returned `runner-ok`.
- [x] Hermes `n8n-official` MCP client was shown as connected.
- [x] REST plugin list/get/create/update paths were tested.
- [x] Permanent REST test workflow was manually executed and returned `rest-api-ok`; it remains inactive.
- [ ] Review n8n security, ingress exposure, PostgreSQL/runner network boundaries, and backup/restore.
- [ ] If activation testing is needed, use a separate harmless workflow with an automatic trigger and explicit approval. The Manual Trigger-only test returned HTTP 400 on activation and remains inactive.
