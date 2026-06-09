import os
import sqlite3
import pandas as pd
from shapely import wkt
from modules.database import initialize_database

DB_PATH = os.path.join("data", "odisha_land_registry.db")
STAGING_DIR = "staging"

def clean_and_validate_spatial_batch(file_path: str) -> pd.DataFrame:
    """Ingests and validates multi-city dataset structures."""
    print(f"📁 Processing Active RoR File: {file_path}")
    df = pd.read_csv(file_path, dtype=str)
    
    required_fields = ['khatiyan_no', 'tenant_name_en', 'tenant_name_or', 'district', 'city', 'village_code', 'plot_no', 'area_acres', 'geometry_wkt']
    df = df.dropna(subset=[f for f in required_fields if f in df.columns])
    
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        
    if 'tenant_name_en' in df.columns:
        df['tenant_name_en'] = df['tenant_name_en'].str.title()
    if 'district' in df.columns:
        df['district'] = df['district'].str.title()
    if 'city' in df.columns:
        df['city'] = df['city'].str.title()
    if 'area_acres' in df.columns:
        df['area_acres'] = pd.to_numeric(df['area_acres'], errors='coerce')
        
    df = df.dropna(subset=['khatiyan_no', 'tenant_name_en', 'plot_no', 'village_code', 'geometry_wkt', 'district', 'city'])
    df = df[df['area_acres'] > 0]
    
    valid_spatial_rows = []
    for _, row in df.iterrows():
        try:
            shape = wkt.loads(row['geometry_wkt'])
            valid_spatial_rows.append(shape.is_valid)
        except Exception:
            valid_spatial_rows.append(False)
            
    return df[valid_spatial_rows]

def execute_spatial_batch_insert(cleaned_df: pd.DataFrame):
    if cleaned_df.empty:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    records = [
        (r['khatiyan_no'], r['tenant_name_en'], r['tenant_name_or'], r['district'], r['city'], r['village_code'], r['plot_no'], float(r['area_acres']), r['geometry_wkt'])
        for _, r in cleaned_df.iterrows()
    ]
    try:
        cursor.execute("BEGIN TRANSACTION;")
        cursor.executemany("""
            INSERT INTO active_ror (khatiyan_no, tenant_name_en, tenant_name_or, district, city, village_code, plot_no, area_acres, geometry_wkt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, records)
        conn.commit()
        print(f"✔️ Successfully saved {len(cleaned_df)} multi-city vector records.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Transaction failure: {e}")
    finally:
        conn.close()

def run_pipeline():
    initialize_database()
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)
        return

    for file_name in os.listdir(STAGING_DIR):
        full_path = os.path.join(STAGING_DIR, file_name)
        if file_name.startswith("spatial_land_batch") and file_name.endswith(".csv"):
            cleaned = clean_and_validate_spatial_batch(full_path)
            execute_spatial_batch_insert(cleaned)
            os.remove(full_path)

if __name__ == "__main__":
    run_pipeline()
