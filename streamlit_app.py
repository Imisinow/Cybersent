import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Page configuration
st.set_page_config(page_title="Cyber-Sentinel Dashboard", layout="wide")

st.title("🛡️ Remote Security Command Center")
st.markdown("Monitoring activity from **Termux Edge Agents**")

# 1. Connection Logic
def get_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Ensure credentials.json is in your GitHub repo
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Open the sheet
    sheet = client.open("Security_Log").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# 2. Load and Display Data
try:
    df = get_data()

    # Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", len(df))
    col2.metric("Active Agents", df['Status'].nunique() if 'Status' in df else 0)
    col3.metric("Last Sync", df['Timestamp'].iloc[-1] if not df.empty else "N/A")

    st.divider()

    # Main Data Table
    st.subheader("Recent Activity Logs")
    
    # Apply some basic styling
    def highlight_status(val):
        color = 'red' if val == 'CRITICAL' else 'green'
        return f'color: {color}'

    st.dataframe(df.style.applymap(highlight_status, subset=['Status']) if 'Status' in df else df, use_container_width=True)

    # 3. Evidence Access (Dropbox Links)
    if 'Evidence_Link' in df.columns:
        st.subheader("📁 Forensics Vault")
        for index, row in df.iterrows():
            if row['Evidence_Link'] and row['Evidence_Link'] != "N/A":
                with st.expander(f"Evidence for Event {row['Timestamp']}"):
                    st.write(f"Source IP: {row['IP_Address']}")
                    st.link_button("View Evidence on Dropbox", row['Evidence_Link'])

except Exception as e:
    st.error(f"Waiting for data... Ensure your Termux script has run at least once. Error: {e}")

# Sidebar for Manual Controls
st.sidebar.header("Agent Controls")
if st.sidebar.button("Refresh Dashboard"):
    st.rerun()
