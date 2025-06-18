import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS for improved UI
st.markdown("""
    <style>
        .sidebar .css-1d391kg {background-color: #f8f9fa;}
        .main {padding: 20px;}
        .stButton button {font-size: 16px; padding: 12px 24px; margin: 10px 0;}
        .card {background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
        .chat-bubble-user {background: #d1e7dd; margin: 5px 0; padding: 10px; border-radius: 10px;}
        .chat-bubble-bot {background: #fff3cd; margin: 5px 0; padding: 10px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = "Home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "symptoms_history" not in st.session_state:
    st.session_state.symptoms_history = []
if "treatment_plan" not in st.session_state:
    st.session_state.treatment_plan = {}
if "profile" not in st.session_state:
    st.session_state.profile = {}

# Watsonx setup
try:
    credentials = {
        "url": st.secrets["WATSONX_URL"],
        "apikey": st.secrets["WATSONX_APIKEY"]
    }
    project_id = st.secrets["WATSONX_PROJECT_ID"]
    llm = WatsonxLLM(
        model_id="ibm/granite-3-2-8b-instruct",
        url=credentials.get("url"),
        apikey=credentials.get("apikey"),
        project_id=project_id,
        params={
            GenParams.DECODING_METHOD: "greedy",
            GenParams.TEMPERATURE: 0.7,
            GenParams.MAX_NEW_TOKENS: 500,
        },
    )
except KeyError:
    st.warning("⚠️ Watsonx credentials missing.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("☰ Navigation")
nav_option = st.sidebar.radio("Choose Section", 
    ["Home", "Login", "Profile", "Symptoms", "Chat", "Diseases", "Reports", "Treatments", "Settings"])

# Page Header
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🩺 Health Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>A Modern Health Tracking Solution</h4>", unsafe_allow_html=True)
st.markdown("---")

# Content Sections
def home_section():
    st.info("Welcome! Use the sidebar to navigate different health modules.")

def login_section():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.success(f"Welcome, {username}!")
        else:
            st.warning("Please enter credentials")

def profile_section():
    st.subheader("🧾 Profile")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", 50, 250)
    weight = st.number_input("Weight (kg)", 10, 300)
    
    if height > 0 and st.button("Calculate BMI"):
        bmi = weight / (height/100)**2
        st.success(f"BMI: {bmi:.2f}")
        if bmi < 18.5:
            st.warning("Underweight")
        elif 18.5 <= bmi <= 24.9:
            st.success("Healthy weight")
        else:
            st.error("Overweight")

def symptoms_section():
    st.subheader("🧠 Symptom Checker")
    symptoms = st.text_area("Describe your symptoms:")
    if st.button("Analyze Symptoms"):
        with st.spinner("Analyzing..."):
            prompt = f"Medical analysis for: {symptoms}. Possible conditions and recommendations?"
            response = llm.invoke(prompt)
            st.markdown(f"### AI Analysis:\n{response}")

def chat_section():
    st.subheader("🤖 Health Chatbot")
    user_input = st.text_input("Ask a health question:")
    if st.button("Send"):
        st.session_state.messages.append(("You", user_input))
        with st.spinner("Thinking..."):
            response = llm.invoke(user_input)
            st.session_state.messages.append(("AI", response))
    
    for role, msg in reversed(st.session_state.messages):
        bubble_class = "chat-bubble-user" if role == "You" else "chat-bubble-bot"
        st.markdown(f"<div class='{bubble_class}'><b>{role}:</b> {msg}</div>", unsafe_allow_html=True)

def diseases_section():
    st.subheader("🫀 Chronic Disease Management")
    condition = st.selectbox("Select Condition", ["Diabetes", "Hypertension", "Asthma"])
    # Add disease-specific tracking here (similar to original code)

def reports_section():
    st.subheader("📈 Health Reports")
    # Add report generation functionality here

def treatments_section():
    st.subheader("💊 Treatment Planner")
    condition = st.text_input("Medical Condition")
    if st.button("Generate Plan"):
        prompt = f"Create treatment plan for {condition}"
        response = llm.invoke(prompt)
        st.markdown(f"### Treatment Plan:\n{response}")

def settings_section():
    st.subheader("⚙️ Settings")
    st.write("Configuration options coming soon!")

# Route to selected section
sections = {
    "Home": home_section,
    "Login": login_section,
    "Profile": profile_section,
    "Symptoms": symptoms_section,
    "Chat": chat_section,
    "Diseases": diseases_section,
    "Reports": reports_section,
    "Treatments": treatments_section,
    "Settings": settings_section
}

sections[nav_option]()
