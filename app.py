import streamlit as st
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor
import pydeck as pdk  # We are using pydeck now for the 3D map!

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="GAM Assurances - Risk Dashboard", layout="wide")
st.title("🛡️ GAM Assurances: AI CATNAT Predictor")
st.markdown("Powered by CatBoost & RPA 99 (All 48 Wilayas)")

# --- 2. THE 48 WILAYAS & RPA99 DATA ---
WILAYAS_DATA = {
    "ADRAR": {"zone": 0, "lat": 27.874, "lon": -0.293}, "CHLEF": {"zone": 3, "lat": 36.165, "lon": 1.334},
    "LAGHOUAT": {"zone": 1, "lat": 33.800, "lon": 2.865}, "OUM EL BOUAGHI": {"zone": 1, "lat": 35.875, "lon": 7.113},
    "BATNA": {"zone": 1, "lat": 35.555, "lon": 6.174}, "BEJAIA": {"zone": 2, "lat": 36.755, "lon": 5.084},
    "BISKRA": {"zone": 1, "lat": 34.850, "lon": 5.728}, "BECHAR": {"zone": 0, "lat": 31.616, "lon": -2.215},
    "BLIDA": {"zone": 3, "lat": 36.470, "lon": 2.827}, "BOUIRA": {"zone": 2, "lat": 36.374, "lon": 3.902},
    "TAMANRASSET": {"zone": 0, "lat": 22.785, "lon": 5.522}, "TEBESSA": {"zone": 1, "lat": 35.404, "lon": 8.124},
    "TLEMCEN": {"zone": 1, "lat": 34.878, "lon": -1.315}, "TIARET": {"zone": 1, "lat": 35.371, "lon": 1.316},
    "TIZI OUZOU": {"zone": 2, "lat": 36.711, "lon": 4.045}, "ALGER": {"zone": 3, "lat": 36.753, "lon": 3.058},
    "DJELFA": {"zone": 1, "lat": 34.672, "lon": 3.263}, "JIJEL": {"zone": 2, "lat": 36.820, "lon": 5.766},
    "SETIF": {"zone": 2, "lat": 36.189, "lon": 5.414}, "SAIDA": {"zone": 1, "lat": 34.825, "lon": 0.151},
    "SKIKDA": {"zone": 2, "lat": 36.876, "lon": 6.907}, "SIDI BEL ABBES": {"zone": 1, "lat": 35.189, "lon": -0.630},
    "ANNABA": {"zone": 2, "lat": 36.900, "lon": 7.766}, "GUELMA": {"zone": 2, "lat": 36.462, "lon": 7.426},
    "CONSTANTINE": {"zone": 2, "lat": 36.365, "lon": 6.614}, "MEDEA": {"zone": 2, "lat": 36.264, "lon": 2.753},
    "MOSTAGANEM": {"zone": 2, "lat": 35.931, "lon": 0.089}, "M SILA": {"zone": 2, "lat": 35.705, "lon": 4.541},
    "MASCARA": {"zone": 2, "lat": 35.398, "lon": 0.140}, "OUARGLA": {"zone": 0, "lat": 31.949, "lon": 5.325},
    "ORAN": {"zone": 2, "lat": 35.691, "lon": -0.641}, "EL BAYADH": {"zone": 0, "lat": 33.680, "lon": 1.020},
    "ILLIZI": {"zone": 0, "lat": 26.483, "lon": 8.466}, "BORDJ BOU ARRERIDJ": {"zone": 2, "lat": 36.073, "lon": 4.761},
    "BOUMERDES": {"zone": 3, "lat": 36.760, "lon": 3.473}, "EL TARF": {"zone": 2, "lat": 36.767, "lon": 8.313},
    "TINDOUF": {"zone": 0, "lat": 27.671, "lon": -8.147}, "TISSEMSILT": {"zone": 2, "lat": 35.607, "lon": 1.810},
    "EL OUED": {"zone": 0, "lat": 33.368, "lon": 6.853}, "KHENCHELA": {"zone": 1, "lat": 35.435, "lon": 7.143},
    "SOUK AHRAS": {"zone": 1, "lat": 36.286, "lon": 7.951}, "TIPAZA": {"zone": 3, "lat": 36.589, "lon": 2.443},
    "MILA": {"zone": 2, "lat": 36.450, "lon": 6.264}, "AIN DEFLA": {"zone": 3, "lat": 36.265, "lon": 1.939},
    "NAAMA": {"zone": 2, "lat": 33.267, "lon": -0.316}, "AIN TEMOUCHENT": {"zone": 2, "lat": 35.297, "lon": -1.140},
    "GHARDAIA": {"zone": 0, "lat": 32.490, "lon": 3.673}, "RELIZANE": {"zone": 2, "lat": 35.737, "lon": 0.555}
}

zone_labels = {0: "Zone 0 (Very Low)", 1: "Zone I (Low)", 2: "Zone II (Medium)", 3: "Zone III (High)"}

# --- 3. LOAD DATA & AI MODEL ---
@st.cache_resource 
def load_model():
    # THIS is the function that was accidentally deleted! I put it back.
    model = CatBoostRegressor()
    try:
        model.load_model('gam_catboost_v2.cbm')
    except:
        st.error("Model file not found. Run train_v2.py first!")
    return model

@st.cache_data 
def load_hotspots():
    try:
        # Load your friend's CSV file (Make sure it's in the data/ folder!)
        df = pd.read_csv('data/hotspots_identified.csv')
        df['wilaya_clean'] = df['WILAYA'].str.split(' - ').str[-1].str.strip()
        df['commune_clean'] = df['COMMUNE'].str.split(' - ').str[-1].str.strip()
        return df
    except Exception as e:
        return pd.DataFrame() 

model = load_model()
hotspots_df = load_hotspots()

# --- 4. SIDEBAR INPUTS ---
st.sidebar.header("📝 New Policy Details")
b_type = st.sidebar.selectbox("Building Type",["Bien immobilier", "2 - Installation Commerciale", "1 - Installation Industrielle"])

wilaya = st.sidebar.selectbox("Wilaya", sorted(list(WILAYAS_DATA.keys())))
zone = WILAYAS_DATA[wilaya]["zone"] 

commune = st.sidebar.text_input("Commune", "ALGER")
valeur = st.sidebar.number_input("Capital Assuré (DZD)", min_value=100000, value=10000000, step=100000)

st.sidebar.info(f"📍 **RPA 99 Seismic Zone:** {zone} - {zone_labels[zone]}")

# --- 5. DASHBOARD ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 AI Premium Prediction")
    
    # Base AI calculation
    input_data = pd.DataFrame({
        'TYPE': [b_type], 'wilaya_name':[wilaya], 'commune_name': [commune],
        'CAPITAL_ASSURE': [valeur], 'seismic_zone_rpa99': [zone]
    })
    base_prediction = model.predict(input_data)[0]
    
    # RPA 99 Risk Multiplier (Fixes GAM's pricing!)
    multipliers = {0: 0.8, 1: 1.0, 2: 1.3, 3: 1.8}
    adjusted_premium = base_prediction * multipliers[zone]
    final_premium = max(1500.0, adjusted_premium)
    
    st.success(f"### Recommended Premium: {final_premium:,.2f} DZD")
    st.caption(f"Base AI Prediction: {base_prediction:,.2f} DZD | RPA 99 Zone {zone} Multiplier: x{multipliers[zone]}")

    # HOTSPOT WARNING (Reads from your friend's CSV!)
    if not hotspots_df.empty:
        # Check if the user's input matches the CSV
        match = hotspots_df[(hotspots_df['wilaya_clean'] == wilaya) & (hotspots_df['commune_clean'] == commune.upper())]
        
        if not match.empty:
            flag = str(match.iloc[0]['Concentration_Flag'])
            pct = str(match.iloc[0]['Pct_Total_Capital'])
            
            if "CRITICAL" in flag:
                st.error(f"🚨 **PORTFOLIO WARNING:** GAM has a **CRITICAL** concentration ({pct}% of total capital) in {commune}. Recommendation: Require Reinsurance.")
            elif "HIGH" in flag:
                st.warning(f"⚠️ **PORTFOLIO ALERT:** GAM has a **HIGH** concentration ({pct}% of total capital) in {commune}. Monitor exposure closely.")

    st.markdown("---")
    st.subheader("🎲 Monte Carlo Disaster Simulation")
    st.write(f"Simulate 1,000 random earthquake events in {wilaya} to predict GAM's potential financial loss.")
    
    if st.button("Run Simulation"):
        if zone == 3: damage_pct = np.random.triangular(0.1, 0.4, 0.9, 1000)
        elif zone == 2: damage_pct = np.random.triangular(0.05, 0.2, 0.5, 1000)
        elif zone == 1: damage_pct = np.random.triangular(0.01, 0.05, 0.2, 1000)
        else: damage_pct = np.random.triangular(0.001, 0.01, 0.05, 1000)
            
        losses = damage_pct * valeur
        st.warning(f"**Worst Case Loss (95th Percentile):** {np.percentile(losses, 95):,.2f} DZD")
        st.info(f"**Average Expected Loss:** {np.mean(losses):,.2f} DZD")
        st.line_chart(pd.DataFrame(losses, columns=["Simulated Loss (DZD)"]))

with col2:
    st.subheader("🗺️ 3D Seismic Risk Map of Algeria")
    
    # 1. Prepare data for Pydeck
    map_data =[]
    for w_name, w_data in WILAYAS_DATA.items():
        z = w_data["zone"]
        # Define Colors (R, G, B, Opacity) and physical Radii (in meters)
        if z == 3: color, rad =[255, 0, 0, 160], 35000       # Red
        elif z == 2: color, rad =[255, 165, 0, 160], 25000   # Orange
        elif z == 1: color, rad =[255, 255, 0, 160], 15000   # Yellow
        else: color, rad =[0, 255, 0, 160], 10000            # Green
            
        map_data.append({
            "name": w_name, "lat": w_data["lat"], "lon": w_data["lon"], 
            "radius": rad, "color": color, "zone_label": zone_labels[z]
        })
        
    df_map = pd.DataFrame(map_data)
    
    # 2. Create the Pydeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_map,
        pickable=True,
        opacity=0.8,
        stroked=False,
        filled=True,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
    )
    
    # 3. Create the 3D Camera View
    view_state = pdk.ViewState(
        latitude=32.0,
        longitude=3.0,
        zoom=4.8,
        pitch=45,  # <-- THIS creates the beautiful 3D tilt!
        bearing=0
    )
    
    # 4. Render the map
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Wilaya: {name}\n{zone_label}"},
        map_style="dark",  # <-- CHANGE THIS LINE TO JUST "dark" or "light"
    )
    
    st.pydeck_chart(r)