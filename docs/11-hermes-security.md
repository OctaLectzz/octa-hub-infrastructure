# 11 — Hermes Agent Security Review

**Status:** Initial security audit documented; residual risks remain under review
**Last updated:** 2026-10-12

## 1. Official Sources

- Repository: [https://github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Docker installation: [https://hermes-agent.nousresearch.com/docs/user-guide/docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker)
- Web dashboard: [https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)
- API server: [https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server)
- Security and sandboxing: [https://hermes-agent.nousresearch.com/docs/user-guide/security](https://hermes-agent.nousresearch.com/docs/user-guide/security)

Verify security settings against the current official documentation before applying changes. Recheck documentation for the deployed release before changing authentication, networking, or execution isolation.

## 2. Current Deployment

| Item                      | Observed state                                           |
| ------------------------- | -------------------------------------------------------- |
| Container                 | `hermes`                                                 |
| Image reference           | `nousresearch/hermes-agent:stable`                       |
| Dashboard domain          | `https://hermes.octalectzz.my.id`                        |
| Dashboard port            | `9119`, published by Compose                             |
| API server port           | `8642`, not published as a host port                     |
| Docker network            | `octa-hub`                                               |
| Network members observed  | `hermes` and `router`                                    |
| Terminal backend          | `local`                                                  |
| Dashboard authentication  | Nous OAuth and Basic Auth login previously verified      |
| UFW                       | Inactive during the 2026-10-12 audit                     |
| Container privilege       | `Privileged=false`; no added Linux capabilities observed |
| Container user            | `root`                                                   |
| Container root filesystem | Writable                                                 |
| Host Docker socket        | Not mounted                                              |

These observations describe the inspected deployment at the time of the audit. They do not constitute a complete penetration test or prove that all external access paths are secure.

## 3. Dashboard Authentication

Nous OAuth and Basic Auth login have both been verified through the public HTTPS domain.

A request to `https://hermes.octalectzz.my.id/` returned HTTP `302` with `Location: /login?next=%2F`. TLS verification succeeded in the tested request. The dashboard reported `auth_required=True` and registered providers `basic` and `nous`.

These results confirm the observed login gate and redirect behavior, but do not independently establish the security of every authentication flow or session-handling path.

The final public authentication policy remains a documented decision. According to the official dashboard guidance, Basic Auth is intended for trusted networks or VPNs, while OAuth or suitable OIDC is the recommended approach for public-facing dashboards.

Before changing authentication settings:

- Review the current official dashboard authentication guidance.
- Decide which authentication provider or combination is required.
- Confirm the intended login flow before and after any change.
- Never record real passwords, OAuth secrets, or session tokens in this document.

## 4. API Server Exposure

The Hermes API server is enabled on container port `8642`. Compose does not publish this port to the VPS host, and no host listener on `8642` was observed during the audit.

`API_SERVER_KEY` was detected in the Hermes runtime environment file without displaying its value.

An unauthenticated request to `http://127.0.0.1:8642/v1/models` from inside the Hermes container returned HTTP `401`. This confirms that the tested request was rejected without authentication; it does not verify every endpoint or authenticated authorization behavior.

The observed Docker network `octa-hub` contains `hermes` and `router`. Other containers on that network may be able to reach the Hermes API at the container address and port. Actual access requirements and authorization boundaries have not been exhaustively tested.

Required controls and follow-up:

- Keep port `8642` unpublished on the VPS host unless a reviewed requirement changes.
- Protect the API key and never print it during verification.
- Identify which services require API access.
- Review whether the shared Docker network provides more access than necessary.
- Do not expose the API publicly as a troubleshooting shortcut.
- Recheck API authentication and required integrations after any network change.

Official reference: [https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server)

## 5. Terminal Backend and Sandbox

The current Hermes configuration uses `terminal.backend: local`.

The container runs as `root` and has a writable root filesystem. It is not privileged, no additional Linux capabilities were observed, and the host Docker socket is not mounted. These controls reduce some forms of host access but do not provide terminal-command isolation.

The Docker CLI exists inside the Hermes container, but the Docker daemon is not reachable from it. Do not mount the host Docker socket merely to enable another backend; access to that socket can grant extensive control over host containers and resources.

The official security documentation distinguishes the local backend, which does not provide sandbox isolation, from supported sandbox backends. Any change must follow the deployment-specific official guidance.

Follow-up:

- Evaluate the consequences of agent-executed terminal commands.
- Review access to the mounted persistent data at `/opt/data`.
- Determine which official isolation backend is compatible with the deployed release and intended workflows.
- Test any proposed isolation change before applying it to the running deployment.
- Verify required agent features after a change.

Do not claim that terminal commands are sandboxed until the actual configuration and behavior have been verified.

Official reference: [https://hermes-agent.nousresearch.com/docs/user-guide/security](https://hermes-agent.nousresearch.com/docs/user-guide/security)

## 6. Trusted Proxy and Ingress

The dashboard is served through Dahono Web Ingress at `https://hermes.octalectzz.my.id`. The public DNS resolved to `143.20.199.50` during the audit. The HTTPS response included `server: Caddy` and `server: uvicorn`; these headers do not establish the full ingress topology.

The ingress upstream target and source address have not been independently verified. No matching `public_url` or `trusted_proxies` configuration line was found by the limited configuration search; this is not proof that all related settings are absent.

During the audit:

- UFW reported `inactive`.
- Docker published `9119` as `0.0.0.0:9119` and `[::]:9119`.
- Host firewall rules showed permissive default input and forwarding policies; the `DOCKER-USER` chain was empty.
- A Windows TCP connection test to the public IP on port `9119` failed.
- The failed external test does not prove the port is unreachable from every network.
- HTTPS through the domain returned a login redirect and passed TLS verification.

Treat direct port exposure as a residual risk until the provider ingress path and external reachability are fully understood.

Follow-up:

- Verify the Dahono ingress upstream target and source addresses.
- Review the official trusted-proxy guidance before changing proxy settings.
- Trust only verified proxy addresses or appropriately narrow ranges.
- Do not configure wildcard or unnecessarily broad trusted ranges.
- Determine whether direct access to port `9119` can be restricted without breaking HTTPS ingress.
- Recheck authentication, client IP handling, and domain routing after any change.

Official reference: [https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)

## 7. Secrets and Persistent Data

- Keep real environment files and credentials on the VPS.
- Keep Hermes runtime data outside the Git repository.
- Commit placeholder templates only.
- Do not print secrets when inspecting environment variables or rendered Compose configuration.
- Restrict permissions on files containing credentials and authentication state.
- The inspected runtime files `.env`, `config.yaml`, and `auth.json` had mode `600` and owner `hermes:hermes`.
- Do not delete persistent data as part of routine troubleshooting.
- Review all staged changes before pushing to the public repository.

## 8. Security Closeout Checklist

- [x] Confirm API port `8642` is not published as a host port in Compose.
- [x] Detect `API_SERVER_KEY` in the runtime environment file without displaying the value.
- [x] Verify that an unauthenticated API request to `/v1/models` returns `401`.
- [x] Verify Nous OAuth and Basic Auth login through HTTPS in prior testing.
- [x] Confirm dashboard login redirect and successful TLS verification.
- [x] Inspect Docker network members, port mappings, container privilege, mounts, and runtime file permissions.
- [x] Inspect UFW status and host nftables/iptables rules.
- [x] Attempt external TCP access to port `9119`; the tested connection failed.
- [ ] Decide the final public dashboard authentication policy.
- [ ] Verify the Dahono ingress upstream target and actual ingress source addresses.
- [ ] Determine whether direct dashboard port exposure can be restricted safely.
- [ ] Review API access requirements and network isolation between containers.
- [ ] Review terminal backend risks and supported sandbox options.
- [ ] Recheck the current official documentation before any security configuration change.
- [ ] Record the results of any approved changes and repeat relevant tests before declaring security closeout complete.

## 9. Change Control

Before applying a security change:

1. Read the relevant official documentation.
2. Inspect the current configuration without exposing secrets.
3. Record the intended change and its expected impact.
4. Apply one change at a time.
5. Validate configuration and verify service health.
6. Test the affected authentication, API, execution, and network behavior.
7. Update the documentation with observed results.

Do not mark an item complete solely because a configuration file was edited.

The current audit documents observed controls and residual risks. It does not certify that the deployment is completely secure.
