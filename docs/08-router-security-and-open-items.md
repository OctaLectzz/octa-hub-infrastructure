# 08 — 9Router Security Review and Open Items

**Date:** 2026-10-12
**Status:** Review pending

## Verified Controls

- Actual environment file is local at `stacks/router/.env`.
- Git ignores `stacks/router/.env`.
- Environment file permissions were observed as `600`.
- `.env.example` uses safe placeholders for secrets.
- Compose enables `no-new-privileges:true`.
- Application data is stored in a persistent host directory.
- A local data archive was created and its archive listing was verified.
- The dashboard password was changed by the user after initial setup.

## Open Security Checks

1. Compose currently publishes `20128:20128`, binding the port on all host interfaces.
2. Earlier configuration used `127.0.0.1:20128:20128`, but the public HTTPS ingress returned HTTP 502 with that binding.
3. The HTTPS domain later returned a healthy API response after switching to the all-interface binding.
4. Direct port reachability from the user's client failed in a prior test; this does not prove that the port is inaccessible from every network.
5. Dahono NAT, Web Ingress, upstream target, firewall rules, and externally reachable ports must be reviewed together.
6. Do not change port binding or firewall rules until the routing path and recovery access are understood.
7. The local archive has not been restored in staging and does not replace an off-site backup.

## Version Check

The running image is `ghcr.io/decolua/9router:0.5.95`. The dashboard reported `0.5.99`, but the newer tag was not confirmed in the official registry during this session. Verify the registry's actual published tags before upgrading.

## Closure Criteria

- [ ] Public and private network exposure reviewed.
- [ ] Dahono ingress and upstream port confirmed.
- [ ] Published version discrepancy resolved.
- [ ] Backup restore procedure tested or documented as pending.
- [ ] README and checklist reflect verified state.
