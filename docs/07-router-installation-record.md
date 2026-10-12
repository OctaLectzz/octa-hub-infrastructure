# 07 — 9Router Installation Record

**Date:** 2026-10-12
**Status:** Deployed; basic health and public HTTPS access verified.
**Scope:** 9Router only. Other applications are out of scope for this session.

## 1. Official Sources

- Official repository: https://github.com/decolua/9router
- Official Docker guide: https://github.com/decolua/9router/blob/master/DOCKER.md
- Official GHCR package: https://github.com/decolua/9router/pkgs/container/9router

Follow the official documentation and verify the currently published image before upgrades.

## 2. Deployment

- Compose directory: `/opt/octa/stacks/router/`
- Compose file: `compose.yaml`
- Local environment file: `.env` (must never be committed)
- Safe environment template: `.env.example`
- Persistent data: `/opt/octa/data/router/`
- Container name: `router`
- Image: `ghcr.io/decolua/9router:0.5.95`
- Application port: `20128`
- Public URL: https://router.octalectzz.my.id

The deployed image metadata reported version `0.5.95`. The dashboard showed a newer-version notification (`0.5.99`), but that tag was not confirmed in the official GHCR package during the session. Do not upgrade until the published tag and compatibility are verified.

## 3. Compose Configuration Summary

- Restart policy: `unless-stopped`
- Environment loaded from local `.env`
- Persistent bind mount: `/opt/octa/data/router:/app/data`
- `no-new-privileges:true`
- Init process enabled
- Published port: `20128:20128`

The current port binding exposes port 20128 on all host interfaces. Review provider NAT, Dahono Web Ingress, direct port reachability, and firewall behavior before considering the deployment fully security-reviewed. Do not change the binding without verifying the ingress path.

## 4. Verification Results

Observed on 2026-10-12:

- `docker compose config -q`: passed.
- Container `router`: running.
- `https://router.octalectzz.my.id/api/health`: returned `{"ok":true}`.
- HTTPS login page: returned HTTP 200 in prior checks.
- Dashboard login: user confirmed successful login and password change.
- Persistent SQLite database observed at `/opt/octa/data/router/db/data.sqlite`.
- `.env` is ignored by Git.
- `.env` permissions: `600`.
- `.env.example` contains placeholders, not actual secrets.

## 5. Data Backup

A data archive was created while the router container was stopped:

- File: `/opt/octa/backups/router-data-20261012-084444.tar.gz`
- Reported size: 138 KB
- Archive listing test: passed.
- Application health check after restart: passed.

This is a local backup only. It is not an off-site backup and has not been restored in a staging environment.

## 6. Git

- Repository: https://github.com/OctaLectzz/octa-hub-infrastructure
- Branch: `main`
- Commit: `f5d7891` — `chore(router): add Docker Compose configuration`
- Files committed:
  - `stacks/router/compose.yaml`
  - `stacks/router/.env.example`
- Push succeeded; last observed status was synchronized with `origin/main`.

## 7. Remaining Work

- Review direct exposure of port 20128 and confirm Dahono ingress requirements.
- Reconcile the dashboard's `0.5.99` notice with tags published by the official registry.
- Consider a container health check only if supported by official guidance and the image.
- Test backup restoration before relying on this archive for recovery.

Do not mark the installation fully closed until outstanding security and version checks are either resolved or explicitly accepted.
