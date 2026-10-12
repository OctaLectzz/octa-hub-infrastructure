# 03 — Security and Access Controls

**Status:** Policy agreed; application-level controls not implemented  
**Last updated:** 2026-10-12

## 1. SSH

- The VPS is accessed through Dahono's NAT endpoint: `143.20.199.50:33822`, forwarded to internal port 22.
- SSH password authentication has intentionally not been disabled.
- Do not modify SSH or firewall settings until the access path and recovery options have been reviewed.
- The user created an Ed25519 key at `/root/.ssh/id_ed25519` for GitHub authentication. The private key must remain secret and must never be committed or shared.
- The public key was added to GitHub, and `ssh -T git@github.com` succeeded.
- This GitHub deploy/authentication key does not mean SSH password authentication for VPS login has been disabled.

Controls still to evaluate:
- Strong, unique VPS password.
- Protection against repeated login attempts.
- Access restrictions where provider networking supports them.
- Authentication log monitoring.
- Verified alternative access before SSH/firewall changes.

## 2. Firewall and Ingress

- UFW was inactive during the earlier audit; current state should be rechecked before changes.
- Docker-published ports may bypass expectations based only on UFW rules.
- Review Dahono NAT, port forwarding, Web Ingress, and Docker networking before exposing any service.
- Dahono Web Ingress is planned for subdomains and HTTPS, but upstream and port behavior must be verified.
- Do not expose internal service ports without a reviewed requirement.
- Do not add a second reverse proxy until the Web Ingress behavior is understood.

## 3. Obsidian Vault

Hermes and n8n are intended to read and write the vault. All delete operations—single-file, multi-file, folder, or bulk deletion—must require explicit approval from the system owner or designated administrator.

Controls required:
- AI text instructions are not valid approval.
- Approval identifies the requester, reason, exact objects, and time.
- Approval must be authenticated, authorized, valid, and bound to the approved objects.
- Recheck objects immediately before deletion.
- Deny or hold deletion if approval is absent or invalid.
- Audit requester, approver, objects, reason, timestamp, and outcome.
- All deletion paths, including shell, AI tools, and workflows, must enforce the same control.

Filesystem read/write permissions alone do not enforce approval. A controlled file-operation broker or equivalent mechanism must prevent bypass paths.

## 4. Octa Hub

- Public monitoring should expose sanitized service status and metrics.
- Limited operations must be explicitly defined and authenticated.
- Risky operations such as restart, update, configuration changes, and restore require additional authorization and audit.
- Avoid direct Docker socket access and root credentials in the dashboard.
- Define the action allowlist and trusted intermediary before implementation.

## 5. Environment Files and Credentials

- Real `.env` files are intended to be used per service, in accordance with the official application's supported environment variables.
- Commit `.env.example` templates only; never commit real `.env`, tokens, passwords, private keys, or storage credentials.
- File permissions should be restrictive, for example `chmod 600 .env`.
- Repository visibility is intentionally Public for now, per user decision. Treat all committed content as publicly visible and review every staged change carefully.
