import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split

print("Loading the new CATNAT 2023-2025 dataset (Reading all sheets)...")
# sheet_name=None reads ALL tabs in the Excel file at once
all_sheets = pd.read_excel('/home/sensei/Downloads/CATNAT_2023_2025.xlsx', sheet_name=None)
# Combine all the sheets into one giant dataset
df = pd.concat(all_sheets.values(), ignore_index=True)

# 1. Clean the Wilaya and Commune columns (Split "18 - JIJEL" into just "JIJEL")
df[['wilaya_code', 'wilaya_name']] = df['WILAYA'].str.split(' - ', n=1, expand=True)
df[['commune_code', 'commune_name']] = df['COMMUNE'].str.split(' - ', n=1, expand=True)

# Fill missing text with 'Inconnu'
df['TYPE'] = df['TYPE'].fillna('Inconnu')
df['wilaya_name'] = df['wilaya_name'].fillna('Inconnu')
df['commune_name'] = df['commune_name'].fillna('Inconnu')

# FIX THE COMMA ERROR: Replace French commas ',' with English dots '.'
df['CAPITAL_ASSURE'] = df['CAPITAL_ASSURE'].astype(str).str.replace(',', '.').str.strip()
df['PRIME_NETTE'] = df['PRIME_NETTE'].astype(str).str.replace(',', '.').str.strip()

# Now it is safe to convert them to numbers
df['CAPITAL_ASSURE'] = pd.to_numeric(df['CAPITAL_ASSURE'], errors='coerce')
df['PRIME_NETTE'] = pd.to_numeric(df['PRIME_NETTE'], errors='coerce')

# Drop rows if we don't have the price or capital
df = df.dropna(subset=['PRIME_NETTE', 'CAPITAL_ASSURE']) 

# 2. RPA 99 COMPLETE MAPPING (All 48 Wilayas)
def get_rpa99_zone(wilaya):
    w = str(wilaya).upper().strip()
    if w in["CHLEF", "BLIDA", "ALGER", "BOUMERDES", "TIPAZA", "AIN DEFLA"]: return 3
    elif w in["ADRAR", "BECHAR", "TAMANRASSET", "OUARGLA", "EL BAYADH", "ILLIZI", "TINDOUF", "EL OUED", "GHARDAIA"]: return 0
    elif w in["LAGHOUAT", "OUM EL BOUAGHI", "BATNA", "BISKRA", "TEBESSA", "TLEMCEN", "TIARET", "DJELFA", "SAIDA", "SIDI BEL ABBES", "KHENCHELA", "SOUK AHRAS"]: return 1
    else: return 2

df['seismic_zone_rpa99'] = df['wilaya_name'].apply(get_rpa99_zone)

# 3. Train the AI Model
print(f"Data cleaned! Training CatBoost Model V2 on {len(df)} rows...")
X = df[['TYPE', 'wilaya_name', 'commune_name', 'CAPITAL_ASSURE', 'seismic_zone_rpa99']]
y = df['PRIME_NETTE']

cat_features =['TYPE', 'wilaya_name', 'commune_name']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = CatBoostRegressor(iterations=300, learning_rate=0.1, depth=6, loss_function='RMSE')
model.fit(X_train, y_train, cat_features=cat_features, eval_set=(X_test, y_test), verbose=50)

# Save the new model
model.save_model('gam_catboost_v2.cbm')
print("Success! V2 Model saved as 'gam_catboost_v2.cbm'")