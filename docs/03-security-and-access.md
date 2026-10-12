# 03 — Security and Access Controls

**Status:** Security policy documented; 9Router and Hermes deployed; security reviews remain open
**Last updated:** 2026-10-12

## 1. SSH

- VPS endpoint: `<SSH_PUBLIC_IP>:<SSH_FORWARD_PORT>`, forwarded to internal port 22.
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

### Observed State

- Dahono Web Ingress serves the Hermes dashboard at `https://hermes.octalectzz.my.id`, and public HTTPS access was verified.
- Hermes dashboard login was verified with Nous OAuth and Basic Auth.
- The Hermes dashboard port `9119` is published by Docker on `0.0.0.0` and `[::]`, so it is not restricted to loopback at the Docker publishing layer.
- A Windows external TCP test to port `9119` failed. This result alone does not establish whether the port is reachable from every external network.
- UFW was inactive during the Hermes audit. nftables and iptables inspection showed permissive host policies, and the Docker `DOCKER-USER` chain was empty at the time of inspection.
- Hermes API port `8642` is not published as a host port. However, Hermes and 9Router share the external Docker network `octa-hub`, so container-to-container access must be considered separately.
- The Hermes API authentication test to `/v1/models` without credentials returned HTTP `401`.
- TLS verification for the public Hermes HTTPS endpoint succeeded.

### Outstanding Verification

- Verify Dahono Web Ingress upstream targets, source addresses, port requirements, and forwarding behavior.
- Determine whether direct access to published port `9119` can be restricted without breaking the provider ingress.
- Test external reachability from additional networks where appropriate.
- Review the public dashboard authentication policy and trusted-proxy settings against the official Hermes documentation.
- Review API network access and terminal backend isolation before attaching additional services to `octa-hub`.
- Recheck host firewall and Docker networking rules before making any network or exposure changes.

### Operational Rules

- Do not assume UFW alone prevents access to Docker-published ports.
- Do not expose internal service ports without a documented requirement and security review.
- Do not add another reverse proxy until the existing Dahono Web Ingress behavior is understood.
- Do not change firewall rules or published ports solely on the basis of an inconclusive external connectivity test.
- Keep this section aligned with the detailed findings in `docs/11-hermes-security.md`.

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
