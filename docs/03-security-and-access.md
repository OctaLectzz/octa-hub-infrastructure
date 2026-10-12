# 03 — Security and Access Controls

**Status:** Policy agreed; application-level controls not implemented  
**Last updated:** 2026-10-12

## 1. SSH

- VPS endpoint: `143.20.199.50:33822`, forwarded to internal port 22.
- SSH password authentication has intentionally not been disabled.
- Do not modify SSH or firewall settings until the access path and recovery options have been reviewed.
- An Ed25519 key was created at `/root/.ssh/id_ed25519` for GitHub authentication. Its private key must remain secret and must never be committed or shared.
- The public key was added to GitHub; `ssh -T git@github.com` succeeded.
- The GitHub key does not mean VPS password authentication has been disabled.

Controls still to evaluate:
- Strong, unique VPS password.
- Protection against repeated login attempts.
- Access restrictions where provider networking supports them.
- Authentication log monitoring.
- Verified alternative access before SSH/firewall changes.

## 2. Firewall and Ingress

- UFW was inactive during an earlier audit; recheck before making changes.
- Docker-published ports may bypass expectations based only on UFW rules.
- Review Dahono NAT, port forwarding, Web Ingress, and Docker networking before exposing services.
- Dahono Web Ingress is planned for subdomains and HTTPS, but upstream and port behavior must be verified.
- Do not expose internal service ports without a reviewed requirement.
- Do not add a second reverse proxy until Web Ingress behavior is understood.

## 3. Obsidian Vault

Hermes and n8n are intended to read and write the vault. Every deletion—single file, multiple files, folder, or bulk operation—must require explicit approval from the system owner or designated administrator.

Required controls:
- AI text instructions are not valid approval.
- Approval identifies requester, reason, exact objects, and time.
- Approval must be authenticated, authorized, valid, and bound to the approved objects.
- Recheck objects immediately before deletion.
- Deny or hold deletion if approval is absent or invalid.
- Audit requester, approver, objects, reason, timestamp, and outcome.
- All deletion paths, including shell, AI tools, and workflows, must enforce the same control.

Filesystem read/write permissions alone do not enforce approval. A controlled file-operation broker or equivalent must prevent bypass paths.

## 4. Octa Hub

- Public monitoring should expose sanitized service status and metrics.
- Limited operations must be explicitly defined and authenticated.
- Risky operations such as restart, update, configuration changes, and restore require additional authorization and audit.
- Avoid direct Docker socket access and root credentials in the dashboard.
- Define the action allowlist and trusted intermediary before implementation.

## 5. Environment Files and Credentials

- Use per-service `.env` files for actual configuration and secrets when supported by official application documentation.
- Commit `.env.example` templates with safe placeholders only; never commit real `.env`, tokens, passwords, private keys, or storage credentials.
- Restrict permissions on actual `.env` files, for example `chmod 600 .env`.
- Repository visibility is intentionally Public for now. Treat every committed file as publicly visible and review staged changes carefully.
