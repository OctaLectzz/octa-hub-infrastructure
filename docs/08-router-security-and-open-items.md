# 08 — 9Router Security Review and Open Items

**Date:** 2026-10-13
**Status:** Network observations recorded; remediation and restore verification remain open

## Verified Controls

- Actual environment file is local at `stacks/router/.env`.
- Git ignores `stacks/router/.env`.
- Environment file permissions were observed as `600`.
- `.env.example` uses safe placeholders for secrets.
- Compose enables `no-new-privileges:true`.
- Application data is stored in a persistent host directory.
- A local data archive was created and its archive listing was verified.
- The dashboard password was changed by the user after initial setup.

## Network Audit Results (2026-10-13)

### Confirmed observations

- The Dahono Web Ingress entry for `router.octalectzz.my.id` targets port `20128`.
- The public HTTPS health endpoint `https://router.octalectzz.my.id/api/health` returned HTTP `200`.
- An unauthenticated request to `/v1/models` returned HTTP `401`.
- `/` returned HTTP `307` with `Location: /dashboard`.
- `/dashboard` returned HTTP `307` with `Location: /login`.
- `/login` returned HTTP `200`.
- A TCP connection attempt from the owner's Windows Wi-Fi network to `143.20.199.50:20128` failed. This only describes that test source and does not prove the port is unreachable from every network.
- Docker publishes `20128:20128` on all host interfaces. The container is attached to `router_default` and `octa-hub`; persistent data is bind-mounted from `/opt/octa/data/router` to `/app/data`.
- Host firewall observations: UFW inactive; nftables `input` and `forward` policies were `accept`; `DOCKER-USER` was empty at the time of inspection.
- Runtime configuration observed: `DATA_DIR=/app/data`, `PORT=20128`, `HOSTNAME=0.0.0.0`, `NODE_ENV=production`, `REQUIRE_API_KEY=true`, `AUTH_COOKIE_SECURE=true`, `ENABLE_REQUEST_LOGS=false`.
- The owner accepts the Dahono Web Ingress source-IP trust question as resolved for this checklist. The source IP/range was not independently observed in the dashboard during this session; this is an owner decision, not an independently verified network fact.

### Interpretation and limits

- API authentication was confirmed only for the tested `/v1/models` request without an API key. This is not a complete authorization test.
- The dashboard redirect confirms the tested `/dashboard` route redirects to `/login` without an established session. Other administrative routes were not tested.
- Direct TCP failure from one client does not establish global network inaccessibility.
- No firewall, port-binding, ingress, or container configuration was changed during this audit.

## Open Security Checks

1. Compose currently publishes `20128:20128`, binding the port on all host interfaces.
2. Earlier configuration used `127.0.0.1:20128:20128`, but the public HTTPS ingress returned HTTP 502 with that binding.
3. The HTTPS domain later returned a healthy API response after switching to the all-interface binding.
4. Direct TCP to `143.20.199.50:20128` failed from one Windows Wi-Fi client. Exposure from other networks remains unverified.
5. The owner accepts the Web Ingress source-IP trust item as resolved for checklist purposes; the source range was not independently observed. Host firewall policy and Docker port publication still require a safe remediation plan.
6. Do not change port binding or firewall rules until the routing path and recovery access are understood.
7. The local archive has not been restored in staging and does not replace an off-site backup.

## Version Check

The running image is `ghcr.io/decolua/9router:0.5.95`. The dashboard reported `0.5.99`, but the newer tag was not confirmed in the official registry during this session. Verify the registry's actual published tags before upgrading.

## Closure Criteria

- [x] Initial public/private exposure checks recorded: HTTPS ingress works; direct TCP test from one client failed; host firewall and Docker publication were inspected.
- [x] Dahono Web Ingress domain and target port `20128` recorded; source-IP trust accepted by owner for checklist purposes, but not independently verified.
- [ ] Safely restrict direct access to port `20128` without breaking Dahono ingress; validate from external clients.
- [ ] Published version discrepancy (`0.5.95` runtime versus dashboard `0.5.99` notice) resolved against official registry tags.
- [ ] Backup restore procedure tested in staging; SQLite integrity check alone is insufficient.
- [x] Audit observations recorded in the security review and verification checklist.
- [ ] Update README if the verified findings require a public-facing documentation change.
