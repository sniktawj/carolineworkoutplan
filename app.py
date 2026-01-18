import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Connection setup
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏋️ Smart Workout Logger")

# --- 1. SET THE CYCLE DAY ---
# You can set this manually or use a date-based calculation
# For now, let's use a slider so you can pick your day at the gym
current_day = st.sidebar.number_input("Current Cycle Day", min_value=1, max_value=7, value=1)

# --- 2. LOAD YOUR PLAN ---
# Reads the sheet shown in your screenshot
plan_df = conn.read(worksheet="Sheet1", ttl=0) 
today_plan = plan_df[plan_df['Cycle Day'] == current_day]

if not today_plan.empty:
    workout_name = today_plan.iloc[0]['Workout Name']
    st.header(f"Day {current_day}: {workout_name}")
    
    # --- 3. DYNAMIC WORKOUT FORM ---
    with st.form("daily_log"):
        all_sets_data = []
        
        for index, row in today_plan.iterrows():
            st.subheader(f"🔹 {row['Exercise']}")
            st.info(f"Target: {row['Target Sets']} sets of {row['Target Reps']} @ {row['Target Weight (lbs)']} lbs")
            
            # Create columns for side-by-side inputs to save vertical space on iPhone
            col1, col2, col3 = st.columns(3)
            
            with col1:
                actual_weight = st.number_input(f"Weight", key=f"w_{index}", value=float(row['Target Weight (lbs)']), step=5.0)
            with col2:
                actual_reps = st.number_input(f"Reps", key=f"r_{index}", value=0, step=1)
            with col3:
                rpe = st.slider(f"RPE", 5.0, 10.0, 8.0, 0.5, key=f"rpe_{index}")
            
            # Store data to save later
            all_sets_data.append({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": row['Exercise'],
                "Actual Weight": actual_weight,
                "Actual Reps": actual_reps,
                "RPE": rpe,
                "Target Weight": row['Target Weight (lbs)']
            })
            st.divider()

        # --- 4. SUBMIT TO GOOGLE SHEETS ---
        if st.form_submit_button("Finish & Log Workout"):
            # Load your 'Logs' sheet
            try:
                logs_df = conn.read(worksheet="Logs", ttl=0)
            except:
                logs_df = pd.DataFrame() # Create if it doesn't exist
            
            new_logs = pd.DataFrame(all_sets_data)
            updated_logs = pd.concat([logs_df, new_logs], ignore_index=True)
            
            conn.update(worksheet="Logs", data=updated_logs)
            st.success("Workout saved to the Logs tab!")
else:
    st.warning(f"No exercises found for Day {current_day} in your spreadsheet.")