import streamlit as st
import pandas as pd
import time

# --- CONFIGURATION & STATE ---
if 'balance_treasury' not in st.session_state:
    st.session_state.balance_treasury = 0.0
if 'ledger' not in st.session_state:
    st.session_state.ledger = pd.DataFrame(columns=["Timestamp", "Type", "From", "To", "Amount (BTC)", "Note"])
if 'cap_table' not in st.session_state:
    # Default Cap Table (The "Smart Contract" Rules)
    st.session_state.cap_table = [
        {"Role": "Founder", "Name": "Alice", "Wallet": "bc1q...Alice", "Share": 0.20, "Status": "Active"},
        {"Role": "Dev",     "Name": "Bob",   "Wallet": "bc1q...Bob",   "Share": 0.15, "Status": "Active"},
        {"Role": "Ops",     "Name": "Charlie","Wallet": "bc1q...Char", "Share": 0.05, "Status": "Active"},
        {"Role": "Reserve", "Name": "Company Vault", "Wallet": "bc1q...Vault", "Share": 0.60, "Status": "Active"},
    ]

# --- LOGIC ENGINE (The "Smart Contract") ---
def execute_distribution(revenue_amount, note):
    """
    The core logic. Takes incoming BTC and splits it according to the Cap Table.
    """
    # 1. Log the Incoming Payment
    new_entry = {
        "Timestamp": pd.Timestamp.now(),
        "Type": "INCOME",
        "From": "Client",
        "To": "Revenue Router",
        "Amount (BTC)": revenue_amount,
        "Note": note
    }
    st.session_state.ledger = pd.concat([st.session_state.ledger, pd.DataFrame([new_entry])], ignore_index=True)
    
    # 2. Iterate through Cap Table and Split
    distributions = []
    total_distributed = 0
    
    for member in st.session_state.cap_table:
        if member['Status'] == "Active":
            payout = revenue_amount * member['Share']
            
            # Log the Outgoing Payout (The "Stream")
            dist_entry = {
                "Timestamp": pd.Timestamp.now(),
                "Type": "PAYOUT",
                "From": "Revenue Router",
                "To": member['Name'],
                "Amount (BTC)": payout,
                "Note": f"Salary Share ({member['Share']*100}%)"
            }
            distributions.append(dist_entry)
            total_distributed += payout

    # 3. Update Ledger
    st.session_state.ledger = pd.concat([st.session_state.ledger, pd.DataFrame(distributions)], ignore_index=True)
    return total_distributed

# --- USER INTERFACE ---

st.set_page_config(page_title="Roxom DAO Simulator", layout="wide")

st.title("⚡ Roxom Sovereign DAO Engine")
st.markdown("Prototype: `RLP-1 (Revenue Labor Protocol)`")

# Sidebar: Manage the Rules
with st.sidebar:
    st.header("⚙️ Protocol Rules (Cap Table)")
    
    # Editable Cap Table
    edited_cap_table = st.data_editor(st.session_state.cap_table, num_rows="dynamic")
    st.session_state.cap_table = edited_cap_table
    
    # Validation
    total_share = sum([m['Share'] for m in st.session_state.cap_table if m['Status'] == 'Active'])
    st.metric("Total Allocation", f"{total_share*100:.1f}%")
    
    if total_share != 1.0:
        st.error(f"⚠️ Allocation must equal 100%! Current: {total_share*100}%")

# Main Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Live Transaction Ledger")
    # Display the Ledger (The "Truth")
    st.dataframe(st.session_state.ledger.sort_values(by="Timestamp", ascending=False), height=400, use_container_width=True)

with col2:
    st.subheader("💰 Simulate Revenue")
    
    # Input for Simulation
    revenue_input = st.number_input("Incoming Payment (BTC)", min_value=0.0, value=1.0, step=0.1)
    client_note = st.text_input("Payment Reference", "Invoice #1024 - Consulting")
    
    if st.button("🔴 EXECUTE PAYMENT", type="primary"):
        if total_share == 1.0:
            with st.spinner("Processing Smart Contract Logic..."):
                time.sleep(1) # Fake processing time
                distributed = execute_distribution(revenue_input, client_note)
            st.success(f"Successfully bridged {distributed} BTC to {len(st.session_state.cap_table)} wallets!")
            st.rerun()
        else:
            st.error("Cannot execute: Cap Table Logic Error (Shares != 100%)")

    st.divider()
    
    # Stats
    st.subheader("Protocol Stats")
    total_processed = st.session_state.ledger[st.session_state.ledger['Type']=="INCOME"]['Amount (BTC)'].sum()
    st.metric("Total Volume Processed", f"₿ {total_processed:.4f}")
    
    # Export "Compliance" Report
    csv = st.session_state.ledger.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Compliance Report (CSV)",
        data=csv,
        file_name='roxom_compliance_export.csv',
        mime='text/csv',
    )