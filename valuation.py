import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sovereign Valuation Model", layout="wide", page_icon="⚡")

# --- CSS FOR "NO BS" AESTHETIC ---
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #30333d;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: GLOBAL BASELINE DATA (Editable Assumptions) ---
st.sidebar.header("🌍 Global Baseline Data (2026 Est.)")

# Supply Constants
btc_supply = st.sidebar.number_input("BTC Circulating Supply (Millions)", value=19.8, step=0.1) * 1_000_000

# Market Caps (Trillions)
st.sidebar.markdown("---")
st.sidebar.subheader("Asset Class Caps ($ Trillion)")
gold_cap = st.sidebar.number_input("Gold Market Cap", value=15.0)
m2_cap = st.sidebar.number_input("Global M2 Money Supply", value=130.0)
equities_cap = st.sidebar.number_input("Global Equities", value=115.0)
real_estate_cap = st.sidebar.number_input("Global Real Estate", value=330.0)
bonds_cap = st.sidebar.number_input("Global Bond Market", value=133.0)

# Treasury Data
st.sidebar.markdown("---")
st.sidebar.subheader("Corporate Treasuries")
sp500_cash = st.sidebar.number_input("S&P 500 Cash on Hand ($T)", value=2.5)
multiplier = st.sidebar.slider("Fiat Multiplier (Price Impact)", min_value=1, max_value=100, value=25, help="How much Market Cap rises for every $1 of Inflow. (BoA estimates ~118x, conservative is 20x).")

# --- MAIN APP ---

st.title("⚡ Sovereign Valuation Engine")
st.markdown("### The Arbitrage Between 'Flow' and 'Stock'")

# Tabs for different Models
tab1, tab2, tab3 = st.tabs(["🏛️ Model A: Store of Value (Stock)", "🌊 Model B: Settlement (Flow)", "🏢 Model C: The Treasury Standard"])

# --- TAB 1: STORE OF VALUE (Replacing Assets) ---
with tab1:
    st.markdown("#### Scenario: Bitcoin absorbs Monetary Premium from Hard Assets")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Adjust the 'Demonetization %' to see implied price.")
        
        # Sliders for Adoption
        gold_share = st.slider("Gold Replaced (%)", 0, 100, 50)
        m2_share = st.slider("M2 (Fiat) Replaced (%)", 0, 100, 5)
        re_share = st.slider("Real Estate Monetary Premium Replaced (%)", 0, 100, 1)
        bonds_share = st.slider("Bonds Replaced (%)", 0, 100, 2)
        
    with col2:
        # Calculations
        val_from_gold = (gold_cap * 1_000_000_000_000 * (gold_share/100))
        val_from_m2 = (m2_cap * 1_000_000_000_000 * (m2_share/100))
        val_from_re = (real_estate_cap * 1_000_000_000_000 * (re_share/100))
        val_from_bonds = (bonds_cap * 1_000_000_000_000 * (bonds_share/100))
        
        total_market_cap = val_from_gold + val_from_m2 + val_from_re + val_from_bonds
        implied_price = total_market_cap / btc_supply
        
        # Display Big Number
        st.metric(label="✨ Implied Bitcoin Price (SoV Model)", value=f"${implied_price:,.2f}")
        
        # Chart
        data = pd.DataFrame({
            "Source": ["Gold", "M2", "Real Estate", "Bonds"],
            "Value Contributed ($T)": [val_from_gold/1e12, val_from_m2/1e12, val_from_re/1e12, val_from_bonds/1e12]
        })
        
        fig = px.bar(data, x="Source", y="Value Contributed ($T)", title="Where is the Value Coming From?", color="Source", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: SETTLEMENT (Volume / GDP) ---
with tab2:
    st.markdown("#### Scenario: Bitcoin as the Global Settlement Rail")
    st.markdown("_Based on the Equation of Exchange: MV = PQ_")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Inputs")
        annual_gdp = st.number_input("Global GDP / Settlement Volume ($ Trillion)", value=105.0)
        btc_velocity = st.slider("Bitcoin Velocity (Turnover per year)", 1, 100, 10, help="How many times a single coin moves per year. Lower = HODL = Higher Price.")
        adoption_gdp = st.slider("% of GDP Settled on Bitcoin", 1, 100, 10)
        
    with c2:
        st.subheader("Outputs")
        
        # Math: Market Cap = (Volume / Velocity)
        target_volume = (annual_gdp * 1_000_000_000_000) * (adoption_gdp/100)
        required_mcap = target_volume / btc_velocity
        flow_price = required_mcap / btc_supply
        
        st.metric(label="🌊 Implied Bitcoin Price (Flow Model)", value=f"${flow_price:,.2f}")
        
        st.write(f"""
        **The Logic:**
        To settle **${(target_volume/1e12):.1f}T** annually with a velocity of **{btc_velocity}**, 
        the network needs a liquid capacity of **${(required_mcap/1e12):.2f}T**.
        """)

# --- TAB 3: THE TREASURY STANDARD (Saylor Model) ---
with tab3:
    st.markdown("#### Scenario: Corporate Treasuries Adopt the Bitcoin Standard")
    st.markdown("_Simulating the 'Fiat Multiplier' effect of institutional inflows._")
    
    # User Controls
    col_t1, col_t2 = st.columns([1,2])
    
    with col_t1:
        alloc_percent = st.slider("S&P 500 Cash Allocation (%)", 0.0, 100.0, 5.0)
        st.write(f"**Multiplier Assumption:** {multiplier}x")
        st.caption("For every $1 of buying pressure, Market Cap rises by $X due to scarcity.")
        
    with col_t2:
        # Math
        inflow_billions = sp500_cash * 1000 * (alloc_percent/100)
        mcap_impact_billions = inflow_billions * multiplier
        price_impact = (mcap_impact_billions * 1_000_000_000) / btc_supply
        
        # Current Price Assumption (Hardcoded or fetched, using 91k based on context)
        base_price = 91000 
        final_price = base_price + price_impact
        
        st.metric("💰 Net New Inflow", f"${inflow_billions:,.1f} Billion")
        st.metric("🚀 Price Impact (+)", f"+ ${price_impact:,.2f}")
        st.metric("🏁 Final Simulated Price", f"${final_price:,.2f}", delta=f"{((final_price-base_price)/base_price)*100:.1f}%")
        
        # Visualization of the Curve
        # Generate data for 0-100% allocation
        alloc_range = list(range(0, 101, 5))
        prices = []
        for a in alloc_range:
             inf = sp500_cash * 1000 * (a/100)
             impact = (inf * multiplier * 1_000_000_000) / btc_supply
             prices.append(base_price + impact)
             
        df_curve = pd.DataFrame({"Allocation %": alloc_range, "BTC Price": prices})
        fig_curve = px.line(df_curve, x="Allocation %", y="BTC Price", title="The Treasury Curve (S&P 500 Allocation)", template="plotly_dark")
        st.plotly_chart(fig_curve, use_container_width=True)

st.markdown("---")
st.caption( "Internal Tool v0.1 | Data Sources: IMF, World Gold Council, JV Research 2026")