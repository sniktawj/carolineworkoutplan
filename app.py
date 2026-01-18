import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Lifting Log", layout="centered")

# Establish Connection
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏋️ Workout Logger")

# Form for entry
with st.form("entry_form"):
    exercise = st.selectbox("Exercise", ["Squat", "Bench Press", "Deadlift", "Overhead Press"])
    weight = st.number_input("Weight (lbs)", min_value=0, step=5)
    reps = st.number_input("Reps", min_value=0, step=1)
    rpe = st.slider("RPE", 5.0, 10.0, 8.0, 0.5)
    
    submitted = st.form_submit_button("Log Set")
    
    if submitted:
        # Create a new row of data
        new_data = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Exercise": exercise,
            "Weight": weight,
            "Reps": reps,
            "RPE": rpe
        }])
        
        # Read existing data and append
        existing_data = conn.read(ttl=0) # ttl=0 ensures we don't use old cached data
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        
        # Write back to Google Sheets
        conn.update(data=updated_df)
        st.success("Set Logged!")

# Show recent history
st.subheader("Recent Sets")
st.dataframe(conn.read(ttl=0).tail(5))