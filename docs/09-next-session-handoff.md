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

- Official repository: https://github.com/NousResearch/hermes-agent
- Official Docker guide: https://hermes-agent.nousresearch.com/docs/user-guide/docker
- Official dashboard guide: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard
- Compose: `/opt/octa/stacks/hermes/compose.yaml`
- Persistent data: `/opt/octa/data/hermes/`
- Image reference: `nousresearch/hermes-agent:stable`
- Dashboard: `https://hermes.octalectzz.my.id`, routed through Dahono Web Ingress to port `9119`
- Nous OAuth and Basic Auth login have both been verified through HTTPS.
- Telegram connection was previously confirmed in gateway logs.
- API server uses port `8642`, which is not published as a host port in Compose.
- `terminal.backend` remains `local`. Docker CLI exists in the container, but the Docker daemon is not reachable. Do not mount the host Docker socket as a quick fix.
- API access from containers on `octa-hub`, sandbox isolation, trusted-proxy settings, and the public dashboard authentication policy still require review.
- Never display or commit actual `.env` files, OAuth credentials, API keys, Telegram tokens, or Hermes runtime data.

## Start of the Following Session

First review the actual Git status and full diff. Verify that only safe Compose, template, and documentation files are included. Complete the Hermes security review before marking the installation closed. Do not repeat VPS initialization or reinstall Hermes unless a verified issue requires it. Once Hermes is documented and pushed, start the next application in a separate session and follow its official documentation.
