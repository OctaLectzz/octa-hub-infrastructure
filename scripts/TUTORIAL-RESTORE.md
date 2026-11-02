# 🚨 Octa Hub — Disaster Recovery & Restore Runbook
*Panduan Resmi Pemulihan Mandiri Seluruh Komponen Sistem Octa Hub*

---

## 📌 1. Gambaran Umum Arsitektur Cadangan
Seluruh cadangan harian Octa Hub disimpan secara paralel di dua lokasi remote storage:
1. **Dahono S3 Storage** (Target Utama / On-Premise S3)
2. **Cloudflare R2 Bucket** (Target Sekunder / Offsite Cloud)

### ⏳ Kebijakan Retensi Berjenjang (Tiered Retention):
- **Dahono S3 (Penyimpanan Utama):** Menyimpan riwayat snapshot harian selama **7 hari** (pemulihan lokal cepat).
- **Cloudflare R2 (Offsite Cloud DR):** Menyimpan riwayat snapshot harian selama **3 hari** (efisiensi storage offsite).
- **Anti-Pruning Freeze:** Jika terjadi kegagalan pada proses pencadangan atau sinkronisasi, rotasi pembersihan otomatis dibekukan demi mencegah hilangnya snapshot terdahulu.

Struktur objek di dalam storage:
```text
[Bucket S3 / R2]
└── daily-backup/
    ├── manifest.json                  # Indeks global snapshot aktif
    ├── TUTORIAL-RESTORE.md            # Panduan pemulihan ini
    └── <YYYY-MM-DD>/                  # Direktori snapshot per tanggal
        ├── 9router.7z                 # AI Gateway (SQLite atomic snapshot & environment)
        ├── hermes.7z                  # Hermes Agent (State DB, skills, profiles, auth)
        ├── n8n.7z                     # n8n Automation (PostgreSQL custom dump & config)
        ├── obsidian.7z                # Obsidian Knowledge Vault (Markdown & canvas)
        └── manifest.json              # Checksum SHA-256 & verifikasi harian
```

---

## 🔐 2. Spesifikasi Enkripsi & Kata Sandi
- **Format:** 7-Zip (`.7z`) dengan algoritma enkripsi **AES-256**.
- **Header Encryption:** Aktif (`-mhe=on`). Daftar nama file di dalam arsip disembunyikan sampai kata sandi dimasukkan.
- **Kata Sandi:** Menggunakan **Master Backup Password** yang telah ditentukan oleh Pemilik Sistem (Octa). Simpan kata sandi ini di Password Manager offline Anda.

### Utilitas Ekstraksi:
- **Linux:** Paket `7zip` atau `p7zip-full` (`apt install -y 7zip`)
- **macOS:** `brew install p7zip` atau aplikasi [Keka](https://www.keka.io/)
- **Windows:** Aplikasi resmi [7-Zip](https://www.7-zip.org/)

---

## 📥 3. Cara Mengunduh Berkas Cadangan

### Menggunakan AWS CLI / S3 CLI:
```bash
# Contoh mengunduh snapshot tanggal tertentu dari Cloudflare R2
aws s3 cp s3://<BUCKET_NAME>/daily-backup/2026-10-16/ ./restore-2026-10-16/ \
  --endpoint-url https://<ACCOUNT_ID>.r2.cloudflarestorage.com \
  --recursive
```
Atau unduh berkas yang diperlukan langsung melalui Web Console Cloudflare Dashboard atau Dahono S3 Console.

---

## 🔓 4. Perintah Ekstraksi Berkas (.7z)

Di terminal Linux / macOS:
```bash
# Ekstrak satu per satu (Anda akan diminta memasukkan kata sandi)
7z x 9router.7z -o./extracted/9router/
7z x hermes.7z -o./extracted/hermes/
7z x n8n.7z -o./extracted/n8n/
7z x obsidian.7z -o./extracted/obsidian/

# Atau masukkan password langsung via flag -p (gunakan hati-hati agar tidak terekam riwayat shell)
7z x hermes.7z -p"KATA_SANDI_ANDA" -o./extracted/hermes/
```

---

## 🛠️ 5. Prosedur Restorasi Detail per Komponen

### A. Hermes Multi-Agent Framework (`hermes.7z`)
Di dalam `hermes.7z`, terdapat paket resmi `hermes-backup-*.zip`.
1. Ekstrak `hermes.7z`.
2. Salin berkas zip ke dalam lingkungan Hermes atau jalankan perintah restore resmi:
   ```bash
   # Di dalam container hermes atau host:
   /opt/hermes/bin/hermes import /path/to/hermes-backup-*.zip --force
   ```
3. Restart container Hermes:
   ```bash
   docker restart hermes
   ```
*Hasil:* Seluruh sesi riwayat obrolan (`state.db`), kepribadian agen, memori profil, dan kredensial pulih 100%.

---

### B. Obsidian Knowledge Vault (`obsidian.7z`)
Di dalam `obsidian.7z` terdapat struktur lengkap direktori basis pengetahuan Markdown.
1. Ekstrak `obsidian.7z`:
   ```bash
   7z x obsidian.7z -o/tmp/obsidian-restore/
   ```
2. Pindahkan atau sinkronkan kembali ke direktori runtime:
   ```bash
   rsync -av /tmp/obsidian-restore/obsidian-vault/ /opt/octa/data/hermes/obsidian-vault/
   # Sesuaikan kepemilikan
   chown -R 10000:10000 /opt/octa/data/hermes/obsidian-vault/
   ```

---

### C. n8n Automation Engine (`n8n.7z`)
Di dalam `n8n.7z` terdapat:
- `postgres-dump.dump`: PostgreSQL Custom Binary Dump.
- `n8n.env`: Variabel konfigurasi lingkungan n8n termasuk `N8N_ENCRYPTION_KEY`.

1. Ekstrak `n8n.7z`.
2. Pastikan kontainer PostgreSQL `n8n-postgres` menyala dan sehat:
   ```bash
   docker ps | grep n8n-postgres
   ```
3. Pulihkan basis data:
   ```bash
   docker exec -i n8n-postgres pg_restore -U n8n_admin -d n8n --clean --if-exists < postgres-dump.dump
   ```
4. Salin kembali `n8n.env` ke `/opt/octa/stacks/n8n/.env` jika konfigurasi terhapus.
5. Restart kontainer n8n:
   ```bash
   docker restart n8n
   ```

---

### D. 9Router AI Gateway (`9router.7z`)
Di dalam `9router.7z` terdapat:
- `data.sqlite`: Basis data konfigurasi provider, API key, model catalog, dan token balance.
- `router.env`: Variabel lingkungan dan JWT secret.

1. Hentikan kontainer 9Router untuk mencegah konflik lock basis data:
   ```bash
   docker stop router
   ```
2. Ekstrak `9router.7z` dan salin `data.sqlite` ke jalurnya:
   ```bash
   cp -f data.sqlite /opt/octa/data/router/db/data.sqlite
   chown 1000:1000 /opt/octa/data/router/db/data.sqlite
   ```
3. Salin `router.env` ke `/opt/octa/stacks/router/.env` jika diperlukan.
4. Nyalakan kembali kontainer:
   ```bash
   docker start router
   ```

---

## 🔍 6. Verifikasi Integritas Pascarestorasi
Setelah seluruh komponen dipulihkan, jalankan verifikasi kesehatan:
```bash
# 1. Cek seluruh kontainer
docker ps

# 2. Cek endpoint 9Router
curl -s http://127.0.0.1:20128/health || curl -s http://127.0.0.1:20128/v1/models

# 3. Cek endpoint n8n
curl -s http://127.0.0.1:5678/healthz

# 4. Cek endpoint Hermes Gateway
curl -s http://127.0.0.1:9119/health
```

---
*Dokumen ini dibuat otomatis oleh Atlas (octainfra) sebagai bagian dari Disaster Recovery Protocol Octa Hub.*
