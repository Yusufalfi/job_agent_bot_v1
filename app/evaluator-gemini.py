import os
import json
import logging
from google import genai
from google.genai import types

class JobEvaluator:
    def __init__(self, profile_data: dict):
        """
        Inisialisasi AI Evaluator menggunakan Google GenAI SDK.
        Mengambil API key secara otomatis dari environment variable (GEMINI_API_KEY).
        """
        self.profile = profile_data
        # Menginisialisasi klien GenAI resmi
        self.client = genai.Client()
        
        # Gunakan model gemini-2.0-flash atau gemini-2.0-flash-lite yang stabil di SDK google-genai
        self.model_name = "gemini-3.8-flash"

    def evaluate_job(self, job: dict) -> tuple[int, str]:
        """
        Mengirim detail lowongan ke Gemini untuk dievaluasi berdasarkan profile.json
        Mengembalikan tuple: (score: int, reason: str)
        Jika error API, mengembalikan score = -1
        """
        prompt = f"""
        Bertindaklah sebagai Asisten Karier dan Perekrut Profesional AI yang sangat teliti.
        Tugasmu adalah mengevaluasi apakah lowongan pekerjaan berikut cocok untuk kandidat berdasarkan profil keahlian yang diberikan.

        === PROFIL KANDIDAT ===
        Target Roles: {self.profile.get('target_roles')}
        Main Skills: {self.profile.get('keywords')}
        Preferred Locations: {self.profile.get('preferred_locations')}
        Minimum Score Threshold: {self.profile.get('minimum_score', 75)}

        === DATA LOWONGAN PEKERJAAN ===
        Judul: {job.get('title')}
        Perusahaan: {job.get('company')}
        Lokasi: {job.get('location')}
        Gaji: {job.get('salary_text')}
        Jenis Pekerjaan: {job.get('work_type')}
        Deskripsi: {job.get('description')}

        === INSTRUKSI EVALUASI ===
        1. Analisis apakah deskripsi pekerjaan selaras dengan keahlian utama kandidat (RPA, Python, Automation, Playwright, dll).
        2. Berikan skor kecocokan dari angka 0 sampai 100.
        3. Berikan alasan penilaian secara singkat, padat, dan jelas dalam Bahasa Indonesia (maksimal 2-3 kalimat).
        4. Kamu HARUS merespons dalam format JSON murni tanpa teks tambahan di luar JSON, dengan struktur kunci berikut:
        {{
            "score": <angka_integer>,
            "reason": "<alasan_singkat>"
        }}
        """

        try:
            # Memanggil Gemini API menggunakan client.models.generate_content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2, # Temperatur rendah agar analisis konsisten dan objektif
                ),
            )
            
            # Parsing hasil respons JSON dari LLM
            result_json = json.loads(response.text)
            score = int(result_json.get("score", 0))
            reason = result_json.get("reason", "Tidak ada alasan yang diberikan.")
            
            return score, reason

        except Exception as e:
            logging.error(f"Gagal mengevaluasi lowongan [{job.get('title')}]: {e}")
            # Kembalikan -1 agar main.py tahu bahwa ini API_ERROR (bukan LOW_SCORE)
            return -1, f"API Error: {str(e)}"