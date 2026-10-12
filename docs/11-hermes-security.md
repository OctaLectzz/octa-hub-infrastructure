# 11 — Hermes Agent Security Review

**Status:** Security review in progress
**Last updated:** 2026-10-12

## 1. Official Sources

- Repository: https://github.com/NousResearch/hermes-agent
- Docker installation: https://hermes-agent.nousresearch.com/docs/user-guide/docker
- Web dashboard: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard

Verify security settings against the current official documentation before applying changes.

## 2. Current Deployment

| Item | Observed state |
|---|---|
| Container | `hermes` |
| Dashboard domain | `https://hermes.octalectzz.my.id` |
| Dashboard port | `9119`, published by Compose |
| API server port | `8642`, not published as a host port |
| Docker network | `octa-hub` |
| Terminal backend | `local` |
| Dashboard authentication | Nous OAuth and Basic Auth login verified |

These observations describe the current deployment and do not constitute a complete security audit.

## 3. Dashboard Authentication

Nous OAuth and Basic Auth have both been verified through the public HTTPS domain.

The final authentication policy remains open for review. Basic Auth should not be assumed appropriate for unrestricted public exposure merely because login works.

Before changing authentication settings:

- Review the current official dashboard authentication guidance.
- Decide which authentication provider or combination is required.
- Confirm that the intended login flow works before and after any change.
- Never record real passwords, OAuth secrets, or session tokens in this document.

## 4. API Server Exposure

The Hermes API server is enabled and configured to listen on the container network at port `8642`. Compose does not publish this port to the VPS host.

This does not guarantee isolation from other containers. Services attached to `octa-hub` may be able to reach the API server.

Required review:

- Identify which containers are attached to `octa-hub`.
- Verify the API authentication requirements using the official documentation.
- Confirm which services actually require API access.
- Restrict unnecessary network access without breaking required model-provider or messaging connectivity.
- Do not publish port `8642` publicly as a troubleshooting shortcut.

Never place API keys in Git, terminal transcripts, screenshots, or this document.

## 5. Terminal Backend and Sandbox

The current Hermes configuration uses `terminal.backend: local`.

The Docker CLI exists inside the Hermes container, but the Docker daemon is not reachable from it. No host Docker socket should be mounted merely to enable a different backend.

Required review:

- Read the official Hermes sandbox and terminal backend documentation.
- Determine which execution isolation options are supported by the deployed release.
- Evaluate the risks of agent-executed commands and access to mounted persistent data.
- Test any proposed isolation change before applying it to the running deployment.
- Verify that required agent features continue to work after a change.

Do not claim that commands are safely sandboxed until the actual configuration and behavior have been verified.

## 6. Trusted Proxy

The dashboard is served through Dahono Web Ingress.

The actual ingress source address and trusted-proxy configuration must be verified before making proxy-related changes.

- Trust only verified proxy addresses or appropriately narrow ranges.
- Do not configure wildcard or unnecessarily broad trusted ranges.
- Do not assume that the ingress provider's source IP is known without verification.
- Recheck authentication and client IP handling after any change.

## 7. Secrets and Persistent Data

- Keep real environment files and credentials on the VPS.
- Keep Hermes runtime data outside the Git repository.
- Commit placeholder templates only.
- Do not print secrets when inspecting environment variables or rendered Compose configuration.
- Restrict access to files containing credentials and authentication state.
- Do not delete persistent data as part of routine troubleshooting.

## 8. Security Closeout Checklist

- [x] Confirm API port `8642` is not published as a host port in Compose.
- [x] Verify Nous OAuth login through HTTPS.
- [x] Verify Basic Auth login through HTTPS.
- [ ] Decide the final public dashboard authentication policy.
- [ ] Verify trusted-proxy settings and the actual ingress source.
- [ ] Review API access from containers attached to `octa-hub`.
- [ ] Review terminal backend risks and supported sandbox options.
- [ ] Verify the final configuration against official documentation.
- [ ] Record the results of the security review before declaring closeout complete.

## 9. Change Control

Before applying a security change:

1. Read the relevant official documentation.
2. Inspect the current configuration without exposing secrets.
3. Record the intended change and its expected impact.
4. Apply one change at a time.
5. Validate configuration and verify service health.
6. Test the affected authentication, API, or execution behavior.
7. Update the documentation with observed results.

Do not mark an item complete solely because a configuration file was edited.
