Execution Checklist:
Run the generation pipeline steps sequentially in your terminal to seed and view the data layers correctly:


# 1. Regenerates clean, non-overlapping dataset batches
python data_generator.py

# 2. Re-runs ROR string data validation and writes rows to the DB
python data_refresher.py

# 3. Boots up the unified AI Cadastral Multi-City Suite
streamlit run app.py


--
If you want to append a new village or city to ODISHA_CADASTRAL_REGISTRY without lookup errors, 
use this standalone setup block to find its coordinates beforehand:

add_ODISHA_CADASTRAL_REGISTRY.py

 python .\add_ODISHA_CADASTRAL_REGISTRY.py
Connecting to live endpoint for: 'Bhubaneswar, Odisha, India'...

✅ Location Details Found Successfully!
Latitude:  20.2602964
Longitude: 85.8394521
(.venv) PS C:\Learning\AI_Projects\Odisha_cadastre_system> python .\add_ODISHA_CADASTRAL_REGISTRY.py
Connecting to live endpoint for: 'Cuttack, Odisha, India'...

✅ Location Details Found Successfully!
Latitude:  20.4686
Longitude: 85.8792
(.venv) PS C:\Learning\AI_Projects\Odisha_cadastre_system> python .\add_ODISHA_CADASTRAL_REGISTRY.py
Connecting to live endpoint for: 'Sambalpur, Odisha, India'...

✅ Location Details Found Successfully!
Address: Sambalpur, Odisha, India
Latitude:  21.5570606
Longitude: 84.1528515
(.venv) PS C:\Learning\AI_Projects\Odisha_cadastre_system> python .\add_ODISHA_CADASTRAL_REGISTRY.py
Connecting to live endpoint for: 'Koraput, Odisha, India'...

✅ Location Details Found Successfully!
Address: Koraput, Odisha, India
Latitude:  18.7232023
Longitude: 82.6100596
(.venv) PS C:\Learning\AI_Projects\Odisha_cadastre_system> 
