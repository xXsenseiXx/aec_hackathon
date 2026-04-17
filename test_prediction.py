import pandas as pd
from catboost import CatBoostRegressor

# 1. Load the trained AI brain
print("Loading AI Model...")
model = CatBoostRegressor()
model.load_model('gam_catboost_model.cbm')

# 2. Create a fake "New Client" who wants insurance
# Let's test a Commercial building in CHLEF (Zone 3 - High Risk) worth 10,000,000 DZD
new_client = pd.DataFrame({
    'TYPE': ['2 - Installation Commerciale'],
    'wilaya_name': ['CHLEF'],
    'commune_name':['OUED SLY'],
    'VALEUR_ASSUREE': [10000000.0],
    'seismic_zone_rpa99': [3]
})

# 3. Ask the AI to predict the Premium (Risk Cost)
predicted_price = model.predict(new_client)

print("\n--- GAM AI PREDICTION ---")
print(f"Building Type: {new_client['TYPE'][0]}")
print(f"Location: {new_client['wilaya_name'][0]} (Seismic Zone {new_client['seismic_zone_rpa99'][0]})")
print(f"Declared Value: {new_client['VALEUR_ASSUREE'][0]:,.2f} DZD")
print(f">>> RECOMMENDED INSURANCE PREMIUM: {predicted_price[0]:,.2f} DZD")
print("-------------------------\n")