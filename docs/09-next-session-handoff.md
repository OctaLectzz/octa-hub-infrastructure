# 09 — Next Session Handoff

**Prepared:** 2026-10-12
**Current session scope:** Hermes Agent and dashboard deployment and security closeout
**Current deployment:** Hermes is installed and running; dashboard OAuth and Basic Auth login have been verified
**Next planned service:** Complete Hermes security closeout, then proceed to the next application in a separate session.

## Project Rules

- Use official project repositories and official installation documentation.
- Verify the current stable/latest release and compatibility at installation time.
- Use Docker Compose with per-service configuration under `/opt/octa/stacks/<service>/`.
- Keep persistent data under `/opt/octa/data/<service>/`.
- Never commit `.env`, credentials, API keys, private keys, database data, or backups.
- Validate configuration before deployment.
- Verify container state, logs, health, persistence, authentication, network exposure, domain routing, and HTTPS before calling a service complete.
- Update documentation, review staged files, commit, and push each completed service.
- After the service is healthy and no questions remain, close the session and start a new Project session for the next service.
- Do not install multiple services in one session unless the user explicitly changes this rule.

## Current VPS

- Hostname: `octa-hub`
- OS: Ubuntu 24.04.5 LTS
- Architecture: `amd64`
- Docker Engine and Compose are installed.
- Repository: https://github.com/OctaLectzz/octa-hub-infrastructure
- Branch: `main`
- Remote: `origin`
- Hermes documentation and Compose changes are currently under review; check `git status` and the complete diff before committing.

## 9Router State

- Container: `router`
- Image: `ghcr.io/decolua/9router:0.5.95`
- Compose: `/opt/octa/stacks/router/compose.yaml`
- Environment file: `/opt/octa/stacks/router/.env` (secret; do not display or commit)
- Environment template: `/opt/octa/stacks/router/.env.example`
- Data: `/opt/octa/data/router/`
- Backup: `/opt/octa/backups/router-data-20261012-084444.tar.gz`
- Domain: https://router.octalectzz.my.id
- Health endpoint returned `{"ok":true}`.
- Latest configuration commit: `f5d7891` (`chore(router): add Docker Compose configuration`), pushed to GitHub.

## Outstanding 9Router Checks

- Port `20128` currently uses `20128:20128` and binds to all host interfaces.
- Dahono ingress and direct port exposure need a security review.
- Dashboard showed a `0.5.99` update notice, but the tag was not verified in the official registry during the session.
- The local backup has not been restored in staging.
- README and verification checklist have been updated; confirm the documentation commit is pushed before beginning the next service.

Do not repeat VPS initialization. Resume from the repository's actual Git state and these notes.

## Hermes Deployment and Security State

- Hermes Agent is deployed using Docker Compose with image `nousresearch/hermes-agent:stable`.
- Public dashboard: `https://hermes.octalectzz.my.id`.
- Nous OAuth and Basic Auth login were verified through the public HTTPS domain.
- Dashboard port `9119` is published on all host interfaces (`0.0.0.0` and `[::]`). Whether direct access can be restricted without breaking Dahono Web Ingress remains unresolved.
- API port `8642` is not published as a host port. An unauthenticated request to `/v1/models` returned HTTP `401`; API authorization and container-to-container access still require further review.
- Hermes and 9Router share the Docker network `octa-hub`.
- The terminal backend is `local`, without sandbox isolation. The container runs as `root`, has a writable root filesystem, and does not mount the host Docker socket.
- UFW was inactive during the audit. Host firewall and Docker-published port findings are documented in `docs/11-hermes-security.md`.
- The runtime files `.env`, `config.yaml`, and `auth.json` were observed with permissions `600` and owner `hermes:hermes`.
- The Hermes security findings and residual risks have been documented. This is not a complete penetration test or security certification.

## Start of Following Session

1. Check `git status --short` and inspect the current diff before making further edits.
2. Finish reviewing `docs/05-open-items-and-verification.md`, `docs/09-next-session-handoff.md`, and `docs/03-security-and-access.md` against `docs/11-hermes-security.md`.
3. Verify that documentation distinguishes confirmed observations from unresolved risks.
4. Run `git diff --check` and inspect all changed files for accidental disclosure of secrets before staging.
5. Commit and push the reviewed documentation only after the final review.
6. After the documentation is pushed, continue with the separate 9Router security review, including published port `20128`, Dahono ingress behavior, official image updates, and the existing backup's restore verification.

Do not change live security settings or expose credentials as part of documentation-only work.

## n8n Deployment and Hermes Integration

- Domain: https://n8n.octalectzz.my.id
- Compose file: `/opt/octa/stacks/n8n/compose.yaml`
- Persistent data: `/opt/octa/data/n8n` and `/opt/octa/data/n8n-postgres`
- Observed images: `docker.n8n.io/n8nio/n8n:2.42.7`, `n8nio/runners:2.42.7`, and `postgres:18`.
- REST API, external runner, Hermes MCP connection, and selected REST plugin operations were tested.
- Permanent workflow `Octa - REST API Integration Test - Updated` (`IHbqAs7sx1rtL5td`) must remain present and inactive; manual execution returned `rest-api-ok`.
- Activation attempt on the Manual Trigger-only test returned HTTP 400. It remains inactive.
- The active Compose configuration publishes port 5678 on all IPv4 and IPv6 host interfaces. Direct internet reachability is not yet established; verify Dahono NAT, ingress, and firewall rules before changing this mapping.
- See `docs/13-n8n-deployment-and-hermes-integration.md` for the deployment record and remaining checks.

## Documentation Update Status

The proposed documentation ZIP is staged under `/tmp/octa-doc-stage`. Do not overwrite the repository blindly. Preserve local n8n changes, review the complete diff, scan for secrets, and only then commit and push.
