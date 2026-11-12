#!/usr/bin/env python3
"""
Octa Hub — Docker Container Lifecycle Watcher & Rich Telegram Notifier
Author: Atlas (octainfra) for Octa Hub
Location: /opt/octa/scripts/octa-container-watcher.py

Monitors core Docker containers (hermes, router, n8n, n8n-postgres, n8n-runner)
via `docker events` stream and dispatches Bot API 10.3 Rich Messages to
Octa Hub Group (-1004349640522), Topic 36 (DevOps & Infra) using Atlas bot.
"""

import json
import logging
import os
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

# ------------------------------------------------------------------------------
# Configuration & Constants
# ------------------------------------------------------------------------------
WIB = ZoneInfo("Asia/Jakarta")
ENV_FILE = "/opt/octa/data/hermes/profiles/octainfra/.env"
TELEGRAM_CHAT_ID = -1004349640522
TELEGRAM_THREAD_ID = 36

MONITORED_CONTAINERS: Dict[str, Dict[str, str]] = {
    "hermes": {
        "label": "Hermes Agent Runtime",
        "url": "https://hermes.octalectzz.my.id",
        "btn_label": "📊 Buka Dashboard Hermes",
    },
    "router": {
        "label": "9Router AI Gateway",
        "url": "https://router.octalectzz.my.id",
        "btn_label": "🌐 Buka Dashboard 9Router",
    },
    "n8n": {
        "label": "n8n Workflow Automation",
        "url": "https://n8n.octalectzz.my.id",
        "btn_label": "⚡ Buka Konsol n8n",
    },
    "n8n-postgres": {
        "label": "n8n PostgreSQL 18",
        "url": "https://n8n.octalectzz.my.id",
        "btn_label": "⚡ Buka Konsol n8n",
    },
    "n8n-runner": {
        "label": "n8n Task Runner",
        "url": "https://n8n.octalectzz.my.id",
        "btn_label": "⚡ Buka Konsol n8n",
    },
}

SECRET_PATTERNS = [
    re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"((?:token|password|secret|api_key|apikey)\s*[=:]\s*)[^\s\"';]+", re.IGNORECASE),
    re.compile(r"(https://api\.telegram\.org/bot)[^/\s]+", re.IGNORECASE),
]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("octa-container-watcher")


@dataclass
class ContainerDownState:
    down_ts: float
    exit_code: Optional[int]
    oom_killed: bool
    reason: str


class LifecycleWatcher:
    """Streams Docker container events and dispatches Telegram Rich notifications."""

    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.down_states: Dict[str, ContainerDownState] = {}
        self.unhealthy_containers: set[str] = set()
        self.last_oom_ts: Dict[str, float] = {}
        self._proc: Optional[subprocess.Popen[str]] = None

    @staticmethod
    def load_bot_token() -> str:
        """Load Atlas TELEGRAM_BOT_TOKEN from octainfra .env file."""
        if not os.path.exists(ENV_FILE):
            raise FileNotFoundError(f"Env file not found: {ENV_FILE}")
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "TELEGRAM_BOT_TOKEN":
                    token = v.strip().strip("\"").strip("'")
                    if token:
                        return token
        raise ValueError(f"TELEGRAM_BOT_TOKEN not found in {ENV_FILE}")

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Redact potential secrets from container logs before sending to Telegram."""
        cleaned = text
        for pattern in SECRET_PATTERNS:
            cleaned = pattern.sub(r"\1[REDACTED]", cleaned)
        return cleaned

    @staticmethod
    def format_wib_short(unix_ts: int) -> str:
        """Format timestamp <= 31 chars for <tg-time> fallback safety."""
        dt = datetime.fromtimestamp(unix_ts, tz=WIB)
        months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        return f"{dt.day:02d} {months[dt.month - 1]} {dt.year}, {dt.strftime('%H:%M')} WIB"

    @staticmethod
    def inspect_container(name: str) -> Dict[str, Any]:
        """Run `docker inspect` for container state metadata."""
        try:
            res = subprocess.run(
                ["docker", "inspect", name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=8,
            )
            if res.returncode == 0:
                arr = json.loads(res.stdout)
                if arr and isinstance(arr, list):
                    return arr[0]
        except Exception as exc:
            logger.warning("Failed to inspect container %s: %s", name, exc)
        return {}

    @classmethod
    def fetch_tail_logs(cls, name: str, lines: int = 12) -> str:
        """Fetch and sanitize last N lines of container stdout/stderr."""
        try:
            res = subprocess.run(
                ["docker", "logs", "--tail", str(lines), name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=8,
            )
            output = (res.stdout or "").strip()
            if not output:
                return "(tidak ada output log terbaru)"
            output = cls.sanitize_text(output)
            if len(output) > 1200:
                output = "...(truncated)...\n" + output[-1200:]
            return output
        except Exception as exc:
            return f"(gagal mengambil log: {exc})"

    @staticmethod
    def classify_exit_reason(exit_code: Optional[int], oom_killed: bool, error_msg: str) -> str:
        """Translate container exit code & flags into human-readable diagnostics."""
        if oom_killed:
            return "Out-Of-Memory (OOMKilled) — melebihi batas memori"
        if exit_code is None:
            return "Tidak diketahui (container inspect tidak tersedia)"
        if exit_code == 0:
            return "Graceful Stop / Clean Shutdown (Exit 0)"
        if exit_code == 137:
            return "SIGKILL (Force Kill / Manual Restart / OOM)"
        if exit_code == 143:
            return "SIGTERM (Graceful Shutdown / Stack Restart)"
        if error_msg:
            return f"Abnormal Exit (Code {exit_code}): {error_msg[:80]}"
        return f"Crash / Abnormal Exit (Exit Code {exit_code})"

    def send_telegram(self, markdown_text: str, btn_label: str, btn_url: str) -> None:
        """Dispatch Bot API 10.3 sendRichMessage with fallback to sendMessage."""
        try:
            token = self.load_bot_token()
        except Exception as exc:
            logger.error("Cannot load bot token: %s", exc)
            return

        reply_markup = {"inline_keyboard": [[{"text": btn_label, "url": btn_url}]]}
        rich_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "message_thread_id": TELEGRAM_THREAD_ID,
            "rich_message": {"markdown": markdown_text},
            "reply_markup": reply_markup,
        }

        if self._post_bot_api(token, "sendRichMessage", rich_payload):
            return

        fallback_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "message_thread_id": TELEGRAM_THREAD_ID,
            "text": markdown_text,
            "parse_mode": "Markdown",
            "reply_markup": reply_markup,
            "disable_web_page_preview": True,
        }
        self._post_bot_api(token, "sendMessage", fallback_payload)

    @staticmethod
    def _post_bot_api(token: str, method: str, payload: Dict[str, Any]) -> bool:
        url = f"https://api.telegram.org/bot{token}/{method}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                if body.get("ok"):
                    return True
                logger.warning("Telegram %s returned not ok: %s", method, body)
                return False
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.warning("Telegram %s HTTP %s: %s", method, e.code, err_body)
            return False
        except Exception as exc:
            logger.warning("Telegram %s failed: %s", method, exc)
            return False

    def handle_die(self, name: str, event: Dict[str, Any], unix_ts: int) -> None:
        """Handle container `die` event (stop, kill, crash, or restart)."""
        meta = MONITORED_CONTAINERS[name]
        attrs = event.get("Actor", {}).get("Attributes", {})
        raw_exit = attrs.get("exitCode")
        exit_code = int(raw_exit) if raw_exit is not None and str(raw_exit).lstrip("-").isdigit() else None

        insp = self.inspect_container(name)
        state = insp.get("State", {})
        host_cfg = insp.get("HostConfig", {})
        restart_policy = host_cfg.get("RestartPolicy", {}).get("Name", "unknown")
        restart_count = insp.get("RestartCount", 0)
        error_msg = state.get("Error", "")

        recent_oom = (time.time() - self.last_oom_ts.get(name, 0)) < 15
        oom_killed = bool(state.get("OOMKilled", False)) or recent_oom
        if exit_code is None and "ExitCode" in state:
            exit_code = state.get("ExitCode")

        reason = self.classify_exit_reason(exit_code, oom_killed, error_msg)
        self.down_states[name] = ContainerDownState(
            down_ts=time.time(),
            exit_code=exit_code,
            oom_killed=oom_killed,
            reason=reason,
        )

        logs_tail = self.fetch_tail_logs(name, lines=12)
        wib_str = self.format_wib_short(unix_ts)
        status_badge = "OOM KILLED" if oom_killed else ("STOPPED" if exit_code == 0 else "EXITED / RESTARTING")
        icon = "🛑" if exit_code != 0 or oom_killed else "⏸️"

        msg = (
            f"# {icon} Alert: Kontainer `{name}` Berhenti\n"
            f"*{meta['label']} | Docker Lifecycle Watcher*\n\n"
            f"- Kontainer: `{name}`  \n"
            f"- Waktu: <tg-time unix=\"{unix_ts}\" format=\"wDT\">{wib_str}</tg-time>  \n"
            f"- Status: =={status_badge}==  \n\n"
            f"---\n\n"
            f"## 📊 Diagnostik Penghentian\n"
            f"| Parameter | Nilai / Keterangan |\n"
            f"| :--- | :--- |\n"
            f"| **Event** | `die` |\n"
            f"| **Exit Code** | `{exit_code if exit_code is not None else '?'}` |\n"
            f"| **OOM Killed** | `{'true' if oom_killed else 'false'}` |\n"
            f"| **Restart Policy** | `{restart_policy}` (Count: `{restart_count}`) |\n"
            f"| **Alasan Terdeteksi** | {reason} |\n\n"
            f"<details><summary>🔍 Log Terakhir Kontainer (Tap untuk Buka/Tutup)</summary>\n\n"
            f"```text\n{logs_tail}\n```\n\n"
            f"</details>\n\n"
            f"---\n\n"
            f"> 💡 **Tindakan & Pemantauan**:\n"
            f"> - Watcher tetap memantau status pemulihan kontainer `{name}`.\n"
            f"> - Jika kebijakan restart otomatis aktif, notifikasi pemulihan akan dikirimkan saat kontainer kembali berjalan.\n\n"
            f"👉 [**{meta['btn_label']} ↗️**]({meta['url']})"
        )
        logger.info("Sending DOWN alert for %s (exit=%s, oom=%s)", name, exit_code, oom_killed)
        self.send_telegram(msg, meta["btn_label"], meta["url"])

    def handle_start(self, name: str, unix_ts: int) -> None:
        """Handle container `start` event after a recorded down state."""
        down_state = self.down_states.pop(name, None)
        if not down_state:
            return

        # Brief stabilization check so crash-loops are not falsely reported as healthy
        time.sleep(3)
        insp = self.inspect_container(name)
        running = insp.get("State", {}).get("Running", False)
        if not running:
            logger.warning("Container %s did not stay running after start; skipping recovery notice.", name)
            return

        meta = MONITORED_CONTAINERS[name]
        downtime_sec = max(1, int(time.time() - down_state.down_ts))
        wib_str = self.format_wib_short(unix_ts)

        msg = (
            f"# 🟢 Recovery: Kontainer `{name}` Kembali Aktif\n"
            f"*{meta['label']} | Docker Lifecycle Watcher*\n\n"
            f"- Kontainer: `{name}`  \n"
            f"- Waktu Pulih: <tg-time unix=\"{unix_ts}\" format=\"wDT\">{wib_str}</tg-time>  \n"
            f"- Durasi Downtime: `~{downtime_sec} detik`  \n"
            f"- Status: ==RUNNING==  \n\n"
            f"---\n\n"
            f"> 💡 **Status Pemulihan**:\n"
            f"> - Kontainer `{name}` telah kembali berjalan normal setelah insiden sebelumnya (`{down_state.reason}`).\n\n"
            f"👉 [**{meta['btn_label']} ↗️**]({meta['url']})"
        )
        logger.info("Sending RECOVERY notice for %s (downtime=%ss)", name, downtime_sec)
        self.send_telegram(msg, meta["btn_label"], meta["url"])

    def handle_health(self, name: str, action: str, unix_ts: int) -> None:
        """Handle container health_status transitions."""
        meta = MONITORED_CONTAINERS[name]
        wib_str = self.format_wib_short(unix_ts)

        if action == "health_status: unhealthy" and name not in self.unhealthy_containers:
            self.unhealthy_containers.add(name)
            logs_tail = self.fetch_tail_logs(name, lines=10)
            msg = (
                f"# ⚠️ Peringatan: Kontainer `{name}` Unhealthy\n"
                f"*{meta['label']} | Healthcheck Telemetry*\n\n"
                f"- Kontainer: `{name}`  \n"
                f"- Waktu: <tg-time unix=\"{unix_ts}\" format=\"wDT\">{wib_str}</tg-time>  \n"
                f"- Status: ==UNHEALTHY==  \n\n"
                f"---\n\n"
                f"<details><summary>🔍 Log Terakhir Kontainer (Tap untuk Buka/Tutup)</summary>\n\n"
                f"```text\n{logs_tail}\n```\n\n"
                f"</details>\n\n"
                f"> 💡 **Evaluasi**:\n"
                f"> - Healthcheck internal kontainer `{name}` gagal. Periksa kesiapan layanan.\n\n"
                f"👉 [**{meta['btn_label']} ↗️**]({meta['url']})"
            )
            self.send_telegram(msg, meta["btn_label"], meta["url"])

        elif action == "health_status: healthy" and name in self.unhealthy_containers:
            self.unhealthy_containers.discard(name)
            msg = (
                f"# 🟢 Pulih: Kontainer `{name}` Kembali Healthy\n"
                f"*{meta['label']} | Healthcheck Telemetry*\n\n"
                f"- Kontainer: `{name}`  \n"
                f"- Waktu: <tg-time unix=\"{unix_ts}\" format=\"wDT\">{wib_str}</tg-time>  \n"
                f"- Status: ==HEALTHY==  \n\n"
                f"> 💡 **Status**:\n"
                f"> - Healthcheck kontainer `{name}` kembali lolos.\n\n"
                f"👉 [**{meta['btn_label']} ↗️**]({meta['url']})"
            )
            self.send_telegram(msg, meta["btn_label"], meta["url"])

    def process_event(self, raw_line: str) -> None:
        """Parse and route a single JSON line from `docker events`."""
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            return

        if event.get("Type") != "container":
            return

        attrs = event.get("Actor", {}).get("Attributes", {})
        name = attrs.get("name", "")
        if name not in MONITORED_CONTAINERS:
            return

        action = event.get("Action", "")
        unix_ts = int(event.get("time") or time.time())

        if action == "oom":
            self.last_oom_ts[name] = time.time()
        elif action == "die":
            self.handle_die(name, event, unix_ts)
        elif action == "start":
            threading.Thread(
                target=self.handle_start, args=(name, unix_ts), daemon=True
            ).start()
        elif action.startswith("health_status:"):
            self.handle_health(name, action, unix_ts)

    def run(self) -> None:
        """Main event-streaming loop with automatic reconnect on stream drop."""
        logger.info("Starting watcher for containers: %s", ", ".join(MONITORED_CONTAINERS.keys()))
        while not self.stop_event.is_set():
            try:
                self._proc = subprocess.Popen(
                    ["docker", "events", "--filter", "type=container", "--format", "{{json .}}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )
                assert self._proc.stdout is not None
                for line in self._proc.stdout:
                    if self.stop_event.is_set():
                        break
                    line = line.strip()
                    if line:
                        self.process_event(line)

                rc = self._proc.wait()
                if not self.stop_event.is_set():
                    err = self._proc.stderr.read().strip() if self._proc.stderr else ""
                    logger.warning("docker events stream exited (%s): %s. Reconnecting in 5s...", rc, err)
                    self.stop_event.wait(5)
            except Exception as exc:
                logger.error("Watcher loop error: %s. Retrying in 5s...", exc)
                self.stop_event.wait(5)

    def stop(self, *_args: Any) -> None:
        logger.info("Shutdown signal received; stopping watcher...")
        self.stop_event.set()
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()


def main() -> int:
    watcher = LifecycleWatcher()
    signal.signal(signal.SIGTERM, watcher.stop)
    signal.signal(signal.SIGINT, watcher.stop)
    # Validate token at startup so misconfiguration fails fast in journalctl
    watcher.load_bot_token()
    watcher.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
