import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import numpy as np

# ── 1. Load data ────────────────────────────────────────────────────────────
print("Loading cleaned data...")
df = pd.read_csv('gam_cleaned_data.csv')
print(f"Rows before cleaning : {len(df)}")

# ── 2. Drop rows where the target is missing ────────────────────────────────
df = df.dropna(subset=['PRIME_NETTE'])
print(f"Rows after dropping missing PRIME_NETTE : {len(df)}")

# ── 3. Fix missing values ───────────────────────────────────────────────────
# Categorical columns → fill with 'Inconnu'
df['TYPE']         = df['TYPE'].fillna('Inconnu')
df['wilaya_name']  = df['wilaya_name'].fillna('Inconnu')
df['commune_name'] = df['commune_name'].fillna('Inconnu')

# Numeric columns → fill with 0
df['VALEUR_ASSUREE']    = df['VALEUR_ASSUREE'].fillna(0)
df['seismic_zone_rpa99'] = df['seismic_zone_rpa99'].fillna(0)

# ── 4. Features & target ────────────────────────────────────────────────────
FEATURES = ['TYPE', 'wilaya_name', 'commune_name', 'VALEUR_ASSUREE', 'seismic_zone_rpa99']
TARGET   = 'PRIME_NETTE'
CAT_FEATURES = ['TYPE', 'wilaya_name', 'commune_name']

X = df[FEATURES]
y = df[TARGET]

# ── 5. Train / test split ───────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

# ── 6. Train the model ──────────────────────────────────────────────────────
print("\nTraining CatBoost model...")
model = CatBoostRegressor(
    iterations=300,
    learning_rate=0.1,
    depth=6,
    loss_function='RMSE',
    random_seed=42,
)
model.fit(
    X_train, y_train,
    cat_features=CAT_FEATURES,
    eval_set=(X_test, y_test),
    verbose=50,
)

# ── 7. Evaluate ─────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
mae  = mean_absolute_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)
rmse = np.sqrt(((y_test - y_pred) ** 2).mean())

print(f"\n── Evaluation on test set ──────────────────")
print(f"  MAE  : {mae:,.2f}")
print(f"  RMSE : {rmse:,.2f}")
print(f"  R²   : {r2:.4f}")

# ── 8. Save ─────────────────────────────────────────────────────────────────
model.save_model('gam_catboost_model.cbm')
print("\nSuccess! Model saved as 'gam_catboost_model.cbm'")