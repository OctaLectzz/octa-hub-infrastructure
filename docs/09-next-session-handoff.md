# 09 — Next Session Handoff

**Prepared:** 2026-10-12
**Current session scope:** 9Router only
**Next planned service:** Hermes Agent and dashboard
**Do not install Hermes in the 9Router session.**

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
- At handoff preparation, documentation changes were staged for review; verify the actual Git status before continuing.

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

## Start of the Following Session

Begin with a brief acknowledgment that the new session is for Hermes only. Review the official Hermes repository and documentation, verify current stable versions and requirements, then proceed one step at a time. Do not assume Hermes is installed until it has been deployed and verified.
