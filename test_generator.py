import os
import traceback
from dotenv import load_dotenv

# Memuat environment variables (.env)
load_dotenv()

# Impor fungsi generator dari folder app
from app.cover_letter_generator import generate_cover_letter_docx


def test():
    # Cek status API key sebelum tes
    api_key = os.getenv("GROQ_API_KEY")

    print(
        f"DEBUG: Status GROQ_API_KEY -> "
        f"{'Ditemukan (Awalan: ' + api_key[:8] + '...)' if api_key else 'TIDAK DITEMUKAN'}"
    )

    # 1. Simulasikan data lowongan dummy
    dummy_job = {
        "title": "RPA & Automation Engineer",
        "company": "PT Solusi Digital Indonesia",
        "description": (
            "Kami mencari profesional yang berpengalaman "
            "dalam membangun otomasi proses bisnis menggunakan "
            "Python, UiPath, dan integrasi API database."
        )
    }

    print(
        "Sedang meminta AI meracik Cover Letter dan membuat file .docx..."
    )

    try:
        # 2. Panggil fungsi pembuat dokumen
        file_path = generate_cover_letter_docx(
            dummy_job,
            profile_path="config/profile.json"
        )

        print(
            f"\n✅ Berhasil! File Cover Letter tersimpan di: "
            f"{os.path.abspath(file_path)}"
        )

    except Exception:
        print("\n❌ Terjadi kesalahan:")
        traceback.print_exc()


if __name__ == "__main__":
    test()