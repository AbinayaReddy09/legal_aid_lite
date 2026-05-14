import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="AquaFlow Pro Dashboard", layout="wide", page_icon="💧")

# --- CUSTOM CSS (Glassmorphism & Styling) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    div[data-testid="stMetricValue"] {
        font-size: 30px;
        color: #3b82f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #3b82f6;
        color: white;
    }
    .reportview-container .main {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=[
        "Date", "Drinking", "Cooking", "Washing", "Gardening", "Total"
    ])

LIMIT = 135

# --- SIDEBAR ---
with st.sidebar:
    st.title("💧 AquaFlow Pro")
    st.markdown("---")
    menu = st.radio("Navigation", ["Dashboard", "Add Usage", "History", "Settings"])
    st.markdown("---")
    st.info("Goal: Keep daily usage below **135 Litres**.")

# --- ADD USAGE PAGE ---
if menu == "Add Usage":
    st.header("📝 Record Daily Usage")
    with st.container():
        date = st.date_input("Select Date", datetime.now())
        col1, col2 = st.columns(2)
        with col1:
            drinking = st.number_input("Drinking (L)", min_value=0.0, step=0.5)
            cooking = st.number_input("Cooking (L)", min_value=0.0, step=0.5)
        with col2:
            washing = st.number_input("Washing (L)", min_value=0.0, step=1.0)
            gardening = st.number_input("Gardening (L)", min_value=0.0, step=1.0)

        total = drinking + cooking + washing + gardening

        if st.button("Save Record"):
            new_data = pd.DataFrame([[date, drinking, cooking, washing, gardening, total]],
                                    columns=st.session_state.history.columns)
            st.session_state.history = pd.concat([st.session_state.history, new_data], ignore_index=True)
            st.success("Usage updated successfully!")

# --- DASHBOARD PAGE ---
elif menu == "Dashboard":
    st.title("📊 Water Analytics Dashboard")

    if not st.session_state.history.empty:
        latest = st.session_state.history.iloc[-1]

        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Today's Total", f"{latest['Total']} L", delta=f"{latest['Total'] - LIMIT} L",
                    delta_color="inverse")
        col2.metric("Daily Limit", f"{LIMIT} L")
        col3.metric("Avg. Usage", f"{round(st.session_state.history['Total'].mean(), 1)} L")
        col4.metric("Categories", "4 Types")

        # Smart Alerts
        if latest['Total'] > LIMIT:
            st.error(f"⚠️ **High Usage Alert!** You are {latest['Total'] - LIMIT}L over the daily limit.")
            st.warning("Tip: Try to reduce gardening water by using a drip system.")
        else:
            st.success("✅ Good job! You are within the sustainable water limit.")

        # Charts
        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("Usage Trend")
            fig_line = px.area(st.session_state.history, x="Date", y="Total",
                               title="Total Consumption Over Time",
                               color_discrete_sequence=['#3b82f6'])
            st.plotly_chart(fig_line, use_container_width=True)

        with c2:
            st.subheader("Latest Split")
            labels = ['Drinking', 'Cooking', 'Washing', 'Gardening']
            values = [latest['Drinking'], latest['Cooking'], latest['Washing'], latest['Gardening']]
            fig_pie = px.pie(names=labels, values=values, hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("No data available. Please go to 'Add Usage' to enter your first record.")

# --- HISTORY PAGE ---
elif menu == "History":
    st.header("📜 Consumption History")
    if not st.session_state.history.empty:
        st.dataframe(st.session_state.history.style.highlight_max(axis=0, subset=['Total'], color='#441111'),
                     use_container_width=True)
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("Export to CSV", csv, "water_history.csv", "text/csv")
    else:
        st.write("No records found.")

# --- SETTINGS ---
elif menu == "Settings":
    st.header("⚙️ Preferences")
    st.toggle("Enable Dark Mode (Default)", value=True)
    if st.button("Clear All Data"):
        st.session_state.history = pd.DataFrame(
            columns=["Date", "Drinking", "Cooking", "Washing", "Gardening", "Total"])
        st.experimental_rerun()