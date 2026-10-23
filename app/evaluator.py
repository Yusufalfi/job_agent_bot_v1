
import os
import json
import logging
import time

# Membantu Python menggunakan sertifikat tepercaya dari Windows
import truststore
# Memasang sertifikat Windows ke sistem SSL Python.
# Harus dijalankan sebelum membuat koneksi ke Groq.
truststore.inject_into_ssl()
# Groq = client untuk mengirim request ke AI.
# RateLimitError = error khusus ketika batas request/token tercapai.
from groq import Groq, RateLimitError


class JobEvaluator:
    def __init__(self, profile_data: dict):
        # Menyimpan profil kandidat agar bisa digunakan saat evaluasi.
        self.profile = profile_data
        # Mengambil API key dari environment variable.
        # load_dotenv() di main.py harus dipanggil sebelum evaluator dibuat.
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY belum diatur. Periksa file .env."
            )

        # Membuat client untuk berkomunikasi dengan Groq.
        # max_retries=0 menonaktifkan retry otomatis dari SDK,
        # karena retry kita atur sendiri di evaluate_job().
        # timeout=60 berarti request dibatasi sampai 60 detik.
        self.client = Groq(
            api_key=api_key,
            max_retries=0,
            timeout=60.0,
        )

        # Nama model AI yang akan digunakan.
        self.model_name = "openai/gpt-oss-20b"

    def evaluate_job(self, job: dict) -> tuple[int, str]:
        # Menyusun instruksi yang akan dikirim kepada AI.
        # Data kandidat dan lowongan dimasukkan ke dalam prompt.
        prompt = f"""
            Kamu adalah asisten pencari kerja pribadi.

            Tugasmu adalah membantu saya menentukan apakah sebuah lowongan
            pekerjaan layak saya lamar berdasarkan profil dan kemampuan saya.

            === PROFIL SAYA ===
            Target Roles: {self.profile.get('target_roles', [])}
            Main Skills: {self.profile.get('keywords', [])}
            Preferred Locations: {self.profile.get('preferred_locations', [])}
            Minimum Score: {self.profile.get('minimum_score', 75)}

            === LOWONGAN PEKERJAAN ===
            Judul: {job.get('title', 'Tidak diketahui')}
            Perusahaan: {job.get('company', 'Tidak diketahui')}
            Lokasi: {job.get('location', 'Tidak diketahui')}
            Gaji: {job.get('salary_text', job.get('salary', 'Tidak diketahui'))}
            Jenis Pekerjaan: {job.get('work_type', 'Tidak diketahui')}
            Deskripsi:
            {str(job.get('description', ''))[:8000]}

            === TUGAS ===
            Analisis apakah saya cocok dengan lowongan ini dan apakah
            lowongan ini layak saya lamar.

            Pertimbangkan:
            1. Kesesuaian role dengan target role saya.
            2. Kesesuaian skill dan teknologi dengan kemampuan saya.
            3. Kesesuaian pengalaman yang dibutuhkan dengan profil saya.
            4. Kesesuaian lokasi dan jenis pekerjaan.
            5. Jika ada requirement yang tidak saya miliki, pertimbangkan
            seberapa penting requirement tersebut terhadap pekerjaan.

            Berikan skor kecocokan dari 0 sampai 100.

            Berikan alasan singkat dalam Bahasa Indonesia,
            maksimal 2 kalimat.

            Jangan mengarang pengalaman atau kemampuan saya yang tidak ada
            di profil.

            Balas HANYA dalam JSON valid:

            {{
                "score": 75,
                "reason": "Lowongan ini sangat sesuai dengan pengalaman RPA dan Python saya, meskipun ada beberapa requirement tambahan yang belum tercantum di profil."
            }}
            """

        # Mencoba evaluasi maksimal 3 kali jika terkena rate limit.
        for attempt in range(3):
            try:
                # Mengirim prompt ke model Groq.
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],

                    # Meminta model mengembalikan JSON,
                    response_format={"type": "json_object"},
                    # Membuat hasil relatif konsisten.
                    temperature=0.2,
                    # Menyediakan batas token untuk reasoning dan jawaban.
                    max_completion_tokens=1024,
                    # Mengurangi penggunaan token untuk reasoning.
                    reasoning_effort="low",
                    # Tidak meminta reasoning ditampilkan di respons.
                    include_reasoning=False,
                )

                # Mengambil teks jawaban dari respons AI.
                content = response.choices[0].message.content

                # Memastikan AI benar-benar menghasilkan teks.
                if not content:
                    finish_reason = response.choices[0].finish_reason
                    raise ValueError(
                        f"Respons AI kosong. Finish reason: {finish_reason}"
                    )

                # Mengubah teks JSON menjadi dictionary Python.
                result = json.loads(content)
                # Mengambil skor dan memastikan tipenya integer.
                score = int(result["score"])
                # Mengambil alasan penilaian.
                reason = str(result["reason"]).strip()
                # Memastikan skor berada pada rentang 0 sampai 100.
                if not 0 <= score <= 100:
                    raise ValueError(f"Skor tidak valid: {score}")
                # Memastikan AI memberikan alasan yang tidak kosong.
                if not reason:
                    raise ValueError("Alasan evaluasi kosong")

                # Mencatat bahwa evaluasi berhasil.
                logging.info(
                    f"Evaluasi berhasil: {job.get('title')} | Skor: {score}"
                )
                # Mengirim skor dan alasan kembali ke main.py.
                return score, reason

            # Bagian ini hanya berjalan jika Groq mengembalikan rate limit.
            except RateLimitError as e:

                # Jika ini percobaan terakhir, hentikan retry dan laporkan error.
                if attempt == 2:
                    logging.error(
                        f"Groq rate limit untuk [{job.get('title')}]: {e}"
                    )
                    return -1, "API Error: Groq rate limit tercapai"

                # Jeda bertambah setiap kali terkena rate limit:
                # percobaan pertama gagal -> 2 detik
                # percobaan kedua gagal -> 4 detik
                wait_seconds = 2 ** (attempt + 1)

                logging.warning(
                    f"Rate limit. Mencoba lagi dalam {wait_seconds} detik."
                )

                # Menunggu sebelum mencoba request lagi.
                time.sleep(wait_seconds)

            # Menangani error lain, misalnya koneksi gagal,
            # JSON tidak valid, atau respons AI kosong.
            except Exception as e:
                logging.error(
                    f"Gagal mengevaluasi [{job.get('title')}]: {e}"
                )

                # -1 menandakan evaluasi gagal, bukan skor sebenarnya.
                # main.py menggunakan nilai ini untuk status API_ERROR.
                return -1, f"API Error: {str(e)}"

        # Pengaman jika semua percobaan habis tanpa hasil.
        return -1, "API Error: Percobaan ulang habis"
