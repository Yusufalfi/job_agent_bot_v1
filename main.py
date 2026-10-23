# import json
# import asyncio
# import os
# from app.scraper import JobStreetScraper
# from app.notifier import TelegramNotifier
# from app.filters import apply_deterministic_filters
# from app.database import initialize_database, save_jobs_to_excel, EXCEL_FILE_PATH
# from app.evaluator import JobEvaluator
# import openpyxl

# from dotenv import load_dotenv

# # Memuat variabel dari file .env ke environment sistem
# load_dotenv()

# async def main():
#     print("=== LANGKAH 1: Membaca Profile ===")
#     with open("config/profile.json", "r", encoding="utf-8") as f:
#         profile = json.load(f)
    
#     target_roles = profile.get("target_roles", [])
#     print(f"Target peran: {target_roles}")

#     print("\n=== LANGKAH 2: Menjalankan Scraper ===")
#     scraper = JobStreetScraper(max_limit=5)  # Ambil 5 teratas per role untuk uji coba
#     raw_jobs = await scraper.run(target_roles)
#     print(f"Total data mentah terkumpul: {len(raw_jobs)}")

#     print("\n=== LANGKAH 3: Menjalankan Hard Filter ===")
#     filtered_jobs = apply_deterministic_filters(raw_jobs, profile)
    
#     print("\n=== LANGKAH 4: Menyimpan ke Excel Database ===")
#     save_jobs_to_excel(raw_jobs) 

#     print("\n=== LANGKAH 5: Menjalankan AI Evaluator (Gemini) ===")
#     evaluator = JobEvaluator(profile)
    
#     # Membuka file Excel untuk memperbarui skor AI pada baris yang statusnya PENDING_AI
#     wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
#     ws = wb.active
    
#     evaluated_count = 0
#     min_score = profile.get("minimum_score", 75)

#     # Iterasi baris di Excel mulai baris ke-2
#     for row in range(2, ws.max_row + 1):
#         status = ws.cell(row=row, column=11).value # Kolom Evaluation Status
        
#         if status == "PENDING_AI":
#             # Ambil data lowongan dari baris Excel
#             job_data = {
#                 "job_id": ws.cell(row=row, column=1).value,
#                 "title": ws.cell(row=row, column=3).value,
#                 "company": ws.cell(row=row, column=4).value,
#                 "location": ws.cell(row=row, column=5).value,
#                 "salary_text": ws.cell(row=row, column=6).value,
#                 "description": ws.cell(row=row, column=9).value,
#                 "work_type": ws.cell(row=row, column=10).value,
#             }
            
#             print(f"Mengevaluasi via AI: {job_data['title']} di {job_data['company']}...")
#             score, reason = evaluator.evaluate_job(job_data)
            
#             # Tentukan status akhir dengan penanganan khusus jika terjadi Error API (score = -1)
#             if score == -1:
#                 new_status = "API_ERROR"
#                 score_to_save = 0
#                 notif_status = "-"
#                 app_status = "-"
#             elif score >= min_score:
#                 new_status = "EVALUATED"
#                 score_to_save = score
#                 notif_status = "SENT"
#                 app_status = "ToApply"  # Status awal Mini ATS untuk lowongan yang layak dilamar
                
#                 # --- KIRIM KE TELEGRAM OTOMATIS ---
#                 try:
#                     notifier = TelegramNotifier()
#                     notifier.send_job_alert(job_data, score, reason)
#                 except Exception as tg_err:
#                     print(f"Gagal mengirim notifikasi Telegram: {tg_err}")
#                     notif_status = "FAILED"
#                 # -----------------------------------
#             else:
#                 new_status = "LOW_SCORE"
#                 score_to_save = score
#                 notif_status = "-"
#                 app_status = "-"
            
#             # Update nilai ke dalam sel Excel
#             ws.cell(row=row, column=11, value=new_status)          # Evaluation Status (Kolom 11)
#             ws.cell(row=row, column=12, value=score_to_save)        # AI Score (Kolom 12)
#             ws.cell(row=row, column=13, value=reason)               # AI Reason (Kolom 13)
#             ws.cell(row=row, column=14, value=notif_status)         # Notification Status (Kolom 14)
#             ws.cell(row=row, column=15, value=app_status)           # Application Status (Kolom 15)
#             ws.cell(row=row, column=16, value="-")                  # Applied Date (Kolom 16)
            
#             evaluated_count += 1
#             print(f" -> Skor AI: {score_to_save} | Status: {new_status} | Alasan: {reason}\n")
            
#             # Jeda 65 detik agar aman dari batasan Request Per Minute (RPM) Gemini
#             # print("Menunggu 65 detik untuk mematuhi limit RPM Gemini...")
#             # await asyncio.sleep(65)
#             await asyncio.sleep(20)
            
#     wb.save(EXCEL_FILE_PATH)
#     wb.close()
#     print(f"=== PROSES SELESAI. {evaluated_count} lowongan berhasil dievaluasi oleh AI! ===")

# if __name__ == "__main__":
#     asyncio.run(main())



import json
import asyncio
import os
from app.scraper import JobStreetScraper
from app.notifier import TelegramNotifier
from app.filters import apply_deterministic_filters
from app.database import initialize_database, save_jobs_to_excel, EXCEL_FILE_PATH
from app.evaluator import JobEvaluator
import openpyxl

from dotenv import load_dotenv

# Memuat variabel dari file .env ke environment sistem
load_dotenv()

async def main():
    print("=== LANGKAH 1: Membaca Profile ===")
    with open("config/profile.json", "r", encoding="utf-8") as f:
        profile = json.load(f)
    
    # PERBAIKAN: Mengambil target_roles dari candidate (atau root sebagai fallback)
    candidate_data = profile.get("candidate", {})
    target_roles = candidate_data.get("target_roles", profile.get("target_roles", []))
    
    print(f"Target peran: {target_roles}")

    if not target_roles:
        print("⚠️ WARN: target_roles tidak ditemukan di profile.json! Periksa isi file profile kamu.")
        return

    print("\n=== LANGKAH 2: Menjalankan Scraper ===")
    scraper = JobStreetScraper(max_limit=5)  # Ambil 5 teratas per role untuk uji coba
    raw_jobs = await scraper.run(target_roles)
    print(f"Total data mentah terkumpul: {len(raw_jobs)}")

    print("\n=== LANGKAH 3: Menjalankan Hard Filter ===")
    filtered_jobs = apply_deterministic_filters(raw_jobs, profile)
    
    print("\n=== LANGKAH 4: Menyimpan ke Excel Database ===")
    save_jobs_to_excel(raw_jobs) 

    print("\n=== LANGKAH 5: Menjalankan AI Evaluator (Groq/Gemini) ===")
    evaluator = JobEvaluator(profile)
    
    # Membuka file Excel untuk memperbarui skor AI pada baris yang statusnya PENDING_AI
    wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
    ws = wb.active
    
    evaluated_count = 0
    # Mengambil minimum_score dari candidate/profile (default: 75)
    min_score = candidate_data.get("minimum_score", profile.get("minimum_score", 75))

    # Iterasi baris di Excel mulai baris ke-2
    for row in range(2, ws.max_row + 1):
        status = ws.cell(row=row, column=11).value # Kolom Evaluation Status
        
        if status == "PENDING_AI":
            # Ambil data lowongan dari baris Excel
            job_data = {
                "job_id": ws.cell(row=row, column=1).value,
                "title": ws.cell(row=row, column=3).value,
                "company": ws.cell(row=row, column=4).value,
                "location": ws.cell(row=row, column=5).value,
                "salary_text": ws.cell(row=row, column=6).value,
                "description": ws.cell(row=row, column=9).value,
                "work_type": ws.cell(row=row, column=10).value,
            }
            
            print(f"Mengevaluasi via AI: {job_data['title']} di {job_data['company']}...")
            score, reason = evaluator.evaluate_job(job_data)
            
            # Tentukan status akhir dengan penanganan khusus jika terjadi Error API (score = -1)
            if score == -1:
                new_status = "API_ERROR"
                score_to_save = 0
                notif_status = "-"
                app_status = "-"
            elif score >= min_score:
                new_status = "EVALUATED"
                score_to_save = score
                notif_status = "SENT"
                app_status = "ToApply"  # Status awal Mini ATS untuk lowongan yang layak dilamar
                
                # --- KIRIM KE TELEGRAM OTOMATIS ---
                try:
                    notifier = TelegramNotifier()
                    notifier.send_job_alert(job_data, score, reason)
                except Exception as tg_err:
                    print(f"Gagal mengirim notifikasi Telegram: {tg_err}")
                    notif_status = "FAILED"
                # -----------------------------------
            else:
                new_status = "LOW_SCORE"
                score_to_save = score
                notif_status = "-"
                app_status = "-"
            
            # Update nilai ke dalam sel Excel
            ws.cell(row=row, column=11, value=new_status)          # Evaluation Status (Kolom 11)
            ws.cell(row=row, column=12, value=score_to_save)        # AI Score (Kolom 12)
            ws.cell(row=row, column=13, value=reason)               # AI Reason (Kolom 13)
            ws.cell(row=row, column=14, value=notif_status)         # Notification Status (Kolom 14)
            ws.cell(row=row, column=15, value=app_status)           # Application Status (Kolom 15)
            ws.cell(row=row, column=16, value="-")                  # Applied Date (Kolom 16)
            
            evaluated_count += 1
            print(f" -> Skor AI: {score_to_save} | Status: {new_status} | Alasan: {reason}\n")
            
            # Jeda untuk mematuhi rate limit API Groq
            await asyncio.sleep(2)
            
    wb.save(EXCEL_FILE_PATH)
    wb.close()
    print(f"=== PROSES SELESAI. {evaluated_count} lowongan berhasil dievaluasi oleh AI! ===")

if __name__ == "__main__":
    asyncio.run(main())