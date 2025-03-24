import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
import time

import warnings
warnings.filterwarnings('ignore')

# Initialize session state
if 'user_setup_complete' not in st.session_state:
    st.session_state.user_setup_complete = False
    st.session_state.username = ""
    st.session_state.avatar = "👤"
    st.session_state.gender = "Male"  # Default gender

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #240046;
        color: #FFFFFF;
    }
    .stSidebar {
        background-color: #391958 !important;
        color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #5A189A !important;
        color: #FFFFFF !important;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .user-header {
        color: #FFFFFF;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    /* Custom CSS for the username input box */
    .stTextInput>div>div>input {
        background-color: #4f326a !important;
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Welcome Page ---
if not st.session_state.user_setup_complete:
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1 style='color: #9D4EDD; font-size: 3rem; margin-bottom: 2rem;'>
                🏋️ Welcome to Fit Fusion
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("user_setup"):
        # Avatar selection with labels
        st.markdown("### Choose your avatar:")
        avatar = st.radio(
            "", 
            ["👨 Male", "👩 Female"],  # Avatar options with gender labels
            horizontal=False, 
            label_visibility="collapsed"
        )

        # Name input
        st.markdown("### Enter your name:")
        username = st.text_input("", "Fitness Enthusiast", label_visibility="collapsed")

        # Centered "Let's Go! 🚀" button
        col1, col2, col3 = st.columns([1.5, 1, 1.5])  # Adjusted column widths for centering
        with col2:
            submitted = st.form_submit_button("Let's Go! 🚀")

        if submitted:
            st.session_state.user_setup_complete = True
            st.session_state.username = username
            st.session_state.avatar = avatar.split()[0]  # Extract the emoji (👨, 👩)
            st.session_state.gender = avatar.split()[1]  # Extract the gender (Male, Female)
            st.rerun()

    st.stop()  # Stop execution here if setup is not complete

# --- Sidebar Header ---
with st.sidebar:
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <div style='
                background-color: #000000;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                font-size: 40px;
            '>
                {st.session_state.avatar}
            </div>
            <h2 style='margin: 0; padding: 0; color: #ffffff;'>{st.session_state.username}</h2>
            <p style='font-size: 1.2rem; color: #d9b2ff; margin: 0; padding: 0;'>
                Gender: {st.session_state.gender}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Main App ---
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #9D4EDD;'>
            Hello <span style='color: #ffffff;'>{st.session_state.username}</span>, let's crush your fitness goals today! 💪
        </h2>
        <p style='font-size: 1.2rem; color: #FFFFFF;'>
            Every step you take brings you closer to your dreams. Keep going! 🚀
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Define user input features
def user_input_features():
    age = st.sidebar.slider("Age: ", 10, 100, 30)
    bmi = st.sidebar.slider("BMI: ", 15, 40, 20)
    duration = st.sidebar.slider("Duration (min): ", 0, 35, 15)
    heart_rate = st.sidebar.slider("Heart Rate: ", 60, 130, 80)
    body_temp = st.sidebar.slider("Body Temperature (C): ", 36, 42, 38)

    # Use the gender from the session state
    gender_button = st.session_state.gender  # Pre-select the gender from the welcome page
    gender = 1 if gender_button == "Male" else 0

    data_model = {
        "Age": age,
        "BMI": bmi,
        "Duration": duration,
        "Heart_Rate": heart_rate,
        "Body_Temp": body_temp,
        "Gender_male": gender
    }

    features = pd.DataFrame(data_model, index=[0])
    return features

df = user_input_features()

# Display user parameters
st.write("---")
st.header("Your Parameters: ")
latest_iteration = st.empty()
bar = st.progress(0)
for i in range(100):
    bar.progress(i + 1)
    time.sleep(0.01)
st.write(df)

# Load and preprocess data
calories = pd.read_csv("calories.csv")
exercise = pd.read_csv("exercise.csv")

exercise_df = exercise.merge(calories, on="User_ID")
exercise_df.drop(columns="User_ID", inplace=True)

exercise_train_data, exercise_test_data = train_test_split(exercise_df, test_size=0.2, random_state=1)

for data in [exercise_train_data, exercise_test_data]:
    data["BMI"] = data["Weight"] / (data["Height"] / 100) ** 2
    data["BMI"] = round(data["BMI"], 2)

exercise_train_data = exercise_train_data[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
exercise_test_data = exercise_test_data[["Gender", "Age", "BMI", "Duration", "Heart_Rate", "Body_Temp", "Calories"]]
exercise_train_data = pd.get_dummies(exercise_train_data, drop_first=True)
exercise_test_data = pd.get_dummies(exercise_test_data, drop_first=True)

X_train = exercise_train_data.drop("Calories", axis=1)
y_train = exercise_train_data["Calories"]

X_test = exercise_test_data.drop("Calories", axis=1)
y_test = exercise_test_data["Calories"]

# Train the model
random_reg = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6)
random_reg.fit(X_train, y_train)

df = df.reindex(columns=X_train.columns, fill_value=0)

prediction = random_reg.predict(df)

# Display prediction
st.write("---")
st.header("Prediction: ")
latest_iteration = st.empty()
bar = st.progress(0)
for i in range(100):
    bar.progress(i + 1)
    time.sleep(0.01)

st.write(f"{round(prediction[0], 2)} **kilocalories**")

# Display similar results
st.write("---")
st.header("Similar Results: ")
latest_iteration = st.empty()
bar = st.progress(0)
for i in range(100):
    bar.progress(i + 1)
    time.sleep(0.01)

calorie_range = [prediction[0] - 10, prediction[0] + 10]
similar_data = exercise_df[(exercise_df["Calories"] >= calorie_range[0]) & (exercise_df["Calories"] <= calorie_range[1])]
st.write(similar_data.sample(5))

# Display general information
st.write("---")
st.header("General Information: ")

boolean_age = (exercise_df["Age"] < df["Age"].values[0]).tolist()
boolean_duration = (exercise_df["Duration"] < df["Duration"].values[0]).tolist()
boolean_body_temp = (exercise_df["Body_Temp"] < df["Body_Temp"].values[0]).tolist()
boolean_heart_rate = (exercise_df["Heart_Rate"] < df["Heart_Rate"].values[0]).tolist()

st.write("You are older than", round(sum(boolean_age) / len(boolean_age), 2) * 100, "% of other people.")
st.write("Your exercise duration is higher than", round(sum(boolean_duration) / len(boolean_duration), 2) * 100, "% of other people.")
st.write("You have a higher heart rate than", round(sum(boolean_heart_rate) / len(boolean_heart_rate), 2) * 100, "% of other people during exercise.")
st.write("You have a higher body temperature than", round(sum(boolean_body_temp) / len(boolean_body_temp), 2) * 100, "% of other people during exercise.")