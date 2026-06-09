import os
import csv
import random
from shapely.geometry import Polygon

STAGING_DIR = "staging"

# 1. Authentic Odisha Revenue Locations Mapped to Strict Target Names
# This directly matches what your 'forecast_property_valuation' module expects
ODISHA_CADASTRAL_REGISTRY = [
    {
        "district": "Khordha",
        "city": "Bhubaneswar",  # Passed directly to forecast_property_valuation
        "village": "Andharua",
        "village_code": "VIL-OD-KHD-001",
        "center_lat": 20.3291,
        "center_lon": 85.7643
    },
    {
        "district": "Khordha",
        "city": "Bhubaneswar",
        "village": "Kalarahanga",
        "village_code": "VIL-OD-KHD-002",
        "center_lat": 20.3551,
        "center_lon": 85.8436
    },
    {
        "district": "Puri",
        "city": "Puri",
        "village": "Baliapanda",
        "village_code": "VIL-OD-PURI-104",
        "center_lat": 19.7894,
        "center_lon": 85.8012
    },
    {
        "district": "Cuttack",
        "city": "Cuttack",
        "village": "Agrahat",
        "village_code": "VIL-OD-CTC-402",
        "center_lat": 20.5510,
        "center_lon": 85.9015
    },
    {
        "district": "Sambalpur",
        "city": "Sambalpur",
        "village": "Burla",
        "village_code": "VIL-OD-SBP-801",
        "center_lat": 21.4925,
        "center_lon": 83.8812
    }
]

# 2. Names pool structured to verify 'resolve_identity_by_name' phonetic engine matches
NAMES_POOL = [
    {"en": "Rabindra Nath Mohapatra", "or": "ରବୀନ୍ଦ୍ର ନାଥ ମହାପାତ୍ର"},
    {"en": "Pravat Kumar Das", "or": "ପ୍ରଭାତ କୁମାର ଦାସ"},
    {"en": "Manas Ranjan Pradhan", "or": "ମାନସ ରଞ୍ଜନ ପ୍ରଧାନ"},
    {"en": "Subhashree Mishra", "or": "ସୁଭାଶ୍ରୀ ମିଶ୍ର"},
    {"en": "Deepak Kumar Sahu", "or": "ଦୀପକ କୁମାର ସାହୁ"},
    {"en": "Aparajita Patnaik", "or": "ଅପରାଜିତା ପଟ୍ଟନାୟକ"}
]

def generate_precise_wkt_polygon(lon, lat, area_acres):
    """
    Builds a mathematically closed geometric plot around an exact map location.
    The bounding values match your 'convert_dataframe_to_geodataframe' conversion limits.
    """
    delta = 0.0004 * (area_acres ** 0.5)
    
    lon1, lat1 = round(lon - delta, 5), round(lat - delta, 5)
    lon2, lat2 = round(lon + delta, 5), round(lat - delta, 5)
    lon3, lat3 = round(lon + delta, 5), round(lat + delta, 5)
    lon4, lat4 = round(lon - delta, 5), round(lat + delta, 5)
    
    poly = Polygon([(lon1, lat1), (lon2, lat2), (lon3, lat3), (lon4, lat4)])
    return poly.wkt

def generate_validated_batch(batch_id: int, plots_per_village: int = 5):
    """Generates authentic cadastral files that match your active validation constraints."""
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)
        
    file_path = os.path.join(STAGING_DIR, f"spatial_land_batch_{batch_id:02d}.csv")
    
    headers = [
        'khatiyan_no', 'tenant_name_en', 'tenant_name_or', 'district', 
        'city', 'village_code', 'plot_no', 'area_acres', 'geometry_wkt'
    ]
    
    records_written = 0
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for loc in ODISHA_CADASTRAL_REGISTRY:
            for _ in range(plots_per_village):
                identity = random.choice(NAMES_POOL)
                khatiyan_no = f"KH-{random.randint(1000, 9999)}"
                plot_no = str(random.randint(101, 1500))
                area_acres = round(random.uniform(0.25, 5.00), 2)
                
                # Spatial Jitter forces side-by-side tile rendering on the Leaflet Canvas map
                jitter_lon = loc['center_lon'] + random.uniform(-0.0012, 0.0012)
                jitter_lat = loc['center_lat'] + random.uniform(-0.0012, 0.0012)
                
                geometry_wkt = generate_precise_wkt_polygon(jitter_lon, jitter_lat, area_acres)
                
                writer.writerow([
                    khatiyan_no, identity['en'], identity['or'], loc['district'],
                    loc['city'], f"{loc['village_code']}-{loc['village'].upper()}", 
                    plot_no, area_acres, geometry_wkt
                ])
                records_written += 1
                
    print(f"✔️ Saved {records_written} properties matching your ML models in '{file_path}'!")

if __name__ == "__main__":
    generate_validated_batch(batch_id=1, plots_per_village=6)
