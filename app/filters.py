import logging
import re

def apply_deterministic_filters(listings: list, profile: dict) -> list:
    """
    FR-04: Menerapkan aturan hard filter berdasarkan profile.json.
    Hanya menyaring kata kunci terlarang (excluded keywords) pada JUDUL pekerjaan.
    """
    filtered_listings = []
    
    # Hanya ambil kata kunci terlarang dari profile.json
    excluded_keywords = [kw.lower() for kw in profile.get("excluded_keywords", [])]
    
    logging.info("=== MENJALANKAN HARD FILTER (DETERMINISTIC FILTER) ===")
    
    for job in listings:
        title_lower = job.get("title", "").lower()
        
        # 1. Cek Excluded Keywords HANYA pada JUDUL Pekerjaan
        is_excluded = False
        matched_keyword = ""
        
        for ex in excluded_keywords:
            pattern = r'\b' + re.escape(ex) + r'\b'
            if re.search(pattern, title_lower):
                is_excluded = True
                matched_keyword = ex
                break
                
        if is_excluded:
            job["evaluation_status"] = "FILTERED_OUT"
            job["reason_filtered"] = f"Judul mengandung kata terlarang: '{matched_keyword}'"
            logging.info(f"[FILTER OUT] '{job['title']}' di {job['company']} -> Kata terlarang: '{matched_keyword}'")
            continue
            
        # Jika lolos (bukan magang/intern/unpaid), tandai PENDING_AI
        job["evaluation_status"] = "PENDING_AI"
        job["reason_filtered"] = "Lolos filter awal."
        filtered_listings.append(job)
        logging.info(f"[LOLOS FILTER] '{job['title']}' di {job['company']} -> Siap dikirim ke AI Evaluator.")
        
    logging.info(f"=== FILTER SELESAI. {len(filtered_listings)} dari {len(listings)} lowongan lolos ke tahap AI. ===")
    return filtered_listings