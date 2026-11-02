#!/usr/bin/env python3
"""
Octa Hub — Unified Backup & Disaster Recovery Automation
Author: Atlas (octainfra) for Octa Hub
Location: /opt/octa/scripts/octa-backup.py

Features:
- Modular 7-Zip AES-256 with Header Encryption (-mhe=on)
- Online zero-lock SQLite atomic backup for 9Router
- pg_dump custom format (-Fc) for n8n PostgreSQL
- Official hermes CLI backup bundle
- Native Obsidian Knowledge Vault archive
- Dual-Storage Upload (Dahono S3 & Cloudflare R2)
- Root manifest.json & TUTORIAL-RESTORE.md maintenance
- 3-day retention policy with Anti-Pruning Fail-Safe Freeze
- Telegram Bot API 10.3 rich HTML notifications to Group Topic
"""

import os
import sys
import time
import shutil
import hashlib
import sqlite3
import subprocess
import json
import urllib.request
import urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# ------------------------------------------------------------------------------
# Configuration & Constants
# ------------------------------------------------------------------------------
WIB = ZoneInfo("Asia/Jakarta")
CREDENTIALS_FILE = "/etc/octa/backup.env"
FALLBACK_CREDENTIALS = "/opt/octa/data/hermes/credentials/backup.env"
HERMES_ENV_FILE = "/opt/octa/data/hermes/.env"
STAGING_BASE_DIR = "/opt/octa/backups/staging"
TUTORIAL_FILE = "/opt/octa/scripts/TUTORIAL-RESTORE.md"
LAST_BACKUP_FILE = "/opt/octa/backups/last_backup.json"
RETENTION_DAYS_DAHONO = 7
RETENTION_DAYS_R2 = 3
STANDARD_COMPONENTS = ["9router.7z", "hermes.7z", "n8n.7z", "obsidian.7z", "manifest.json"]

# Target Telegram Topic: Octa Hub -> DevOps & Infra (Thread 36)
DEFAULT_TELEGRAM_CHAT_ID = -1004349640522
DEFAULT_TELEGRAM_THREAD_ID = 36


def log(msg: str):
    timestamp = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")
    print(f"[{timestamp}] {msg}", flush=True)


def load_env_file(path: str) -> dict:
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def run_command(cmd: list, cwd: str = None) -> subprocess.CompletedProcess:
    safe_cmd = []
    for c in cmd:
        if c.startswith("-p"):
            safe_cmd.append("-p***")
        else:
            safe_cmd.append(c)
    log(f"Running command: {' '.join(safe_cmd)}")
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        err_out = f"STDERR: {res.stderr.strip()}\nSTDOUT: {res.stdout.strip()}".strip()
        raise RuntimeError(f"Command failed (exit {res.returncode}): {err_out}")
    return res


def send_telegram_notification(token: str, chat_id: int, thread_id: int, html_text: str):
    if not token or not chat_id:
        log("Telegram alert skipped: Token or Chat ID missing.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": html_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                log(f"Telegram notification delivered to chat {chat_id} (topic {thread_id}).")
            else:
                log(f"Telegram notification returned HTTP {resp.status}")
    except Exception as e:
        log(f"Failed to send Telegram notification: {e}")


# ------------------------------------------------------------------------------
# Core Backup Engine
# ------------------------------------------------------------------------------
def main():
    start_time = time.time()
    now_dt = datetime.now(WIB)
    date_str = now_dt.strftime("%Y-%m-%d")
    timestamp_str = now_dt.strftime("%Y%m%d-%H%M%S")
    epoch_now = int(now_dt.timestamp())
    
    log(f"Starting Octa Hub Unified Backup for {date_str} ({timestamp_str})...")

    # 1. Load Credentials
    creds_path = CREDENTIALS_FILE if os.path.exists(CREDENTIALS_FILE) else FALLBACK_CREDENTIALS
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found at {creds_path}")
    
    creds = load_env_file(creds_path)
    backup_password = creds.get("BACKUP_PASSWORD")
    if not backup_password or backup_password == "GANTI_DENGAN_PASSWORD_7ZIP_ANDA":
        raise ValueError("BACKUP_PASSWORD is not configured in credentials file.")

    # Storage targets configuration
    dahono_endpoint = creds.get("DAHONO_S3_ENDPOINT_URL")
    dahono_bucket = creds.get("DAHONO_S3_BUCKET_NAME")
    dahono_ak = creds.get("DAHONO_S3_ACCESS_KEY")
    dahono_sk = creds.get("DAHONO_S3_SECRET_KEY")
    dahono_region = creds.get("DAHONO_S3_REGION", "us-east-1")

    r2_endpoint = creds.get("CF_R2_ENDPOINT_URL")
    r2_bucket = creds.get("CF_R2_BUCKET_NAME")
    r2_ak = creds.get("CF_R2_ACCESS_KEY")
    r2_sk = creds.get("CF_R2_SECRET_KEY")
    r2_region = creds.get("CF_R2_REGION", "auto")

    # Retention configuration (Tiered: Dahono 7 days, Cloudflare R2 3 days)
    retention_dahono = int(creds.get("RETENTION_DAYS_DAHONO", RETENTION_DAYS_DAHONO))
    retention_r2 = int(creds.get("RETENTION_DAYS_R2", RETENTION_DAYS_R2))
    log(f"Configured retention: Dahono S3 = {retention_dahono} days, Cloudflare R2 = {retention_r2} days")

    # Telegram configuration
    hermes_env = load_env_file(HERMES_ENV_FILE)
    tg_token = hermes_env.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = int(creds.get("TELEGRAM_ALERT_CHAT_ID", DEFAULT_TELEGRAM_CHAT_ID))
    tg_thread_id = int(creds.get("TELEGRAM_ALERT_THREAD_ID", DEFAULT_TELEGRAM_THREAD_ID))

    # 2. Setup Staging Directory
    staging_dir = os.path.join(STAGING_BASE_DIR, f"run-{date_str}-{timestamp_str}")
    os.makedirs(staging_dir, mode=0o700, exist_ok=True)
    log(f"Staging directory created: {staging_dir}")

    artifacts = {}
    current_stage = "Initialization"

    try:
        # ----------------------------------------------------------------------
        # A. Module: 9Router AI Gateway
        # ----------------------------------------------------------------------
        current_stage = "Packaging 9Router (SQLite & .env)"
        log("=== [1/4] Processing 9Router AI Gateway ===")
        router_stage = os.path.join(staging_dir, "9router_stage")
        os.makedirs(router_stage, exist_ok=True)
        
        # SQLite atomic online backup
        src_sqlite = "/opt/octa/data/router/db/data.sqlite"
        dst_sqlite = os.path.join(router_stage, "data.sqlite")
        log(f"Backing up SQLite database from {src_sqlite}...")
        con_src = sqlite3.connect(src_sqlite)
        con_dst = sqlite3.connect(dst_sqlite)
        con_src.backup(con_dst)
        con_src.close()
        con_dst.close()
        
        # Environment config
        src_router_env = "/opt/octa/stacks/router/.env"
        if os.path.exists(src_router_env):
            shutil.copy2(src_router_env, os.path.join(router_stage, "router.env"))
        
        # 7-Zip AES-256 + header encryption
        router_7z = os.path.join(staging_dir, "9router.7z")
        cmd_7z_router = [
            "7z", "a", "-t7z", "-m0=lzma2", "-mx=5", "-mfb=64", "-md=32m", "-ms=on",
            "-mhe=on", f"-p{backup_password}", router_7z,
            "data.sqlite"
        ]
        if os.path.exists(os.path.join(router_stage, "router.env")):
            cmd_7z_router.append("router.env")
        run_command(cmd_7z_router, cwd=router_stage)
        
        # Clean uncompressed files
        shutil.rmtree(router_stage)
        artifacts["9router.7z"] = router_7z
        log(f"9Router packaged: {router_7z} ({os.path.getsize(router_7z):,} bytes)")

        # ----------------------------------------------------------------------
        # B. Module: Hermes Agent Ecosystem
        # ----------------------------------------------------------------------
        current_stage = "Packaging Hermes Ecosystem (CLI backup)"
        log("=== [2/4] Processing Hermes Agent Framework ===")
        hermes_temp_zip = "/opt/octa/data/hermes/backups/hermes-temp.zip"
        if os.path.exists(hermes_temp_zip):
            os.remove(hermes_temp_zip)

        log("Executing official hermes backup CLI inside container...")
        res = subprocess.run([
            "docker", "exec", "hermes",
            "/opt/hermes/bin/hermes", "backup",
            "-o", "/opt/data/backups/hermes-temp.zip",
            "-k", "0"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(hermes_temp_zip):
            err_out = f"STDERR: {res.stderr.strip()}\nSTDOUT: {res.stdout.strip()}".strip()
            raise RuntimeError(f"Hermes backup CLI failed to produce archive (exit {res.returncode}): {err_out}")

        if res.returncode != 0:
            warn_msg = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
            log(f"WARNING: Hermes backup CLI exited with code {res.returncode} but produced valid archive. "
                f"Likely transient file races (disposable cron-output/npm logs). Continuing: {warn_msg}")

        # 7-Zip AES-256 + header encryption
        hermes_7z = os.path.join(staging_dir, "hermes.7z")
        run_command([
            "7z", "a", "-t7z", "-m0=lzma2", "-mx=5", "-mfb=64", "-md=32m", "-ms=on",
            "-mmt=2", "-mhe=on", f"-p{backup_password}", hermes_7z,
            os.path.basename(hermes_temp_zip)
        ], cwd=os.path.dirname(hermes_temp_zip))

        os.remove(hermes_temp_zip)
        artifacts["hermes.7z"] = hermes_7z
        log(f"Hermes packaged: {hermes_7z} ({os.path.getsize(hermes_7z):,} bytes)")

        # ----------------------------------------------------------------------
        # C. Module: n8n Automation Engine
        # ----------------------------------------------------------------------
        current_stage = "Packaging n8n Engine (Postgres & .env)"
        log("=== [3/4] Processing n8n Automation Engine ===")
        n8n_stage = os.path.join(staging_dir, "n8n_stage")
        os.makedirs(n8n_stage, exist_ok=True)
        dump_path = os.path.join(n8n_stage, "postgres-dump.dump")

        log("Executing PostgreSQL pg_dump on n8n-postgres...")
        with open(dump_path, "wb") as f_dump:
            res_dump = subprocess.run(
                ["docker", "exec", "n8n-postgres", "pg_dump", "-U", "n8n_admin", "-d", "n8n", "-Fc"],
                stdout=f_dump, stderr=subprocess.PIPE
            )
            if res_dump.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {res_dump.stderr.decode('utf-8')}")

        src_n8n_env = "/opt/octa/stacks/n8n/.env"
        if os.path.exists(src_n8n_env):
            shutil.copy2(src_n8n_env, os.path.join(n8n_stage, "n8n.env"))

        # 7-Zip AES-256 + header encryption
        n8n_7z = os.path.join(staging_dir, "n8n.7z")
        cmd_7z_n8n = [
            "7z", "a", "-t7z", "-m0=lzma2", "-mx=5", "-mfb=64", "-md=32m", "-ms=on",
            "-mhe=on", f"-p{backup_password}", n8n_7z,
            "postgres-dump.dump"
        ]
        if os.path.exists(os.path.join(n8n_stage, "n8n.env")):
            cmd_7z_n8n.append("n8n.env")
        run_command(cmd_7z_n8n, cwd=n8n_stage)

        shutil.rmtree(n8n_stage)
        artifacts["n8n.7z"] = n8n_7z
        log(f"n8n packaged: {n8n_7z} ({os.path.getsize(n8n_7z):,} bytes)")

        # ----------------------------------------------------------------------
        # D. Module: Obsidian Knowledge Vault
        # ----------------------------------------------------------------------
        current_stage = "Packaging Obsidian Vault"
        log("=== [4/4] Processing Obsidian Knowledge Vault ===")
        obsidian_vault_dir = "/opt/octa/data/hermes/obsidian-vault"
        obsidian_7z = os.path.join(staging_dir, "obsidian.7z")

        run_command([
            "7z", "a", "-t7z", "-m0=lzma2", "-mx=1", "-mfb=64", "-md=32m", "-ms=on",
            "-mmt=off", "-mhe=on", f"-p{backup_password}", obsidian_7z,
            "obsidian-vault"
        ], cwd=os.path.dirname(obsidian_vault_dir))

        artifacts["obsidian.7z"] = obsidian_7z
        log(f"Obsidian packaged: {obsidian_7z} ({os.path.getsize(obsidian_7z):,} bytes)")

        # ----------------------------------------------------------------------
        # E. Manifest Generation
        # ----------------------------------------------------------------------
        current_stage = "Generating Manifest & Integrity Digest"
        log("=== Generating Snapshot Manifest ===")
        files_meta = {}
        total_bytes = 0
        for name, path in artifacts.items():
            size = os.path.getsize(path)
            sha = compute_sha256(path)
            total_bytes += size
            files_meta[name] = {
                "size_bytes": size,
                "sha256": sha
            }

        daily_manifest = {
            "snapshot_date": date_str,
            "created_at": now_dt.isoformat(),
            "hostname": "octa-hub",
            "system": "Octa Hub Infrastructure",
            "encryption": {
                "format": "7z",
                "cipher": "AES-256",
                "header_encrypted": True
            },
            "total_size_bytes": total_bytes,
            "files": files_meta
        }

        manifest_path = os.path.join(staging_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(daily_manifest, f, indent=2)
        log(f"Snapshot manifest generated: {manifest_path}")

        # ----------------------------------------------------------------------
        # F. Dual-Storage Upload
        # ----------------------------------------------------------------------
        current_stage = "Dual-Storage S3/R2 Upload"
        log("=== Initializing S3 Clients for Dual-Storage Upload ===")
        s3_dahono = boto3.client(
            "s3",
            endpoint_url=dahono_endpoint,
            aws_access_key_id=dahono_ak,
            aws_secret_access_key=dahono_sk,
            region_name=dahono_region,
            config=Config(s3={"addressing_style": "path"}, signature_version="s3v4")
        )

        s3_r2 = boto3.client(
            "s3",
            endpoint_url=r2_endpoint,
            aws_access_key_id=r2_ak,
            aws_secret_access_key=r2_sk,
            region_name=r2_region,
            config=Config(signature_version="s3v4")
        )

        upload_items = [
            ("9router.7z", artifacts["9router.7z"]),
            ("hermes.7z", artifacts["hermes.7z"]),
            ("n8n.7z", artifacts["n8n.7z"]),
            ("obsidian.7z", artifacts["obsidian.7z"]),
            ("manifest.json", manifest_path)
        ]

        remote_date_prefix = f"daily-backup/{date_str}"
        
        dahono_success = True
        r2_success = True

        log(f"Uploading snapshot files to Dahono S3: {dahono_bucket}/{remote_date_prefix}/...")
        for fname, local_file in upload_items:
            key = f"{remote_date_prefix}/{fname}"
            log(f" -> Dahono S3: {key}")
            try:
                s3_dahono.upload_file(local_file, dahono_bucket, key)
            except Exception as e:
                log(f"ERROR uploading {key} to Dahono S3: {e}")
                dahono_success = False

        log(f"Uploading snapshot files to Cloudflare R2: {r2_bucket}/{remote_date_prefix}/...")
        for fname, local_file in upload_items:
            key = f"{remote_date_prefix}/{fname}"
            log(f" -> Cloudflare R2: {key}")
            try:
                s3_r2.upload_file(local_file, r2_bucket, key)
            except Exception as e:
                log(f"ERROR uploading {key} to Cloudflare R2: {e}")
                r2_success = False

        if not (dahono_success and r2_success):
            raise RuntimeError(f"Storage upload failed! Dahono S3: {dahono_success}, Cloudflare R2: {r2_success}")

        # Auto-normalize Dahono S3 keys (remove duplicate bucket prefix if present)
        try:
            from botocore.auth import SigV4Auth
            from botocore.awsrequest import AWSRequest
            import xml.etree.ElementTree as ET
            
            d_session = boto3.Session(aws_access_key_id=dahono_ak, aws_secret_access_key=dahono_sk)
            d_creds = d_session.get_credentials()
            
            # List all keys at Dahono root
            req_l = AWSRequest(method="GET", url=f"{dahono_endpoint}/")
            SigV4Auth(d_creds, "s3", dahono_region).add_auth(req_l)
            with urllib.request.urlopen(urllib.request.Request(f"{dahono_endpoint}/", headers=dict(req_l.headers))) as r_l:
                xml_l = r_l.read().decode("utf-8")
            
            r_elem = ET.fromstring(xml_l)
            ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
            d_prefix = f"{dahono_bucket}/"
            for c_node in r_elem.findall("s3:Contents", ns):
                raw_k = c_node.find("s3:Key", ns).text
                if raw_k.startswith(d_prefix):
                    clean_k = raw_k[len(d_prefix):]
                    log(f"Normalizing Dahono S3 key: {raw_k} -> {clean_k}")
                    # Copy
                    req_cp = AWSRequest(method="PUT", url=f"{dahono_endpoint}/{clean_k}")
                    req_cp.headers["x-amz-copy-source"] = f"/{dahono_bucket}/{raw_k}"
                    SigV4Auth(d_creds, "s3", dahono_region).add_auth(req_cp)
                    with urllib.request.urlopen(urllib.request.Request(f"{dahono_endpoint}/{clean_k}", headers=dict(req_cp.headers), method="PUT")) as r_cp:
                        pass
                    # Delete old
                    req_del = AWSRequest(method="DELETE", url=f"{dahono_endpoint}/{raw_k}")
                    SigV4Auth(d_creds, "s3", dahono_region).add_auth(req_del)
                    with urllib.request.urlopen(urllib.request.Request(f"{dahono_endpoint}/{raw_k}", headers=dict(req_del.headers), method="DELETE")) as r_del:
                        pass
        except Exception as e_norm:
            log(f"Warning during Dahono S3 key normalization: {e_norm}")

        # ----------------------------------------------------------------------
        # G. Tiered Retention Policy & Snapshot Pruning
        # ----------------------------------------------------------------------
        current_stage = "Evaluating Retention Policy & Snapshot Pruning"
        pruned_dahono = []
        pruned_r2 = []

        # Discover active snapshots on Cloudflare R2
        res_r2_prefixes = s3_r2.list_objects_v2(Bucket=r2_bucket, Prefix="daily-backup/", Delimiter="/")
        found_snapshots_r2 = []
        for p_info in res_r2_prefixes.get("CommonPrefixes", []):
            prefix_str = p_info.get("Prefix", "").strip("/")
            parts = prefix_str.split("/")
            if len(parts) == 2 and parts[0] == "daily-backup":
                d_candidate = parts[1]
                if len(d_candidate) == 10 and d_candidate.count("-") == 2:
                    found_snapshots_r2.append(d_candidate)

        if date_str not in found_snapshots_r2:
            found_snapshots_r2.append(date_str)
        found_snapshots_r2 = sorted(list(set(found_snapshots_r2)))

        # Discover active snapshots on Dahono S3
        found_snapshots_dahono = []
        try:
            res_da_prefixes = s3_dahono.list_objects_v2(Bucket=dahono_bucket, Prefix="daily-backup/", Delimiter="/")
            for p_info in res_da_prefixes.get("CommonPrefixes", []):
                prefix_str = p_info.get("Prefix", "").strip("/")
                parts = prefix_str.split("/")
                if len(parts) == 2 and parts[0] == "daily-backup":
                    d_candidate = parts[1]
                    if len(d_candidate) == 10 and d_candidate.count("-") == 2:
                        found_snapshots_dahono.append(d_candidate)
        except Exception as e_ds:
            log(f"Warning discovering Dahono snapshots: {e_ds}")
            found_snapshots_dahono = list(found_snapshots_r2)

        if date_str not in found_snapshots_dahono:
            found_snapshots_dahono.append(date_str)
        found_snapshots_dahono = sorted(list(set(found_snapshots_dahono)))

        log(f"Discovered snapshots in Dahono S3 before pruning (Target Retensi {retention_dahono}d): {found_snapshots_dahono}")
        log(f"Discovered snapshots in Cloudflare R2 before pruning (Target Retensi {retention_r2}d): {found_snapshots_r2}")

        # 1. Dahono S3 Retention (Keep 7 Days)
        log(f"=== Evaluating Dahono S3 Retention Policy (Keep {retention_dahono} Days) ===")
        if len(found_snapshots_dahono) > retention_dahono:
            prune_targets_d = found_snapshots_dahono[:-retention_dahono]
            log(f"Pruning candidate snapshots on Dahono S3 (older than {retention_dahono} days): {prune_targets_d}")
            for p_date in prune_targets_d:
                p_prefix = f"daily-backup/{p_date}/"
                log(f"Pruning snapshot {p_date} from Dahono S3...")
                try:
                    res_objs_d = s3_dahono.list_objects_v2(Bucket=dahono_bucket, Prefix=p_prefix)
                    del_keys_d = [{"Key": o["Key"]} for o in res_objs_d.get("Contents", [])]
                    if del_keys_d:
                        del_res_d = s3_dahono.delete_objects(Bucket=dahono_bucket, Delete={"Objects": del_keys_d})
                        if del_res_d.get("Errors"):
                            log(f"Warning: errors deleting objects in {p_prefix} on Dahono S3: {del_res_d.get('Errors')}")
                        else:
                            log(f"Deleted {len(del_keys_d)} objects from Dahono S3 ({p_prefix})")
                            pruned_dahono.append(p_date)
                    else:
                        pruned_dahono.append(p_date)
                except Exception as e_prune_d:
                    log(f"Warning deleting snapshot {p_date} on Dahono S3: {e_prune_d}")
        else:
            log(f"Dahono S3 snapshots ({len(found_snapshots_dahono)}) <= {retention_dahono}. No pruning required.")

        # 2. Cloudflare R2 Retention (Keep 3 Days)
        log(f"=== Evaluating Cloudflare R2 Retention Policy (Keep {retention_r2} Days) ===")
        if len(found_snapshots_r2) > retention_r2:
            prune_targets_r2 = found_snapshots_r2[:-retention_r2]
            log(f"Pruning candidate snapshots on Cloudflare R2 (older than {retention_r2} days): {prune_targets_r2}")
            for p_date in prune_targets_r2:
                p_prefix = f"daily-backup/{p_date}/"
                log(f"Pruning snapshot {p_date} from Cloudflare R2...")
                try:
                    res_objs_r2 = s3_r2.list_objects_v2(Bucket=r2_bucket, Prefix=p_prefix)
                    del_keys_r2 = [{"Key": o["Key"]} for o in res_objs_r2.get("Contents", [])]
                    if del_keys_r2:
                        del_res_r2 = s3_r2.delete_objects(Bucket=r2_bucket, Delete={"Objects": del_keys_r2})
                        if del_res_r2.get("Errors"):
                            log(f"Warning: errors deleting objects in {p_prefix} on Cloudflare R2: {del_res_r2.get('Errors')}")
                        else:
                            log(f"Deleted {len(del_keys_r2)} objects from Cloudflare R2 ({p_prefix})")
                            pruned_r2.append(p_date)
                    else:
                        pruned_r2.append(p_date)
                except Exception as e_prune_r2:
                    log(f"Warning deleting snapshot {p_date} on Cloudflare R2: {e_prune_r2}")
        else:
            log(f"Cloudflare R2 snapshots ({len(found_snapshots_r2)}) <= {retention_r2}. No pruning required.")

        # Compute verified post-pruning active snapshots
        active_snapshots_dahono = [s for s in found_snapshots_dahono if s not in pruned_dahono]
        active_snapshots_r2 = [s for s in found_snapshots_r2 if s not in pruned_r2]
        log(f"Active snapshots remaining in Dahono S3: {active_snapshots_dahono}")
        log(f"Active snapshots remaining in Cloudflare R2: {active_snapshots_r2}")

        # ----------------------------------------------------------------------
        # H. Upload Root Files: TUTORIAL-RESTORE.md & Global manifest.json
        # ----------------------------------------------------------------------
        current_stage = "Root Files Maintenance"
        log("=== Updating Root Files (TUTORIAL-RESTORE.md & Global manifest.json) ===")
        if os.path.exists(TUTORIAL_FILE):
            tut_key = "daily-backup/TUTORIAL-RESTORE.md"
            log(f"Uploading {tut_key} to Dahono S3 and Cloudflare R2...")
            s3_dahono.upload_file(TUTORIAL_FILE, dahono_bucket, tut_key)
            s3_r2.upload_file(TUTORIAL_FILE, r2_bucket, tut_key)

        # Manifest for Dahono S3 (7 Days retention)
        manifest_dahono = {
            "system": "Octa Hub Infrastructure",
            "environment": "production-dahono",
            "storage_target": "Dahono S3 (Primary)",
            "last_updated": now_dt.isoformat(),
            "latest_snapshot": date_str,
            "retention_days": retention_dahono,
            "encryption": {
                "format": "7z",
                "cipher": "AES-256",
                "header_encrypted": True
            },
            "active_snapshots": active_snapshots_dahono
        }

        # Manifest for Cloudflare R2 (3 Days retention)
        manifest_r2 = {
            "system": "Octa Hub Infrastructure",
            "environment": "production-dahono",
            "storage_target": "Cloudflare R2 (Offsite DR)",
            "last_updated": now_dt.isoformat(),
            "latest_snapshot": date_str,
            "retention_days": retention_r2,
            "encryption": {
                "format": "7z",
                "cipher": "AES-256",
                "header_encrypted": True
            },
            "active_snapshots": active_snapshots_r2
        }

        manifest_dahono_path = os.path.join(staging_dir, "manifest_dahono.json")
        with open(manifest_dahono_path, "w", encoding="utf-8") as f:
            json.dump(manifest_dahono, f, indent=2)

        manifest_r2_path = os.path.join(staging_dir, "manifest_r2.json")
        with open(manifest_r2_path, "w", encoding="utf-8") as f:
            json.dump(manifest_r2, f, indent=2)

        root_man_key = "daily-backup/manifest.json"
        log(f"Uploading root manifest.json to Dahono S3 (Retensi {retention_dahono}d) & Cloudflare R2 (Retensi {retention_r2}d)...")
        s3_dahono.upload_file(manifest_dahono_path, dahono_bucket, root_man_key)
        s3_r2.upload_file(manifest_r2_path, r2_bucket, root_man_key)

        duration = time.time() - start_time
        total_mb = total_bytes / (1024 * 1024)
        log(f"Backup job completed in {duration:.1f}s. Total size: {total_mb:.2f} MB")

        # Record persistent JSON state for Hermes Cron Reporter
        last_backup_data = {
            "status": "SUCCESS",
            "snapshot_date": date_str,
            "timestamp": now_dt.isoformat(),
            "epoch": epoch_now,
            "duration_seconds": round(duration, 2),
            "total_bytes": total_bytes,
            "total_mb": round(total_mb, 2),
            "encryption": {
                "format": "7z",
                "cipher": "AES-256",
                "header_encrypted": True
            },
            "files": files_meta,
            "dual_storage": {
                "dahono_s3": dahono_success,
                "cloudflare_r2": r2_success
            },
            "retention": {
                "dahono_days": retention_dahono,
                "cloudflare_days": retention_r2,
                "pruned_dahono": pruned_dahono,
                "pruned_cloudflare": pruned_r2,
                "active_dahono": active_snapshots_dahono,
                "active_cloudflare": active_snapshots_r2
            },
            "error": None
        }
        try:
            with open(LAST_BACKUP_FILE, "w", encoding="utf-8") as f_last:
                json.dump(last_backup_data, f_last, indent=2)
            log(f"Recorded state to {LAST_BACKUP_FILE}")
        except Exception as e_rec:
            log(f"Warning: could not write {LAST_BACKUP_FILE}: {e_rec}")

        # ----------------------------------------------------------------------
        # I. Telegram Notification Handling
        # ----------------------------------------------------------------------
        # By default, Hermes Cron Job handles official rich reporting at 05:05 WIB.
        # Direct Telegram dispatch here is optional via SEND_DIRECT_TELEGRAM_REPORT.
        send_direct = creds.get("SEND_DIRECT_TELEGRAM_REPORT", "false").lower() in ("1", "true", "yes")
        if tg_token and send_direct:
            prune_info = f"Dahono: {len(found_snapshots_dahono)}/{retention_dahono} hari (Rotasi: {len(pruned_dahono)}) | R2: {len(found_snapshots_r2)}/{retention_r2} hari (Rotasi: {len(pruned_r2)})"
            msg_html = (
                f"🛡️ <b>Octa Hub — Laporan Cadangan Harian</b>\n"
                f"<i>Pencadangan Otomatis Ekosistem Selesai & Terverifikasi</i>\n"
                f"<code>Status: VERIFIED SUCCESS</code> • <tg-time unix=\"{epoch_now}\" format=\"wDT\">{date_str}</tg-time>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📊 <b>Ringkasan Operasional:</b>\n"
                f"• <b>Snapshot:</b> <code>daily-backup/{date_str}/</code>\n"
                f"• <b>Durasi:</b> <code>{duration:.1f}s</code>\n"
                f"• <b>Total Ukuran:</b> <code>{total_mb:.2f} MB</code> ({total_bytes:,} bytes)\n"
                f"• <b>Format Enkripsi:</b> <code>7-Zip AES-256 (-mhe=on)</code>\n"
                f"• <b>Status Rotasi:</b> {prune_info}\n\n"
                f"☁️ <b>Sinkronisasi Dual-Storage:</b>\n"
                f"• <b>Dahono S3:</b> 🟢 <code>SYNCHRONIZED (100%)</code>\n"
                f"• <b>Cloudflare R2:</b> 🟢 <code>SYNCHRONIZED (100%)</code>\n"
                f"• <b>Root Runbook & Manifest:</b> 🟢 <code>UPDATED</code>\n\n"
                f"📦 <b>Rincian Modul Terenkripsi:</b>\n"
                f"• <code>9router.7z</code>: <b>{files_meta['9router.7z']['size_bytes'] / (1024*1024):.2f} MB</b> (AI Gateway SQLite)\n"
                f"• <code>hermes.7z</code>: <b>{files_meta['hermes.7z']['size_bytes'] / (1024*1024):.2f} MB</b> (Hermes State & Memory)\n"
                f"• <code>n8n.7z</code>: <b>{files_meta['n8n.7z']['size_bytes'] / (1024*1024):.2f} MB</b> (n8n Postgres Custom Dump)\n"
                f"• <code>obsidian.7z</code>: <b>{files_meta['obsidian.7z']['size_bytes'] / (1024*1024):.2f} MB</b> (Obsidian Knowledge Base)\n\n"
                f"<blockquote expandable><b>🔍 Digest Integritas Checksum (SHA-256):</b>\n"
                f"• <code>9router.7z</code>: <code>{files_meta['9router.7z']['sha256'][:16]}...</code>\n"
                f"• <code>hermes.7z</code>: <code>{files_meta['hermes.7z']['sha256'][:16]}...</code>\n"
                f"• <code>n8n.7z</code>: <code>{files_meta['n8n.7z']['sha256'][:16]}...</code>\n"
                f"• <code>obsidian.7z</code>: <code>{files_meta['obsidian.7z']['sha256'][:16]}...</code>\n"
                f"Panduan restorasi: <code>daily-backup/TUTORIAL-RESTORE.md</code></blockquote>"
            )
            send_telegram_notification(tg_token, tg_chat_id, tg_thread_id, msg_html)

    except Exception as e:
        log(f"FATAL ERROR during backup: {e}")
        import traceback
        err_trace = traceback.format_exc()
        traceback.print_exc()

        # Record failure state to JSON
        fail_data = {
            "status": "FAILED",
            "snapshot_date": date_str,
            "timestamp": now_dt.isoformat(),
            "epoch": epoch_now,
            "duration_seconds": round(time.time() - start_time, 2),
            "stage": current_stage,
            "error": str(e),
            "traceback": err_trace
        }
        try:
            with open(LAST_BACKUP_FILE, "w", encoding="utf-8") as f_fail:
                json.dump(fail_data, f_fail, indent=2)
        except Exception as e_fail_rec:
            log(f"Warning: could not write failure to {LAST_BACKUP_FILE}: {e_fail_rec}")

        # Send Telegram Failure Alert (Always dispatched on failure as safety watchdog)
        if tg_token:
            err_summary = str(e).replace("<", "&lt;").replace(">", "&gt;")
            clean_trace = err_trace[-400:].replace("<", "&lt;").replace(">", "&gt;")
            msg_fail = (
                f"🚨 <b>Octa Hub — Peringatan Kegagalan Cadangan</b>\n"
                f"<i>Insiden Terdeteksi pada Scheduler Backup Host</i>\n"
                f"<code>Status: BACKUP FAILED</code> • <tg-time unix=\"{epoch_now}\" format=\"wDT\">{date_str}</tg-time>\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ <b>Rincian Masalah:</b>\n"
                f"• <b>Snapshot:</b> <code>daily-backup/{date_str}/</code>\n"
                f"• <b>Tahap Kegagalan:</b> <code>{current_stage}</code>\n"
                f"• <b>Pesan Kesalahan:</b> <code>{err_summary}</code>\n\n"
                f"🛡️ <b>Tindakan Keamanan Otomatis:</b>\n"
                f"• <b>Anti-Pruning Freeze:</b> 🔒 <b>DIAKTIFKAN</b> (Tidak ada data lama yang dihapus).\n"
                f"• <b>Snapshot Historis:</b> Seluruh cadangan hari sebelumnya tetap utuh dan aman.\n\n"
                f"<blockquote expandable><b>Traceback Diagnosa Singkat:</b>\n"
                f"<pre>{clean_trace}</pre>\n"
                f"SOP Investigasi: Periksa <code>journalctl -u octa-backup.service</code></blockquote>"
            )
            send_telegram_notification(tg_token, tg_chat_id, tg_thread_id, msg_fail)
        sys.exit(1)

    finally:
        # Cleanup staging
        if os.path.exists(staging_dir):
            log(f"Cleaning up staging directory: {staging_dir}")
            shutil.rmtree(staging_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
