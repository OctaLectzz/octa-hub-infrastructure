# 02 — Backup and Restore Policy

**Status:** Policy agreed; implementation not started  
**Last updated:** 2026-10-12

## 1. Agreed Policy

- Schedule: daily at **05:00 WIB (`Asia/Jakarta`)**.
- Destinations: Cloudflare R2 and Dahono S3.
- Buckets: private.
- Encryption: client-side encryption; the encryption key is managed separately from the backup.
- Retention: at most **three valid daily backup generations per destination**.
- Delete an older generation only after a new generation has uploaded successfully and been verified at the relevant destination.
- If a backup fails, do not delete the last valid backup.
- Test restoration in staging; do not overwrite the active system during restore testing.
- Configure the first automated backup after all applications have been installed, per the user's decision.

## 2. Scope

Back up required persistent data, relevant configuration, databases, the Obsidian vault, and recovery metadata. Exclude reproducible cache only after documenting the decision. Use consistent database backup mechanisms rather than copying live database directories blindly.

## 3. Candidate Tooling

Restic remains a candidate, not a final decision. Test:
- Cloudflare R2 S3 endpoint and authentication.
- Dahono S3 endpoint and authentication.
- Backup, integrity checking, download, and restore.
- Three-generation retention.
- Partial destination failure handling.
- Local staging disk requirements.

## 4. Keys and Secrets

- Do not keep the only encryption/recovery key on the VPS being backed up.
- Store recovery material securely outside the VPS.
- Never commit storage credentials, passwords, API keys, encryption keys, or private keys.
- Define recovery-key ownership and access procedures before enabling automated backups.

## 5. Valid Backup Criteria

1. Source snapshot is consistent.
2. Upload to the destination succeeds.
3. Repository/snapshot integrity can be verified.
4. Generation metadata is updated safely.
5. Retention runs only after a new valid generation exists.
6. A staging restore succeeds on the defined test schedule.

## 6. Scheduling and Monitoring

A systemd timer is the preferred primary scheduler so backup execution does not depend on Hermes or n8n. Hermes may report status and help troubleshoot but must not be the sole backup controller.

## 7. Open Items

- Verify Cloudflare R2 capacity and usage.
- Verify Dahono S3 plan, capacity, endpoint, API compatibility, and credentials.
- Measure actual persistent-data size and local staging needs.
- Verify Dahono `Backup to KVM` coverage, retention, pricing, and restore behavior.
- Select and test the backup engine.
- Define consistent database backup and partial-failure handling.
- Define periodic restore testing.
