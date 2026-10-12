# 13 — n8n Deployment and Hermes Integration

**Status:** Deployment and selected integration tests verified; security and operational closeout pending
**Last updated:** 2026-10-13

## 1. Official References

- n8n Docker Compose guide: https://docs.n8n.io/hosting/installation/server-setups/docker-compose/
- n8n hosting examples: https://github.com/n8n-io/n8n-hosting
- n8n REST API: https://docs.n8n.io/api/
- n8n MCP server: https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/
- Hermes Agent repository: https://github.com/NousResearch/hermes-agent
- Hermes Docker guide: https://hermes-agent.nousresearch.com/docs/user-guide/docker

Re-check official documentation and release notes before changing versions or configuration. The versions below are observed deployment references, not a claim that they are the latest versions available today.

## 2. Deployment Record

| Item | Observed state |
|---|---|
| Public URL | `https://n8n.octalectzz.my.id` |
| Compose file | `/opt/octa/stacks/n8n/compose.yaml` |
| Persistent data | `/opt/octa/data/n8n` |
| PostgreSQL data | `/opt/octa/data/n8n-postgres` |
| n8n image | `docker.n8n.io/n8nio/n8n:2.42.7` |
| Runner image | `n8nio/runners:2.42.7` |
| Database image | `postgres:18` |
| Docker network | `octa-hub`; private runner/database network `n8n-backend` |
| Proxy settings | `N8N_PROXY_HOPS=1`; secure cookies enabled; timezone `Asia/Jakarta` |

The ingress dashboard previously showed the n8n HTTPS route as Ready and forwarding to port `5678`. Do not change the provider ingress route without first collecting evidence that it is misconfigured.

## 3. Verified Checks

- An authenticated n8n REST API request returned HTTP `200`.
- The n8n MCP page showed client `Hermes Agent` connected with full access.
- MCP endpoint: `https://n8n.octalectzz.my.id/mcp-server/http`.
- Hermes has the `n8n-official` MCP integration enabled; it remains the primary integration.
- The `hermes-n8n-rest` plugin repository is `https://github.com/OctaLectzz/hermes-n8n-rest`. It is secondary to the official MCP integration.
- The plugin's five tools appeared in the Hermes tool catalog:
  - `n8n_rest_list_workflows`
  - `n8n_rest_get_workflow`
  - `n8n_rest_create_workflow`
  - `n8n_rest_update_workflow`
  - `n8n_rest_set_workflow_active`
- List, get, create, and update paths were exercised successfully through Hermes.
- External runner workflow `Octa - Runner Test` (`v5GwJGMvC7WMHIKV`) returned `runner-ok`.
- Permanent REST test workflow `Octa - REST API Integration Test - Updated` (`IHbqAs7sx1rtL5td`) was manually executed in the n8n UI and returned `rest-api-ok`. It must remain in place and inactive.

## 4. Workflow Activation Test — Failed as Expected for This Test Shape

An attempt to activate the Manual Trigger-only REST test workflow returned HTTP `400`. A subsequent read confirmed that the workflow remained inactive. This is not a successful activation test and must not be reported as one.

If activation behavior needs testing later, create a separate harmless workflow with a suitable automatic trigger, get approval before enabling it, verify its effect, then disable/remove it deliberately. Do not change the permanent REST test workflow's inactive state.

## 5. Hermes REST Plugin

Repository: https://github.com/OctaLectzz/hermes-n8n-rest
Verified commit: `e76d42d` — `Fix Hermes tool schema registration`

The plugin registers tool schemas from its metadata and uses the `N8N_API_KEY` and `N8N_BASE_URL` environment requirements. It enforces HTTPS for remote calls, rejects URL credentials/query/fragment, disables redirects, caps responses at 2 MB, uses a 20-second timeout, and redacts unexpected errors.

The GitHub Actions workflow provides offline unit tests; it is not a live integration test. Live behavior was separately checked using Hermes tools as listed above.

Real `N8N_API_KEY` values and any OAuth tokens must remain secret. Never copy them into documentation, Git, chat, or logs.

## 6. Safe Operational Checks

Run these on the VPS only when needed:

```bash
cd /opt/octa/stacks/n8n
sudo docker compose ps
sudo docker compose config --quiet
sudo docker compose logs --tail=100 n8n
```

Do not print `docker compose config` output: interpolated values can disclose credentials. Review logs before sharing them and redact tokens, passwords, personal data, and workflow payloads.

## 7. Remaining Work

- Review n8n public ingress and direct port exposure without changing the provider ingress speculatively.
- Verify authentication and authorization policy for public access.
- Review PostgreSQL and runner network isolation and least privilege.
- Confirm persistent volume ownership and permissions.
- Add verified backup and restore procedures for n8n and PostgreSQL, then test restoration in staging.
- Re-check deployed image digests/releases against official release information before planned upgrades.
- Review public GitHub disclosure risks before every push.
- Keep n8n and Hermes credentials in protected runtime configuration only.
