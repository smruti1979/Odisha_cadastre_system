import time
from geopy.geocoders import Nominatim

# FIX 1: Change user_agent to a unique custom ID. Using generic strings results in 403/429 blocks.
geolocator = Nominatim(user_agent="odisha_cadastre_system_poc_registration_agent_12")

# FIX 2: Simplify the query. Nominatim processes clear, broader landmarks better than precise village-level addresses.
query = "Koraput, Odisha, India" 

try:
    print(f"Connecting to live endpoint for: '{query}'...")
    location = geolocator.geocode(query, timeout=10)
    
    if location:
        print("\n✅ Location Details Found Successfully!")
        print(f"Address: {location.address}")
        print(f"Latitude:  {location.latitude}")
        print(f"Longitude: {location.longitude}")
    else:
        print("\n❌ Location details could not be found. Check query strings.")
except Exception as e:
    print(f"\n⚠️ Connection Error: {e}")
