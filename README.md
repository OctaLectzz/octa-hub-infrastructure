
# Octa Hub Infrastructure

Infrastructure repository for managing the Octa Hub self-hosted services.

## Services

| Service | Internal Directory | Public URL |
|---|---|---|
| 9router | `stacks/router/` | https://router.octalectzz.my.id |
| Hermes | `stacks/hermes/` | https://hermes.octalectzz.my.id |
| n8n | `stacks/n8n/` | https://n8n.octalectzz.my.id |
| Obsidian | `stacks/obsidian/` | https://obsidian.octalectzz.my.id |
| Octa Hub | `stacks/octa-hub/` | https://hub.octalectzz.my.id |

## Repository Structure

- `stacks/`: Docker Compose files and environment templates.
- `data/`: Persistent application data; never commit this directory.
- `backups/`: Local backup and recovery artifacts; never commit these files.
- `logs/`: Operational logs; never commit these files.
- `docs/architecture/`: Architecture documentation and design decisions.
- `docs/runbooks/`: Installation, maintenance, and recovery procedures.
- `docs/changelog/`: Infrastructure change records.

## Environment Configuration

Each service has an `.env.example` file containing its documented configuration variables.

To configure a service:

1. Navigate to its directory under `stacks/`.
2. Copy `.env.example` to `.env`.
3. Replace all placeholders with valid values.
4. Restrict access to the `.env` file.
5. Validate the configuration before starting the service.

Example:

```bash
cd /opt/octa/stacks/n8n
cp .env.example .env
chmod 600 .env
```

Do not commit `.env` files or disclose their contents.

Environment variable names and required values must follow the official documentation for the corresponding application.

## Git Workflow

Review changes before committing:

```bash
git status
git diff
git diff --cached
```

Stage and commit approved changes:

```bash
git add .gitignore README.md stacks docs
git diff --cached
git commit -m "docs: initialize infrastructure repository"
```

Never use `git add -f` to force sensitive files into the repository.

## Security Requirements

- Never commit passwords, API tokens, encryption keys, or private certificates.
- Keep persistent application data outside version control.
- Review every staged file before committing.
- Use separate credentials for individual services whenever supported.
- Follow official installation and security documentation for each service.
- Test recovery procedures before relying on backups.
