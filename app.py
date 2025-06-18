import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Sidebar Navigation
st.sidebar.title("☰ Navigation")
nav_option = st.sidebar.radio("Choose Section", ["Home", "Login", "Profile", "Settings"])

# Page Header
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🩺 Health Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>A Mini Project</h4>", unsafe_allow_html=True)
st.markdown("---")

# Initialize session state
if "current_module" not in st.session_state:
    st.session_state.current_module = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "symptoms_history" not in st.session_state:
    st.session_state.symptoms_history = []
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

# Main Feature Buttons Area (Only visible on Home page)
if nav_option == "Home":
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_module = "chat"
        if st.button("🦠 Diseases", use_container_width=True):
            st.session_state.current_module = "diseases"

    with col2:
        if st.button("🤒 Symptoms", use_container_width=True):
            st.session_state.current_module = "symptoms"
        if st.button("📄 Report", use_container_width=True):
            st.session_state.current_module = "reports"

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("💊 Treatment", use_container_width=False):
        st.session_state.current_module = "treatments"
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

# Module Display Area
if st.session_state.current_module and nav_option == "Home":
    module = st.session_state.current_module
    st.markdown(f"### {module.capitalize()} Module")
    
    if module == "chat":
        user_input = st.text_input("Ask a health question:")
        if st.button("Send"):
            st.session_state.messages.append(("You", user_input))
            with st.spinner("Thinking..."):
                response = llm.invoke(user_input)
                st.session_state.messages.append(("AI", response))
        
        for role, msg in reversed(st.session_state.messages):
            bubble_color = "#d1e7dd" if role == "You" else "#fff3cd"
            st.markdown(f"<div style='background:{bubble_color}; padding:10px; border-radius:10px; margin:5px;'>**{role}:** {msg}</div>", unsafe_allow_html=True)

    elif module == "symptoms":
        symptoms = st.text_area("Describe your symptoms:")
        if st.button("Analyze Symptoms"):
            with st.spinner("Analyzing..."):
                prompt = f"Medical analysis for: {symptoms}. Possible conditions and recommendations?"
                response = llm.invoke(prompt)
                st.session_state.symptoms_history.append((symptoms, response))
                st.markdown(f"### AI Analysis:\n{response}")

        st.markdown("### Symptom History")
        for symptom, analysis in st.session_state.symptoms_history:
            st.markdown(f"**Symptoms:** {symptom}")
            st.write(analysis)
            st.divider()

    elif module == "treatments":
        condition = st.text_input("Medical Condition")
        if st.button("Generate Plan"):
            prompt = f"Create treatment plan for {condition}"
            response = llm.invoke(prompt)
            st.markdown(f"### Treatment Plan:\n{response}")

    elif module == "reports":
        days = st.slider("Days of data", 1, 30, 7)
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
        metrics = {
            "Heart Rate": [random.randint(60, 100) for _ in range(days)],
            "Glucose": [round(random.uniform(70, 140), 1) for _ in range(days)],
            "BP": [(random.randint(110, 130), random.randint(70, 90)) for _ in range(days)]
        }
        df = pd.DataFrame(metrics, index=dates)
        st.line_chart(df)

    elif module == "diseases":
        condition = st.selectbox("Select Condition", ["Diabetes", "Hypertension", "Asthma"])
        if condition == "Diabetes":
            glucose = st.number_input("Blood Glucose Level (mg/dL)", 40, 400)
            if st.button("Log"):
                prompt = f"My blood sugar is {glucose}. Advice?"
                response = llm.invoke(prompt)
                st.write(response)
        # Add other conditions similarly

# Original Sidebar Content
if nav_option == "Home":
    if not st.session_state.current_module:
        st.info("Welcome to the Health Assistant. Use the buttons above to explore features.")

elif nav_option == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.success(f"Welcome, {username}!")
        else:
            st.warning("Please enter credentials")

elif nav_option == "Profile":
    st.subheader("🧾 Profile")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", 50, 250)
    weight = st.number_input("Weight (kg)", 10, 300)
    
    if height > 0:
        bmi = weight / (height/100)**2
        st.success(f"BMI: {bmi:.2f}")
        if bmi < 18.5:
            st.warning("Underweight")
        elif 18.5 <= bmi <= 24.9:
            st.success("Healthy weight")
        else:
            st.error("Overweight")
    
    if st.button("Save Profile"):
        st.session_state.profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight
        }
        st.success("Profile saved!")

elif nav_option == "Settings":
    st.subheader("⚙️ Settings")
    st.write("Configuration options coming soon!")

# Footer
st.markdown("---")
st.markdown("<center>© 2025 Mini Project | Designed by Your Team</center>", unsafe_allow_html=True)
