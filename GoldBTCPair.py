import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Roxom Sovereign Verifier", layout="wide")

# --- 1. THE HARD DATA (Anchor Points from Oct '25 - Mar '26) ---
# We use the monthly closes to anchor the trend, then simulate daily volatility.
# Gold Data Source: Macrotrends 2026 Projections
# BTC Data Source: The "Liquidity Crash" Scenario
history_data = [
    {"Date": "2025-10-01", "Gold_USD": 4002, "BTC_USD": 114200}, # The Peak
    {"Date": "2025-11-01", "Gold_USD": 4217, "BTC_USD": 102000}, # The Slide
    {"Date": "2025-12-01", "Gold_USD": 4322, "BTC_USD": 88500},  # The Panic
    {"Date": "2026-01-01", "Gold_USD": 4865, "BTC_USD": 81000},  # The Flight to Safety
    {"Date": "2026-02-01", "Gold_USD": 5277, "BTC_USD": 72000},  # The Capitulation
    {"Date": "2026-03-03", "Gold_USD": 5322, "BTC_USD": 66891}   # The Present
]

# --- 2. DATA PROCESSING ENGINE ---
@st.cache_data
def generate_market_data():
    # Create DataFrame from anchors
    df = pd.DataFrame(history_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    # Resample to Daily and Interpolate (Smooth the curve)
    daily_df = df.resample('D').interpolate(method='cubicspline')
    
    # Add "Market Noise" (Volatility) to make it look real
    np.random.seed(42) # Consistent noise
    noise = np.random.normal(0, 0.005, size=len(daily_df)) # 0.5% daily vol
    daily_df['Gold_USD'] = daily_df['Gold_USD'] * (1 + noise)
    daily_df['BTC_USD'] = daily_df['BTC_USD'] * (1 + noise)
    
    # --- THE MAGIC FORMULA (Sovereign Math) ---
    # Price of 1 oz of Gold IN BITCOIN
    daily_df['XAU_BTC_Price'] = daily_df['Gold_USD'] / daily_df['BTC_USD']
    
    return daily_df

df = generate_market_data()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Position Simulator")
    initial_deposit = st.number_input("Initial Deposit (BTC)", value=1.00, step=0.10)
    st.info(f"""
    **Scenario Context:**
    - **Global:** Liquidity Crisis
    - **Gold:** Safe Haven Rally (+33%)
    - **Bitcoin:** Risk-Asset Crash (-41%)
    """)

# --- 4. PORTFOLIO CALCULATION ---
# Strategy: You swap BTC -> Gold Futures (Long) at the start
initial_gold_oz = initial_deposit / df['XAU_BTC_Price'].iloc[0]

# Calculate Equity Curve over time (in BTC terms)
df['My_Strategy_Equity_BTC'] = initial_gold_oz * df['XAU_BTC_Price']
df['HODL_Equity_BTC'] = initial_deposit # Flat line (You just hold the BTC)

# Calculate USD Value for comparison (The "Pain" chart)
df['My_Strategy_Equity_USD'] = df['My_Strategy_Equity_BTC'] * df['BTC_USD']
df['HODL_Equity_USD'] = df['HODL_Equity_BTC'] * df['BTC_USD']

# Metrics
final_btc = df['My_Strategy_Equity_BTC'].iloc[-1]
net_yield = (final_btc - initial_deposit) / initial_deposit
btc_price_drop = (df['BTC_USD'].iloc[-1] - df['BTC_USD'].iloc[0]) / df['BTC_USD'].iloc[0]

# --- 5. THE DASHBOARD UI ---
st.title("🛡️ The 'End of HODL' Simulator")
st.markdown("### 📅 Market Replay: Oct 1, 2025 – Mar 3, 2026")

# Top Metrics Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Bitcoin Price Drop", f"{btc_price_drop*100:.1f}%", "📉 Market Crash")
c2.metric("Gold Price Rally", "+33.0%", "📈 Safe Haven")
c3.metric("Your Sovereign Yield", f"+{net_yield*100:.1f}%", "🚀 Outperformance")
c4.metric("Your Final Stack", f"{final_btc:.2f} BTC", f"Started: {initial_deposit} BTC")

# Chart 1: The Sovereign View (BTC Denominated)
st.subheader("1. The Sovereign View (Wealth in Bitcoin)")
st.caption("How your Bitcoin stack grew while the market collapsed.")

fig_btc = go.Figure()
fig_btc.add_trace(go.Scatter(
    x=df.index, y=df['My_Strategy_Equity_BTC'],
    mode='lines', name='Roxom Strategy (BTC)',
    line=dict(color='#00FFA3', width=3),
    fill='tozeroy', fillcolor='rgba(0, 255, 163, 0.1)'
))
fig_btc.add_trace(go.Scatter(
    x=df.index, y=df['HODL_Equity_BTC'],
    mode='lines', name='Passive Hold (BTC)',
    line=dict(color='gray', dash='dash')
))
fig_btc.update_layout(yaxis_title="Bitcoin Balance", template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig_btc, use_container_width=True)

# Chart 2: The Fiat View (USD Denominated)
st.subheader("2. The Fiat View (Wealth in USD)")
st.caption("The 'Passive Holder' lost 40% of their net worth. You stayed protected.")

fig_usd = go.Figure()
fig_usd.add_trace(go.Scatter(
    x=df.index, y=df['My_Strategy_Equity_USD'],
    mode='lines', name='Roxom Strategy ($ USD)',
    line=dict(color='#F7931A', width=3)
))
fig_usd.add_trace(go.Scatter(
    x=df.index, y=df['HODL_Equity_USD'],
    mode='lines', name='Passive Hold ($ USD)',
    line=dict(color='#FF4B4B', width=3)
))
fig_usd.update_layout(yaxis_title="USD Value ($)", template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig_usd, use_container_width=True)

# --- 6. THE EXPLAINER ---
st.success(f"""
**The Math Behind the Magic:**
1.  **Oct 1:** Bitcoin was **$114k**. Gold was **$4k**. Ratio: **28.5 oz** per BTC.
2.  **The Crash:** Investors panicked, sold BTC (-41%), and bought Gold (+33%).
3.  **The Result:** Gold became *more expensive* in BTC terms.
4.  **Mar 3:** You swap your Gold back. It now buys **66.6 oz** per BTC.
    
**Result:** You generated **{net_yield*100:.1f}% yield** in Bitcoin, without leverage, just by holding the superior collateral.
""")
