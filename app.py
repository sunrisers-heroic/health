import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS for green-themed UI
st.markdown("""
    <style>
        body {
            background-color: #f0fff4;
            font-family: Arial, sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .card {
            background-color: #ffffff;
            padding: 15px 20px;
            border-left: 5px solid #2ecc71;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .tab-button {
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 10px 16px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .tab-button:hover {
            background-color: #27ae60;
        }
        .section {
            display: none;
            padding: 20px;
            background-color: #f9fcff;
            border-left: 5px solid #2ecc71;
            margin-top: 10px;
            border-radius: 6px;
        }
        .active-section {
            display: block;
        }
        .chat-bubble-user {
            background-color: #d6eaff;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            align-self: flex-end;
            margin: 5px 0;
        }
        .chat-bubble-bot {
            background-color: #e6f0ff;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            align-self: flex-start;
            margin: 5px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "medications" not in st.session_state:
    st.session_state.medications = []
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "posts" not in st.session_state:
    st.session_state.posts = []
if "symptoms_history" not in st.session_state:
    st.session_state.symptoms_history = []

# Load Watsonx credentials from secrets
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
            GenParams.TEMPERATURE: 0,
            GenParams.MIN_NEW_TOKENS: 5,
            GenParams.MAX_NEW_TOKENS: 250,
            GenParams.STOP_SEQUENCES: ["Human:", "Observation"],
        },
    )
except KeyError:
    st.warning("⚠️ Watsonx credentials missing.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Error initializing LLM: {str(e)}")
    st.stop()

# Navigation bar with buttons
st.markdown('<div class="navbar">', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("🏠 Home", key="btn_home", use_container_width=True):
        st.session_state.current_section = "home"
with col2:
    if st.button("🔐 Login", key="btn_login", use_container_width=True):
        st.session_state.current_section = "login"
with col3:
    if st.button("🧾 Profile", key="btn_profile", use_container_width=True):
        st.session_state.current_section = "profile"
with col4:
    if st.button("🧠 Symptoms", key="btn_symptoms", use_container_width=True):
        st.session_state.current_section = "symptoms"
with col5:
    if st.button("📈 Reports", key="btn_reports", use_container_width=True):
        st.session_state.current_section = "reports"
with col6:
    if st.button("🫀 Diseases", key="btn_diseases", use_container_width=True):
        st.session_state.current_section = "diseases"
with col7:
    if st.button("⚙️ Settings", key="btn_settings", use_container_width=True):
        st.session_state.current_section = "settings"

st.markdown('</div>', unsafe_allow_html=True)

# Header
st.markdown('<h1 style="text-align:center; color:#2ecc71;">🩺 Health Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:16px;">A modern health tracking and wellness assistant.</p>', unsafe_allow_html=True)

# Function to show/hide sections
def show_section(name):
    return st.session_state.current_section == name

# ------------------------------ HOME PAGE ------------------------------
if show_section("home"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>Welcome to Your Health Assistant 🏥</h2>', unsafe_allow_html=True)
    st.markdown("""
    This application helps you manage your health comprehensively — from symptom checks to fitness planning.
    
    ### 🧠 Highlights:
    - 💬 AI-Powered Symptom Checker  
    - 📊 Real-Time Health Metrics  
    - 🎯 Customizable Wellness Plans  
    - 🔐 Secure, Private, and Simple  

    Use the navigation above to explore!
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ LOGIN PAGE ------------------------------
elif show_section("login"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>🔐 Login</h2>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state.user_logged_in = True
        st.success("Logged in successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ USER PROFILE ------------------------------
elif show_section("profile"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>🧾 User Profile & Dashboard</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        height = st.number_input("Height (cm)", min_value=50, max_value=250)
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
        if height > 0:
            bmi = weight / ((height / 100) ** 2)
            st.write(f"**BMI:** {bmi:.1f}")
    if st.button("Save Profile"):
        st.session_state.profile = {"name": name, "age": age, "gender": gender, "height": height, "weight": weight}
        st.success("Profile saved!")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ SYMPTOM CHECKER ------------------------------
elif show_section("symptoms"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>🧠 AI Symptom Checker</h2>', unsafe_allow_html=True)
    symptoms = st.text_area("Describe your symptoms:")
    if st.button("Check Symptoms"):
        with st.spinner("Analyzing..."):
            prompt = f"Based on these symptoms: '{symptoms}', what could be the possible conditions?"
            response = llm.invoke(prompt)
            st.session_state.symptoms_history.append({
                "input": symptoms,
                "response": response
            })
            st.markdown(f"🔍 **Possible Conditions:**\n\n{response}")

    st.markdown("### 📜 Symptom History")
    for item in st.session_state.symptoms_history:
        st.markdown(f"**Q:** {item['input']}\n\n**A:** {item['response']}")
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ PROGRESS REPORTS ------------------------------
elif show_section("reports"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>📈 Progress Reports</h2>', unsafe_allow_html=True)
    steps = st.slider("Steps Taken", 0, 50000, step=100)
    heart_rate = st.slider("Heart Rate (bpm)", 40, 200)
    sleep_hours = st.slider("Hours Slept", 0, 12)
    water = st.slider("Water Intake (L)", 0.0, 5.0, step=0.1)

    if st.button("Save Data"):
        st.session_state.health_data = {
            "steps": steps,
            "heart_rate": heart_rate,
            "sleep_hours": sleep_hours,
            "water_intake": water
        }
        st.success("Data saved successfully.")

    st.markdown("### Weekly Summary")
    st.line_chart([10, 20, 30, 25, 40])
    st.bar_chart({"Week 1": [20], "Week 2": [25], "Week 3": [30]})
    if st.button("Export Report"):
        df = pd.DataFrame([st.session_state.health_data])
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name="health_report.csv")
        st.success("Report exported as CSV!")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ CHRONIC DISEASE MANAGEMENT ------------------------------
elif show_section("diseases"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>🫀 Chronic Disease Logs</h2>', unsafe_allow_html=True)
    condition = st.selectbox("Condition", ["Diabetes", "Hypertension", "Asthma"])
    if condition == "Diabetes":
        glucose = st.number_input("Blood Glucose Level (mg/dL)")
        if st.button("Log Glucose"):
            st.success(f"Logged: {glucose} mg/dL")
    elif condition == "Hypertension":
        bp = st.text_input("Blood Pressure (e.g., 120/80)")
        if st.button("Log BP"):
            st.success(f"Logged: {bp}")
    elif condition == "Asthma":
        triggers = st.text_area("Triggers Today")
        if st.button("Log Asthma"):
            st.success("Logged successfully.")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ SETTINGS ------------------------------
elif show_section("settings"):
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.markdown('<h2>⚙️ Settings & Preferences</h2>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
    theme = st.selectbox("Theme", ["Light", "Dark"])
    font_size = st.slider("Font Size", 12, 24)
    if st.button("Save Preferences"):
        st.success("Preferences updated!")
    st.markdown('</div>', unsafe_allow_html=True)

# Default fallback
else:
    st.markdown('<div class="active-section">', unsafe_allow_html=True)
    st.info("Select a feature from the navigation above.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2025 MyHospital Health Assistant | Built with ❤️ using Streamlit & Watsonx")

# Debug Mode
with st.expander("🔧 Debug Mode"):
    st.write("Session State:", st.session_state)
