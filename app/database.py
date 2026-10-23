import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import logging

# Nama file Excel penyimpanan utama
EXCEL_FILE_PATH = os.path.join("data", "job_opportunities.xlsx")

def initialize_database():
    """
    Membuat folder 'data' dan file Excel beserta header kolomnya 
    jika file tersebut belum ada.
    """
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists(EXCEL_FILE_PATH):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Job Openings"
        
        # Header Kolom Standar (Ditambahkan Description dan Work Type)
        # headers = [
        #     "Job ID", "Search Role", "Title", "Company", "Location", 
        #     "Salary", "Date Posted", "URL", "Description", "Work Type", 
        #     "Evaluation Status", "AI Score", "AI Reason", "Notification Status"
        # ]
        headers = [
            "Job ID", "Search Role", "Title", "Company", "Location", 
            "Salary", "Date Posted", "URL", "Description", "Work Type", 
            "Evaluation Status", "AI Score", "AI Reason", "Notification Status", 
            "Application Status", "Applied Date"
        ]
        ws.append(headers)
        
        # Styling Header agar terlihat profesional (Neo-Brutalist / Clean Modern)
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            
        wb.save(EXCEL_FILE_PATH)
        logging.info(f"Database Excel baru berhasil dibuat di: {EXCEL_FILE_PATH}")

def load_existing_job_ids() -> set:
    """
    Memuat semua Job ID yang sudah pernah disimpan sebelumnya 
    untuk mencegah duplikasi data (Deduplication).
    """
    initialize_database()
    existing_ids = set()
    
    wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
    ws = wb.active
    
    # Membaca kolom Job ID (kolom ke-1) mulai baris kedua
    for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
        cell_value = row[0].value
        if cell_value:
            existing_ids.add(str(cell_value))
            
    wb.close()
    return existing_ids

def save_jobs_to_excel(jobs: list):
    """
    Menyimpan daftar lowongan baru ke dalam file Excel.
    Mengabaikan lowongan yang Job ID-nya sudah ada di dalam file (duplikat).
    """
    initialize_database()
    existing_ids = load_existing_job_ids()
    
    wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
    ws = wb.active
    
    added_count = 0
    skipped_count = 0
    
    for job in jobs:
        job_id = str(job.get("job_id", ""))
        
        if job_id in existing_ids:
            skipped_count += 1
            continue
            
        # Format baris data sesuai urutan header baru (termasuk Description & Work Type)
        row_data = [
            job.get("job_id", ""),
            job.get("search_role", ""),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("salary_text", "Unknown"),
            job.get("date_posted", "Unknown"),
            job.get("url", ""),
            job.get("description", "N/A"),
            job.get("work_type", "N/A"),
            job.get("evaluation_status", "NEW"),
            job.get("ai_score", 0),
            job.get("ai_reason", "-"),
            job.get("notification_status", "NOT_REQUIRED")
        ]
        
        ws.append(row_data)
        existing_ids.add(job_id)
        added_count += 1
        
    wb.save(EXCEL_FILE_PATH)
    wb.close()
    
    logging.info(f"[DATABASE] Berhasil menyimpan {added_count} lowongan baru ke Excel. ({skipped_count} duplikat dilewati).")