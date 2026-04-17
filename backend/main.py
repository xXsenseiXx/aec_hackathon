"""
GAM Assurances - CATNAT Risk Dashboard API
FastAPI Backend with CatBoost Model + RPA 99 Business Logic
"""
import os
import sys
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from catboost import CatBoostRegressor

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "gam_catboost_v2.cbm")

# --- App ---
app = FastAPI(title="GAM CATNAT Risk API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class PredictRequest(BaseModel):
    type: str
    wilaya: str
    commune: str
    capital_assure: float

class MonteCarloRequest(BaseModel):
    wilaya: str
    capital_assure: float
    n_simulations: int = 1000

# --- 48 Wilayas + RPA99 Zones + GPS ---
WILAYAS_DATA = {
    "ADRAR": {"zone": 0, "lat": 27.874, "lon": -0.293},
    "CHLEF": {"zone": 3, "lat": 36.165, "lon": 1.334},
    "LAGHOUAT": {"zone": 1, "lat": 33.800, "lon": 2.865},
    "OUM EL BOUAGHI": {"zone": 1, "lat": 35.875, "lon": 7.113},
    "BATNA": {"zone": 1, "lat": 35.555, "lon": 6.174},
    "BEJAIA": {"zone": 2, "lat": 36.755, "lon": 5.084},
    "BISKRA": {"zone": 1, "lat": 34.850, "lon": 5.728},
    "BECHAR": {"zone": 0, "lat": 31.616, "lon": -2.215},
    "BLIDA": {"zone": 3, "lat": 36.470, "lon": 2.827},
    "BOUIRA": {"zone": 2, "lat": 36.374, "lon": 3.902},
    "TAMANRASSET": {"zone": 0, "lat": 22.785, "lon": 5.522},
    "TEBESSA": {"zone": 1, "lat": 35.404, "lon": 8.124},
    "TLEMCEN": {"zone": 1, "lat": 34.878, "lon": -1.315},
    "TIARET": {"zone": 1, "lat": 35.371, "lon": 1.316},
    "TIZI OUZOU": {"zone": 2, "lat": 36.711, "lon": 4.045},
    "ALGER": {"zone": 3, "lat": 36.753, "lon": 3.058},
    "DJELFA": {"zone": 1, "lat": 34.672, "lon": 3.263},
    "JIJEL": {"zone": 2, "lat": 36.820, "lon": 5.766},
    "SETIF": {"zone": 2, "lat": 36.189, "lon": 5.414},
    "SAIDA": {"zone": 1, "lat": 34.825, "lon": 0.151},
    "SKIKDA": {"zone": 2, "lat": 36.876, "lon": 6.907},
    "SIDI BEL ABBES": {"zone": 1, "lat": 35.189, "lon": -0.630},
    "ANNABA": {"zone": 2, "lat": 36.900, "lon": 7.766},
    "GUELMA": {"zone": 2, "lat": 36.462, "lon": 7.426},
    "CONSTANTINE": {"zone": 2, "lat": 36.365, "lon": 6.614},
    "MEDEA": {"zone": 2, "lat": 36.264, "lon": 2.753},
    "MOSTAGANEM": {"zone": 2, "lat": 35.931, "lon": 0.089},
    "M SILA": {"zone": 2, "lat": 35.705, "lon": 4.541},
    "MASCARA": {"zone": 2, "lat": 35.398, "lon": 0.140},
    "OUARGLA": {"zone": 0, "lat": 31.949, "lon": 5.325},
    "ORAN": {"zone": 2, "lat": 35.691, "lon": -0.641},
    "EL BAYADH": {"zone": 0, "lat": 33.680, "lon": 1.020},
    "ILLIZI": {"zone": 0, "lat": 26.483, "lon": 8.466},
    "BORDJ BOU ARRERIDJ": {"zone": 2, "lat": 36.073, "lon": 4.761},
    "BOUMERDES": {"zone": 3, "lat": 36.760, "lon": 3.473},
    "EL TARF": {"zone": 2, "lat": 36.767, "lon": 8.313},
    "TINDOUF": {"zone": 0, "lat": 27.671, "lon": -8.147},
    "TISSEMSILT": {"zone": 2, "lat": 35.607, "lon": 1.810},
    "EL OUED": {"zone": 0, "lat": 33.368, "lon": 6.853},
    "KHENCHELA": {"zone": 1, "lat": 35.435, "lon": 7.143},
    "SOUK AHRAS": {"zone": 1, "lat": 36.286, "lon": 7.951},
    "TIPAZA": {"zone": 3, "lat": 36.589, "lon": 2.443},
    "MILA": {"zone": 2, "lat": 36.450, "lon": 6.264},
    "AIN DEFLA": {"zone": 3, "lat": 36.265, "lon": 1.939},
    "NAAMA": {"zone": 2, "lat": 33.267, "lon": -0.316},
    "AIN TEMOUCHENT": {"zone": 2, "lat": 35.297, "lon": -1.140},
    "GHARDAIA": {"zone": 0, "lat": 32.490, "lon": 3.673},
    "RELIZANE": {"zone": 2, "lat": 35.737, "lon": 0.555},
}

ZONE_LABELS = {
    0: "Zone 0 (Very Low)",
    1: "Zone I (Low)",
    2: "Zone II (Medium)",
    3: "Zone III (High)",
}

MULTIPLIERS = {0: 0.8, 1: 1.0, 2: 1.3, 3: 1.8}

# --- Load Model + CSVs at Startup ---
print("Loading CatBoost model...")
model = CatBoostRegressor()
model.load_model(MODEL_PATH)
print("Model loaded!")

def load_csv(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

hotspots_df = load_csv("hotspots_identified.csv")
if not hotspots_df.empty:
    hotspots_df["wilaya_clean"] = hotspots_df["WILAYA"].str.split(" - ").str[-1].str.strip()
    hotspots_df["commune_clean"] = hotspots_df["COMMUNE"].str.split(" - ").str[-1].str.strip()

pml_df = load_csv("pml_scenarios.csv")
portfolio_df = load_csv("portfolio_3d_segmentation.csv")
stress_df = load_csv("stress_test_scenarios.csv")
gis_df = load_csv("gis_commune_heatmap.csv")

print("All data loaded!")

# ═══════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════

@app.get("/api/wilayas")
def get_wilayas():
    """Return all 48 wilayas with zone, GPS, labels for the map."""
    result = []
    for name, data in WILAYAS_DATA.items():
        z = data["zone"]
        if z == 3:
            color = [255, 50, 50, 200]
            radius = 35000
        elif z == 2:
            color = [255, 165, 0, 200]
            radius = 25000
        elif z == 1:
            color = [255, 255, 0, 200]
            radius = 15000
        else:
            color = [0, 220, 100, 200]
            radius = 10000
        result.append({
            "name": name,
            "lat": data["lat"],
            "lon": data["lon"],
            "zone": z,
            "zone_label": ZONE_LABELS[z],
            "color": color,
            "radius": radius,
        })
    return result


@app.post("/api/predict")
def predict_premium(req: PredictRequest):
    """Predict insurance premium using CatBoost + RPA99 multiplier."""
    wilaya_upper = req.wilaya.upper().strip()
    w_data = WILAYAS_DATA.get(wilaya_upper, {"zone": 1})
    zone = w_data["zone"]

    # CatBoost prediction
    input_df = pd.DataFrame({
        "TYPE": [req.type],
        "wilaya_name": [wilaya_upper],
        "commune_name": [req.commune.upper().strip()],
        "CAPITAL_ASSURE": [req.capital_assure],
        "seismic_zone_rpa99": [zone],
    })
    base_prediction = float(model.predict(input_df)[0])

    # Apply RPA99 risk multiplier
    multiplier = MULTIPLIERS[zone]
    adjusted = base_prediction * multiplier
    final_premium = max(1500.0, adjusted)

    # Hotspot check
    hotspot_warning = None
    if not hotspots_df.empty:
        commune_upper = req.commune.upper().strip()
        match = hotspots_df[
            (hotspots_df["wilaya_clean"] == wilaya_upper)
            & (hotspots_df["commune_clean"] == commune_upper)
        ]
        if not match.empty:
            row = match.iloc[0]
            flag = str(row.get("Concentration_Flag", ""))
            pct = str(row.get("Pct_Total_Capital", ""))
            if "CRITICAL" in flag:
                hotspot_warning = {
                    "level": "CRITICAL",
                    "message": f"GAM has a CRITICAL concentration ({pct}% of total capital) in {commune_upper}. Recommendation: Require Reinsurance.",
                }
            elif "HIGH" in flag:
                hotspot_warning = {
                    "level": "HIGH",
                    "message": f"GAM has a HIGH concentration ({pct}% of total capital) in {commune_upper}. Monitor exposure closely.",
                }

    return {
        "base_prediction": round(base_prediction, 2),
        "zone": zone,
        "zone_label": ZONE_LABELS[zone],
        "multiplier": multiplier,
        "final_premium": round(final_premium, 2),
        "hotspot_warning": hotspot_warning,
    }


@app.post("/api/monte-carlo")
def monte_carlo(req: MonteCarloRequest):
    """Run Monte Carlo simulation for disaster loss estimation."""
    wilaya_upper = req.wilaya.upper().strip()
    w_data = WILAYAS_DATA.get(wilaya_upper, {"zone": 1})
    zone = w_data["zone"]
    n = req.n_simulations

    if zone == 3:
        damage_pct = np.random.triangular(0.1, 0.4, 0.9, n)
    elif zone == 2:
        damage_pct = np.random.triangular(0.05, 0.2, 0.5, n)
    elif zone == 1:
        damage_pct = np.random.triangular(0.01, 0.05, 0.2, n)
    else:
        damage_pct = np.random.triangular(0.001, 0.01, 0.05, n)

    losses = (damage_pct * req.capital_assure).tolist()
    avg_loss = float(np.mean(losses))
    worst_case_95 = float(np.percentile(losses, 95))
    median_loss = float(np.median(losses))

    return {
        "zone": zone,
        "zone_label": ZONE_LABELS[zone],
        "n_simulations": n,
        "losses": [round(l, 2) for l in losses],
        "avg_loss": round(avg_loss, 2),
        "worst_case_95": round(worst_case_95, 2),
        "median_loss": round(median_loss, 2),
    }


@app.get("/api/hotspots")
def get_hotspots():
    """Return portfolio concentration hotspots."""
    if hotspots_df.empty:
        return []
    cols = ["WILAYA", "COMMUNE", "ZONE_SISMIQUE", "Policy_Count",
            "Total_Capital", "Pct_Total_Capital", "Concentration_Flag"]
    available = [c for c in cols if c in hotspots_df.columns]
    return hotspots_df[available].to_dict(orient="records")


@app.get("/api/pml-scenarios")
def get_pml():
    """Return Probable Maximum Loss scenarios."""
    if pml_df.empty:
        return []
    return pml_df.to_dict(orient="records")


@app.get("/api/portfolio")
def get_portfolio():
    """Return portfolio 3D segmentation data."""
    if portfolio_df.empty:
        return []
    return portfolio_df.head(30).to_dict(orient="records")


@app.get("/api/stress-test")
def get_stress_test():
    """Return stress test scenario data."""
    if stress_df.empty:
        return []
    return stress_df.to_dict(orient="records")


@app.get("/api/gis-heatmap")
def get_gis_heatmap():
    """Return top 50 commune-level risk data for heatmap."""
    if gis_df.empty:
        return []
    return gis_df.head(50).to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
