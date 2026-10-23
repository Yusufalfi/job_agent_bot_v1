import os
import requests
import logging

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            logging.warning("Telegram Notifier tidak aktif karena Token atau Chat ID belum disetel di .env")

    def send_job_alert(self, job: dict, score: int, reason: str):
        """
        Mengirimkan notifikasi lowongan kerja lengkap dengan Inline Buttons ke Telegram.
        """
        if not self.enabled:
            return

        message = (
            f"🎯 **REKOMENDASI LOWONGAN BARU!**\n\n"
            f"📌 **Jabatan:** {job.get('title')}\n"
            f"🏢 **Perusahaan:** {job.get('company')}\n"
            f"📍 **Lokasi:** {job.get('location')}\n"
            f"💰 **Gaji:** {job.get('salary_text', 'Tidak disebutkan')}\n"
            f"⭐ **Skor AI:** {score}/100\n\n"
            f"💡 **Alasan:** {reason}\n\n"
            f"🔗 [Link JobStreet]({job.get('url')})\n\n\n"
            f"💡 **Mau dibuatkan cover letter juga? klik ya **"
        )

        job_id = job.get('job_id', 'unknown')
        inline_keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Iya,Buatkan Cover Letter", "callback_data": f"gen_cl_{job_id}"},
                    {"text": "❌ Skip", "callback_data": f"skip_{job_id}"}
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
            "reply_markup": inline_keyboard
        }

        try:
            # Menggunakan verify=False agar tembus SSL lokal dan mencetak status aslinya
            response = requests.post(url, json=payload, verify=False, timeout=10)
            
            print(f"STATUS CODE TELEGRAM: {response.status_code}")
            print(f"RESPONSE TEXT: {response.text}")

            if response.status_code == 200:
                logging.info(f"Notifikasi Telegram dengan tombol terkirim untuk: {job.get('title')}")
            else:
                # Cek apakah respons berupa HTML (indikasi diblokir firewall/proxy kantor)
                if "<html" in response.text.lower() or "<doctype" in response.text.lower():
                    logging.error("Gagal mengirim Telegram: Koneksi diblokir oleh firewall jaringan kantor.")
                else:
                    logging.error(f"Gagal mengirim Telegram: {response.text}")
        except Exception as e:
            logging.error(f"Error koneksi ke Telegram API: {e}")