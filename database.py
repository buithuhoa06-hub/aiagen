import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "thienminh_rfp.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tender_dossiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dossier_code TEXT UNIQUE,
        client_name TEXT,
        project_name TEXT,
        deadline_days INTEGER,
        discount_requested REAL,
        total_list_price REAL,
        final_bid_price REAL,
        approval_level TEXT,
        status TEXT, -- PENDING_CLARIFICATION, PENDING_APPROVAL, APPROVED, ISSUED, REJECTED
        compliance_summary TEXT, -- JSON
        pricing_details TEXT, -- JSON
        approval_notes TEXT,
        created_at TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_code TEXT UNIQUE,
        client_name TEXT,
        contact_email TEXT,
        source TEXT,
        raw_sheet TEXT,
        cleaned_data TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_dossier(data: dict) -> str:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    code = f"TM-{datetime.now().strftime('%Y%m')}-{os.urandom(2).hex().upper()}"
    
    cursor.execute("""
    INSERT INTO tender_dossiers (
        dossier_code, client_name, project_name, deadline_days,
        discount_requested, total_list_price, final_bid_price,
        approval_level, status, compliance_summary, pricing_details,
        approval_notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code,
        data.get("client_name"),
        data.get("project_name"),
        data.get("deadline_days"),
        data.get("discount_requested"),
        data.get("total_list_price"),
        data.get("final_bid_price"),
        data.get("approval_level"),
        data.get("status"),
        json.dumps(data.get("compliance_summary", {}), ensure_ascii=False),
        json.dumps(data.get("pricing_details", {}), ensure_ascii=False),
        data.get("approval_notes", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return code

def get_all_dossiers():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tender_dossiers ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_dossier_status(code: str, status: str, notes: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE tender_dossiers 
    SET status = ?, approval_notes = ?
    WHERE dossier_code = ?
    """, (status, notes, code))
    conn.commit()
    conn.close()

def save_customer_request(client_name: str, contact_email: str, source: str, raw_sheet: dict, cleaned_data: dict) -> str:
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    code = f"KH-{datetime.now().strftime('%m%d')}-{os.urandom(2).hex().upper()}"
    cursor.execute("""
    INSERT INTO customer_requests (
        request_code, client_name, contact_email, source,
        raw_sheet, cleaned_data, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code,
        client_name,
        contact_email,
        source,
        json.dumps(raw_sheet, ensure_ascii=False),
        json.dumps(cleaned_data, ensure_ascii=False),
        "NEW",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()
    return code

def get_customer_requests():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_requests ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["raw_sheet"] = json.loads(d["raw_sheet"] or "{}")
            d["cleaned_data"] = json.loads(d["cleaned_data"] or "{}")
        except Exception:
            pass
        result.append(d)
    return result

def mark_customer_request_status(request_code: str, status: str = "PROCESSED"):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customer_requests SET status = ? WHERE request_code = ?", (status, request_code))
    conn.commit()
    conn.close()


