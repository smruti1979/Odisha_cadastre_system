import sqlite3
import pandas as pd
import os

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "odisha_land_registry.db")

def initialize_database():
    """Initializes standard property schemas along with system security audit log tables."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Active land records schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_ror (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            khatiyan_no TEXT NOT NULL,
            tenant_name_en TEXT NOT NULL,
            tenant_name_or TEXT NOT NULL,
            district TEXT NOT NULL,
            city TEXT NOT NULL,
            village_code TEXT NOT NULL,
            plot_no TEXT NOT NULL,
            area_acres REAL NOT NULL,
            geometry_wkt TEXT NOT NULL
        )
    """)
    
    # Ancestral lineage schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS land_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plot_no TEXT NOT NULL,
            village_code TEXT NOT NULL,
            owner_name TEXT NOT NULL,
            relationship_tier TEXT NOT NULL,
            transfer_year INTEGER NOT NULL,
            mutation_reason TEXT NOT NULL
        )
    """)
    
    # UPGRADED: Added api_latency_ms to track REST API performance metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT NOT NULL,
            user_role TEXT NOT NULL,
            action_type TEXT NOT NULL,
            search_string TEXT,
            accessed_plots TEXT,
            api_latency_ms REAL,
            event_hash TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def write_audit_entry(user_id: str, role: str, action: str, search_str: str, plots: str, latency: float, event_hash: str):
    """Commissions validated audit entry vectors directly into data files with latency data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO security_audit_log (user_id, user_role, action_type, search_string, accessed_plots, api_latency_ms, event_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, role, action, search_str, plots, latency, event_hash))
    conn.commit()
    conn.close()

def get_all_active_records() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM active_ror", conn)
    conn.close()
    return df

def get_admin_audit_logs() -> pd.DataFrame:
    """Returns historical records of system operations with API performance tracking columns."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT timestamp, user_id, user_role, action_type, search_string, accessed_plots, api_latency_ms 
        FROM security_audit_log 
        ORDER BY timestamp DESC
    """, conn)
    conn.close()
    return df