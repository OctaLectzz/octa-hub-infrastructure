# 10 — Hermes Agent Deployment

**Status:** Deployed; dashboard authentication verified; security review pending
**Last updated:** 2026-10-12

## 1. Official Sources

- Repository: https://github.com/NousResearch/hermes-agent
- Docker installation: https://hermes-agent.nousresearch.com/docs/user-guide/docker
- Web dashboard: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard

Use official documentation to verify installation requirements, current stable releases, configuration options, and upgrade procedures before making changes.

## 2. Deployment Overview

| Item | Configuration |
|---|---|
| Service | Hermes Agent |
| Docker image | `nousresearch/hermes-agent:stable` |
| Container name | `hermes` |
| Compose file | `/opt/octa/stacks/hermes/compose.yaml` |
| Environment file | `/opt/octa/stacks/hermes/.env` |
| Persistent data | `/opt/octa/data/hermes/` |
| Container home | `/opt/data` |
| Docker network | `octa-hub` |
| Dashboard URL | https://hermes.octalectzz.my.id |
| Dashboard port | `9119` |
| API server port | `8642` |

The Compose configuration uses the external Docker network `octa-hub`.

## 3. Persistent Data and Secrets

The host directory `/opt/octa/data/hermes/` is mounted at `/opt/data` inside the container.

Runtime configuration, authentication state, provider credentials, and other application data must remain on the VPS. Do not commit runtime data or real environment files to Git.

The repository may contain `.env.example` with placeholders only. Never paste API keys, OAuth secrets, Telegram tokens, or passwords into documentation.

## 4. Authentication and Integrations

The following have been verified:

- Dashboard access through the public HTTPS domain.
- Nous OAuth login through the public HTTPS domain.
- Basic Auth login through the public HTTPS domain.
- Telegram connectivity was previously confirmed in gateway logs.

The final public authentication policy remains under review. Verify the official dashboard security guidance before changing authentication settings.

## 5. Network Exposure

- Dashboard port `9119` is published by Compose.
- API server port `8642` is configured inside the container but is not published as a host port in Compose.
- Containers attached to `octa-hub` may be able to reach services on that network. Review network access before attaching additional applications.
- Do not assume that an unpublished port is unreachable from other containers.

## 6. Runtime and Security Notes

- The current terminal backend is `local`.
- The Docker CLI exists inside the Hermes container, but the Docker daemon is not reachable from it.
- Do not mount the host Docker socket as a quick fix; doing so can grant an agent broad control over host containers.
- Review the official Hermes sandbox documentation before changing terminal execution settings.
- Verify trusted-proxy settings against the actual ingress proxy source. Do not configure wildcard or unnecessarily broad trusted ranges.

## 7. Validation Checklist

- [x] Compose configuration validates successfully.
- [x] Dashboard responds through the configured HTTPS domain.
- [x] Nous OAuth login verified.
- [x] Basic Auth login verified.
- [x] API port `8642` is not published as a host port in Compose.
- [ ] Review public dashboard authentication policy.
- [ ] Review trusted-proxy configuration.
- [ ] Review API network boundaries and terminal sandbox isolation.
- [ ] Complete documentation review and commit verified changes.

## 8. Operational Commands

Run commands from the Compose directory:

```bash
cd /opt/octa/stacks/hermes

# Validate configuration without printing rendered secrets
sudo docker compose config --quiet

# Check container state
sudo docker compose ps

# Read recent logs
sudo docker compose logs --tail=100 hermes
```

Do not run upgrades, recreate the container, or change authentication and network settings without reviewing the official documentation and current deployment state first.
