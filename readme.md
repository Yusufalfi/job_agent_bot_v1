# Job Application Automation Bot 🚀

Bot otomasi pencarian lowongan kerja, penilaian kesesuaian berbasis AI, serta pembuatan *cover letter* otomatis yang terintegrasi langsung dengan Telegram. Proyek ini dirancang untuk memangkas waktu proses pelamaran kerja harian dengan mengotomatisasi pengumpulan lowongan hingga penyiapan dokumen siap kirim.

---

## 🎯 Goal Utama

Tujuan utama dari proyek ini adalah menyediakan sistem asisten pribadi otomatis yang bekerja harian untuk:
1. **Menghemat Waktu Pelamaran:** Secara otomatis mengikis (*scraping*) lowongan kerja terbaru yang relevan.
2. **Filtering & Scoring Cerdas:** Memanfaatkan AI (Groq / Gemini) untuk menganalisis deskripsi pekerjaan dan memberikan skor kesesuaian (*match score*) berdasarkan profil/CV pengguna.
3. **Penyiapan Dokumen Instan:** Meng-generate dokumen *Cover Letter* kustom berbentuk file Word (`.docx`) yang siap digunakan.
4. **Kontrol Interaktif:** Memberikan notifikasi dan kemudahan akses pembuatan dokumen langsung dari aplikasi Telegram.

---

## ✨ Fitur Utama

- **Automated Job Scraper:** Mengambil data lowongan kerja dari berbagai sumber platform lowongan kerja secara berkala.
- **AI-Powered Match Assessment:** Evaluasi kualifikasi lowongan menggunakan LLM (Groq API / Google Gemini API) untuk menentukan apakah lowongan tersebut layak dilamar.
- **Automated Cover Letter Generator:** Membuat file `.docx` *Cover Letter* yang disesuaikan dengan posisi dan kualifikasi perusahaan terkait secara otomatis.
- **Telegram Bot Integration:** Notifikasi *real-time* mengenai lowongan berprospek tinggi dilengkapi dengan tombol interaktif untuk *generate* dokumen langsung dari *chat*.
- **Local Data Persistence:** Penyimpanan riwayat lowongan dan status aplikasi kerja.

---

## 📁 Struktur Folder Project

```text
# Agentic AI Job Match Bot 🚀

Bot otomasi pencarian dan lamaran kerja cerdas menggunakan Python, Playwright, LLM (Groq/Gemini) untuk evaluasi & pembuatan *cover letter*, serta integrasi notifikasi interaktif via Telegram Bot.

---

## 📁 Struktur Project

```text
Agentic_Ai_Job_match/
├── app/
│   ├── cover_letter_generator.py # Generator dokumen cover letter (.docx)
│   ├── database.py             # Modul manajemen & penyimpanan data (Excel/DB)
│   ├── evaluator-gemini.py     # Evaluator kecocokan lowongan menggunakan Google Gemini
│   ├── evaluator.py            # Evaluator kecocokan lowongan menggunakan Groq LLM
│   ├── filters.py              # Logika penyaringan & kriteria lowongan kerja
│   ├── notifier.py             # Logika pengiriman notifikasi/alert
│   ├── scraper copy.py         # Backup/Eksperimen script scraper
│   ├── scraper.py              # Engine scraping lowongan kerja (Playwright)
│   └── telegram_bot.py         # Modul integrasi & formatting pesan Telegram
├── backup/                     # Backup file/data lama
├── config/                     # Configuration files & settings
├── data/                       # Penyimpanan lokal data hasil scraping (Excel/JSON)
├── doc/                        # Dokumentasi BRD & panduan project
├── logs/                       # File log aktivitas aplikasi
├── test/                       # Unit test & script pengujian lokal
├── .env                        # Environment variables (API Keys, Token, DB)
├── .gitignore                  # Daftar file/folder yang diabaikan Git
├── bot_listener.py             # Telegram bot event listener / polling handler
├── main.py                     # Entry point utama untuk menjalankan workflow scraper
└── requirements.txt            # Daftar dependensi Python
```

---

## 🛠️ Prasyarat & Cara Instalasi (Local Setup)

### 1. Prasyarat Sistem
- Python versi `3.10` atau yang lebih baru.
- Akun Telegram & Bot Token (dibuat via `@BotFather`).
- API Key dari **Groq** atau **Google GenAI**.

### 2. Langkah Instalasi

1. **Clone Repository:**
   ```bash
   git clone https://github.com/Yusufalfi/job_agent_bot_v1.git
   cd NAMA_REPOSITORY
   ```

2. **Buat & Aktifkan Virtual Environment (`.venv`):**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment Variable (`.env`):**
   Salin file `.env.example` (atau buat file `.env` baru di root folder) lalu isi credential yang dibutuhkan:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## 🚀 Cara Penggunaan (Local Run)

Untuk menjalankan seluruh sistem secara lokal:

1. **Menjalankan Scraper & Analisis Lowongan:**
   Jalankan script utama untuk mengambil lowongan kerja terbaru, menghitung skor AI, dan mengirimkan notifikasi ke Telegram:
   ```bash
   python main.py
   ```

2. **Menjalankan Bot Listener Telegram:**
   Jalankan script bot listener agar bot dapat merespons perintah/tombol dari Telegram (misal: tombol pembuat Cover Letter):
   ```bash
   python bot_listener.py
   ```

---

## 🗺️ Roadmap & Pengembangan Selanjutnya

- [ ] **Migrasi ke Web Server Flask (`app.py`):** Menyatukan logika bot dan trigger ke dalam arsitektur berbasis HTTP Webhook.
- [ ] **Cloud Persistence (Supabase / PostgreSQL):** Menggantikan penyimpanan lokal Excel dengan database cloud gratis agar data aman saat dideploy.
- [ ] **Deployment 24/7 di Render:** Menjalankan aplikasi web server di cloud secara bebas hambatan jaringan/firewall lokal.
- [ ] **Automated Cron Trigger:** Mengintegrasikan penggerak otomatis harian (misal jam 19.00 WIB) menggunakan GitHub Actions atau Cron-Job service.
- [ ] **Multi-User Capabilities:** Mendukung pengelolaan profil/CV dan `chat_id` yang dinamis untuk banyak pengguna sekaligus.