import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Lift Tracker", layout="centered")

# Establish Connection
# Make sure your secrets.toml has the correct spreadsheet URL!
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏋️ Workout Log")

# --- 1. LOAD THE PLAN ---
try:
    # This MUST match the tab name at the bottom of your Google Sheet
    sheet_name = "Workouts" 
    plan_df = conn.read(worksheet=sheet_name, ttl=0)
    
    # Sidebar to select the day of your 6 or 7 day cycle
    max_day = int(plan_df['Cycle Day'].max())
    current_day = st.sidebar.number_input("Select Cycle Day", min_value=1, max_value=max_day, value=1)

    # Filter the plan for the selected day
    today_plan = plan_df[plan_df['Cycle Day'] == current_day]
    
    if not today_plan.empty:
        workout_name = today_plan.iloc[0]['Workout Name']
        st.header(f"{workout_name} (Day {current_day})")

        # --- 2. WORKOUT FORM ---
        with st.form("workout_entry"):
            logs = []
            
            for index, row in today_plan.iterrows():
                st.markdown(f"### {row['Exercise']}")
                st.caption(f"Goal: {row['Target Sets']} sets of {row['Target Reps']} @ {row['Target Weight (lbs)']} lbs")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Defaulting value to the target weight so you don't have to type it
                    actual_w = st.number_input("Weight", key=f"w_{index}", value=float(row['Target Weight (lbs)']))
                with col2:
                    actual_r = st.number_input("Reps", key=f"r_{index}", value=0)
                with col3:
                    rpe = st.slider("RPE", 5.0, 10.0, 8.0, 0.5, key=f"rpe_{index}")
                
                logs.append({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Exercise": row['Exercise'],
                    "Weight": actual_w,
                    "Reps": actual_r,
                    "RPE": rpe
                })
                st.divider()

            # --- 3. SAVE DATA ---
            if st.form_submit_button("Finish Workout"):
                # Note: This requires a second tab named "Logs" to exist in your Sheet
                try:
                    existing_logs = conn.read(worksheet="Logs", ttl=0)
                    updated_logs = pd.concat([existing_logs, pd.DataFrame(logs)], ignore_index=True)
                    conn.update(worksheet="Logs", data=updated_logs)
                    st.success("Successfully Logged to 'Logs' tab!")
                except Exception as e:
                    st.error("Could not save. Make sure you have a tab named 'Logs' created.")

except Exception as e:
    st.error("Connection Error!")
    st.write(f"Ensure your tab is named '{sheet_name}' and your Sheet is shared as 'Anyone with the link'.")
    st.info(f"Error detail: {e}")