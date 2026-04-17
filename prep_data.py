import pandas as pd
import numpy as np

# 1. Load the three Excel files
print("Loading data...")
df_2023 = pd.read_excel('data/catnat_2023.xlsx')
df_2024 = pd.read_excel('data/Catnat_2024.xlsx')
df_2025 = pd.read_excel('data/catnat_2025.xlsx')

# 2. Combine them into one big dataset
df = pd.concat([df_2023, df_2024, df_2025], ignore_index=True)

# This removes the 'É' and any hidden spaces so your code works perfectly
df.columns = df.columns.str.upper().str.replace('É', 'E').str.strip()

# 3. Clean the 'Wilaya' and 'commune_du_risque' columns
# They look like "2 - CHLEF". We want to split the number and the name.
df[['wilaya_code', 'wilaya_name']] = df['WILAYA'].str.split(' - ', n=1, expand=True)
df[['commune_code', 'commune_name']] = df['COMMUNE_DU_RISQUE'].str.split(' - ', n=1, expand=True)

# 4. Handle the "NULL" values in VALEUR_ASSUREE
# Replace the string "NULL" with standard pandas NaN
df['VALEUR_ASSUREE'] = df['VALEUR_ASSUREE'].replace('NULL', np.nan)
df['VALEUR_ASSUREE'] = pd.to_numeric(df['VALEUR_ASSUREE'], errors='coerce')

# Quick Fix for Missing Values:
# If Valeur Assuree is missing, we can estimate it based on the Prime Nette (Premium).
# Usually, the premium is a small percentage of the total value (e.g., 0.1%).
median_ratio = (df['PRIME_NETTE'] / df['VALEUR_ASSUREE']).median()
if pd.isna(median_ratio):
    median_ratio = 0.001 # Fallback assumption: premium is 0.1% of value

# Fill missing values based on this ratio
df['VALEUR_ASSUREE'] = df['VALEUR_ASSUREE'].fillna(df['PRIME_NETTE'] / median_ratio)

# 5. Add the RPA 99 Seismic Zones (The Secret Sauce!)
# According to the RPA 99 document, Chlef is high risk (Zone III), Mostaganem is Zone IIa, etc.
# We map the Wilaya Name to its danger zone.
def get_seismic_zone(wilaya):
    wilaya = str(wilaya).upper()
    if 'CHLEF' in wilaya: return 3 # Zone III (Very High)
    if 'ALGER' in wilaya: return 3 # Zone III
    if 'BOUMERDES' in wilaya: return 3 # Zone III
    if 'MOSTAGANEM' in wilaya: return 2 # Zone IIa
    if 'ORAN' in wilaya: return 2
    return 1 # Default to Zone I (Low Risk)

df['seismic_zone_rpa99'] = df['wilaya_name'].apply(get_seismic_zone)

# 6. Save the cleaned data for your Dashboard and AI guy
columns_to_keep =[
    'NUMERO_POLICE', 'TYPE', 'wilaya_name', 'commune_name', 
    'VALEUR_ASSUREE', 'PRIME_NETTE', 'seismic_zone_rpa99'
]
df_clean = df[columns_to_keep]

df_clean.to_csv('gam_cleaned_data.csv', index=False)
print("Data cleaning complete! Saved to gam_cleaned_data.csv")


