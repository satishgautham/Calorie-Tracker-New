import streamlit as st
import pandas as pd
import os
import datetime

# Optional Firebase Auth integration placeholder
# from firebase_admin import auth, credentials, initialize_app

# Page config for a polished look
st.set_page_config(page_title="Calorie Tracker", layout="wide")

@st.cache_data
def load_data():
    if not os.path.exists("cleaned_food_data.csv"):
        st.error("🚫 'cleaned_food_data.csv' not found. Please upload it to your GitHub repo root.")
        st.stop()
    return pd.read_csv("cleaned_food_data.csv")

food_df = load_data()

# Initialize session state
if 'food_log' not in st.session_state:
    st.session_state.food_log = []
if 'supplement_log' not in st.session_state:
    st.session_state.supplement_log = []
if 'weight_log' not in st.session_state:
    st.session_state.weight_log = []

# Optional: user targets
macro_targets = {
    "Calories": 2000,
    "Protein": 150,
    "Carbs": 200,
    "Fats": 70
}

st.markdown("""
    <style>
    .main { background-color: #f9fbfc; }
    .stApp { font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.title("💪 Calorie & Supplement Tracker")
st.subheader("Track your food, supplements, and body stats to hit your fitness goals.")

# Tabs layout
tabs = st.tabs(["🍴 Food Intake", "📚 Past Logs", "💊 Supplements", "📈 Weight Progress"])

# Shared date picker
selected_date = st.date_input("Select Date", datetime.date.today(), key="date")

# --- Food Intake Tab ---
with tabs[0]:
    st.header("🍽️ Log Your Meals")
    with st.form("food_form"):
        ingredient = st.selectbox("Select Ingredient", sorted(food_df["Ingredient"].dropna().unique()))
        intake = st.number_input("Quantity Consumed (g)", min_value=1.0, step=1.0)
        meal_type = st.radio("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        submit_food = st.form_submit_button("➕ Add to Log")

        if submit_food:
            row = food_df[food_df["Ingredient"] == ingredient].iloc[0]
            protein_per_g = pd.to_numeric(row["Protein_per_g"], errors="coerce")
            carbs_per_g = pd.to_numeric(row["Carbs_per_g"], errors="coerce")
            fats_per_g = pd.to_numeric(row["Fats_per_g"], errors="coerce")
            calories_per_portion = pd.to_numeric(row["Calories"], errors="coerce")
            intake_portion = pd.to_numeric(row["Intake_g"], errors="coerce")

            if pd.isnull([protein_per_g, carbs_per_g, fats_per_g, calories_per_portion, intake_portion]).any():
                st.warning("⚠️ Some nutrition values are invalid. Please check the CSV for missing or non-numeric entries.")
                st.stop()

            protein = protein_per_g * intake
            carbs = carbs_per_g * intake
            fats = fats_per_g * intake
            calories = calories_per_portion * (intake / intake_portion)

            st.session_state.food_log.append({
                "Date": selected_date,
                "Ingredient": ingredient,
                "Qty (g)": intake,
                "Meal": meal_type,
                "Protein": protein,
                "Carbs": carbs,
                "Fats": fats,
                "Calories": calories
            })

    log_df = pd.DataFrame(st.session_state.food_log)
    if not log_df.empty:
        st.subheader("📋 Today's Food Log")
        daily_log = log_df[log_df['Date'] == selected_date]
        st.dataframe(daily_log, use_container_width=True)

        daily = daily_log.sum(numeric_only=True)
        cols = st.columns(4)
        cols[0].metric("🔥 Calories", f"{daily['Calories']:.0f} kcal", delta=f"Target: {macro_targets['Calories']}")
        cols[1].metric("🍗 Protein", f"{daily['Protein']:.1f} g", delta=f"Target: {macro_targets['Protein']}")
        cols[2].metric("🥖 Carbs", f"{daily['Carbs']:.1f} g", delta=f"Target: {macro_targets['Carbs']}")
        cols[3].metric("🥑 Fats", f"{daily['Fats']:.1f} g", delta=f"Target: {macro_targets['Fats']}")

        # Alerts
        for macro in ["Calories", "Protein", "Carbs", "Fats"]:
            if daily[macro] > macro_targets[macro]:
                st.warning(f"⚠️ {macro} intake exceeds your target ({macro_targets[macro]})")

        st.download_button("⬇️ Export Today's Log", daily_log.to_csv(index=False), "today_log.csv")

# Hosting Instructions
with st.expander("🚀 How to Host This App on Streamlit Cloud"):
    st.markdown("""
    1. Push all files to a GitHub repository (including `calorie_tracker_app.py`, `cleaned_food_data.csv`, `requirements.txt`)
    2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
    3. Click **'New App'**, connect your GitHub, and choose your repo and branch
    4. Set `calorie_tracker_app.py` as the main file
    5. Click **Deploy** and enjoy your live tracker!
    """)

# Remaining tabs remain unchanged
