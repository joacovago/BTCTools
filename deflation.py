import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Roxom Purchasing Power Engine", layout="wide", page_icon="🛡️")

# --- CUSTOM CSS (Sovereign Aesthetic) ---
st.markdown("""
<style>
    .big-metric { font-size: 30px !important; font-weight: bold; }
    .stProgress > div > div > div > div { background-color: #00FFAA; }
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE (The Economic Truth) ---
# We model the divergence: Assets inflate faster than CPI.
data = {
    "Year": list(range(2015, 2027)),
    "BTC_Price": [312, 430, 1000, 7500, 3800, 11000, 47000, 28000, 42000, 65000, 95000, 120000],
    # Official CPI (The "Lie")
    "CPI_Index": [1.00, 1.01, 1.03, 1.05, 1.07, 1.08, 1.14, 1.22, 1.27, 1.31, 1.35, 1.39],
    # Asset Inflation (The Reality: Housing, Tuition, Healthcare)
    "Asset_Inflation_Index": [1.00, 1.05, 1.12, 1.20, 1.28, 1.40, 1.65, 1.85, 2.00, 2.15, 2.30, 2.45]
}
df = pd.DataFrame(data)

# --- BASKET DEFINITIONS (The Real World) ---
baskets = {
    "🏙️ The Urban Professional (Solopreneur)": {
        "Base_Monthly_USD_2015": 4000,
        "Composition": "Rent (City Center), Dining, Uber, Co-working, Tech Stack",
        "Inflation_Type": "Mixed" # Mix of CPI and Asset inflation
    },
    "🏡 The Provider (Family of 4)": {
        "Base_Monthly_USD_2015": 8500,
        "Composition": "Mortgage, Private School, Health Insurance, 2 Cars, Groceries",
        "Inflation_Type": "Asset_Heavy" # Heavily impacted by real asset inflation
    },
    "✈️ The Sovereign Nomad (Global)": {
        "Base_Monthly_USD_2015": 3000,
        "Composition": "AirBnBs, Flights, Digital Services, Visa Costs, Crypto Conferences",
        "Inflation_Type": "Service_Heavy"
    }
}

# --- SIDEBAR: CONFIGURE REALITY ---
st.sidebar.title("⚙️ Configure Reality")
profile = st.sidebar.selectbox("Select Economic Profile", list(baskets.keys()))
selected_data = baskets[profile]

# Customization Override
st.sidebar.markdown("---")
st.sidebar.subheader("Make it Personal")
custom_burn = st.sidebar.number_input(
    "Override: Your Monthly Spend (in 2015 Dollars)", 
    value=selected_data["Base_Monthly_USD_2015"], 
    step=500
)

# Inflation Reality Slider
inflation_mode = st.sidebar.radio(
    "Which Inflation impacts you?",
    ("Official CPI (Government Numbers)", "Real World (Assets, Housing, Services)"),
    index=1
)

# --- CALCULATION LOGIC ---
# Select the inflation factor based on user choice
if inflation_mode.startswith("Official"):
    inflation_col = "CPI_Index"
    color_fiat = "#FF8800" # Orange for mild warning
else:
    inflation_col = "Asset_Inflation_Index"
    color_fiat = "#FF4B4B" # Red for danger

# Calculate Costs
df["Monthly_Cost_USD"] = df[inflation_col] * custom_burn
df["Monthly_Cost_BTC"] = df["Monthly_Cost_USD"] / df["BTC_Price"]

# --- MAIN DASHBOARD ---
st.title("🛡️ The Purchasing Power Defense System")
st.markdown(f"**Scenario:** {profile}")
st.caption(f"Basket Includes: {selected_data['Composition']}")

# 1. THE VISUALIZATION
col_chart, col_metrics = st.columns([3, 1])

with col_chart:
    fig = go.Figure()
    
    # Fiat Cost Line (The Pain)
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Monthly_Cost_USD"], name="Cost in Fiat (USD)",
        line=dict(color=color_fiat, width=4), yaxis="y1"
    ))
    
    # Bitcoin Cost Line (The Solution)
    fig.add_trace(go.Scatter(
        x=df["Year"], y=df["Monthly_Cost_BTC"], name="Cost in Bitcoin (BTC)",
        line=dict(color="#00FFAA", width=4, dash='solid'), yaxis="y2"
    ))

    # --- FIX APPLIED HERE ---
    # Replaced 'titlefont' with nested title dict structure
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
        title="Cost of Living: Fiat vs. Bitcoin Standard",
        yaxis=dict(
            title=dict(text="Monthly Cost (USD)", font=dict(color=color_fiat)), 
            tickfont=dict(color=color_fiat), 
            gridcolor="#333"
        ),
        yaxis2=dict(
            title=dict(text="Monthly Cost (BTC)", font=dict(color="#00FFAA")), 
            tickfont=dict(color="#00FFAA"), 
            overlaying="y", 
            side="right"
        ),
        legend=dict(orientation="h", y=1.05),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# 2. THE METRICS (The "So What?")
with col_metrics:
    st.markdown("### 📊 The Gap")
    
    # Get values
    start_usd = df.iloc[0]["Monthly_Cost_USD"]
    curr_usd = df.iloc[-1]["Monthly_Cost_USD"]
    start_btc = df.iloc[0]["Monthly_Cost_BTC"]
    curr_btc = df.iloc[-1]["Monthly_Cost_BTC"]

    # Calculate Changes
    inflation_pain = ((curr_usd - start_usd) / start_usd) * 100
    deflation_gain = ((curr_btc - start_btc) / start_btc) * 100
    
    # Display
    st.markdown("##### Your Fiat Problem")
    st.metric("Monthly Cost (USD)", f"${curr_usd:,.0f}", f"+{inflation_pain:.0f}%", delta_color="inverse")
    
    st.markdown("##### Your Bitcoin Fix")
    st.metric("Monthly Cost (BTC)", f"₿ {curr_btc:.4f}", f"{deflation_gain:.1f}%")
    
    st.markdown("---")
    st.info(f"""
    **The 'Parity' Trap:**
    
    To maintain this lifestyle in Fiat, you need to work **{inflation_pain/100 + 1:.1f}x harder** today than in 2015.
    
    In Bitcoin, this lifestyle costs **99% less** than it did in 2015.
    """)

# --- THE "ROXOM PITCH" SECTION ---
st.markdown("### 🌉 Bridging the Parity Gap")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### 1. The Trap")
    st.write("Businesses are trapped in the **Red Line**. Their OpEx (Salaries, Servers, Rent) is denominated in inflating USD.")

with c2:
    st.markdown("#### 2. The Hedge")
    st.write("Roxom allows you to hold the **Green Line** (Asset) while paying the **Red Line** (Liability) using the Basis Trade to manage the volatility.")

with c3:
    st.markdown("#### 3. The Result")
    st.write("You stop running on the inflation hamster wheel. Your Balance Sheet gets stronger simply by waiting.")