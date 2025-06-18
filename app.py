import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
import random
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Enhanced Custom CSS
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #2c3e50;
        }
        .stApp {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .sidebar {
            background: linear-gradient(135deg, #ffffff 0%, #e0eafc 100%);
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 25px;
            position: sticky;
            top: 20px;
        }
        .sidebar .css-1d391kg {
            border-radius: 10px;
        }
        .main {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .main:hover {
            transform: translateY(-5px);
        }
        .header {
            font-family: 'Arial', sans-serif;
            color: #2ecc71;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .button-primary {
            background: linear-gradient(45deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .button-primary:hover {
            background: linear-gradient(45deg, #27ae60 0%, #2ecc71 100%);
            transform: scale(1.05);
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid #2ecc71;
        }
        .chat-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
        }
        .chat-bubble-user {
            background: #d5f7e6;
            border-radius: 15px;
            padding: 12px;
            margin: 5px 0;
            align-self: flex-end;
        }
        .chat-bubble-bot {
            background: #e8f4ff;
            border-radius: 15px;
            padding: 12px;
            margin: 5px 0;
            align-self: flex-start;
        }
        .metric-box {
            background: #fff;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .symptom-history {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        .treatment-plan {
            background: #fff3e0;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #e67e22;
        }
        .footer {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 -2px 6px rgba(0,0,0,0.05);
        }
        .glucose-chart {
            background: linear-gradient(135deg, #ffffff 0%, #e0eafc 100%);
            padding: 15px;
            border-radius: 10px;
        }
        .bp-chart {
            background: linear-gradient(135deg, #ffffff 0%, #d5f7e6 100%);
            padding: 15px;
            border-radius: 10px;
        }
        .asthma-chart {
            background: linear-gradient(135deg, #ffffff 0%, #fce4ec 100%);
            padding: 15px;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "symptoms_history" not in st.session_state:
    st.session_state.symptoms_history = []
if "treatment_plan" not in st.session_state:
    st.session_state.treatment_plan = {}
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "glucose_log" not in st.session_state:
    st.session_state.glucose_log = []
if "bp_log" not in st.session_state:
    st.session_state.bp_log = []
if "asthma_log" not in st.session_state:
    st.session_state.asthma_log = []

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
    ["Home", "Login", "Profile", "Symptoms", "Chat", 
     "Diseases", "Reports", "Treatments", "Settings"])

# Page Header
st.markdown('<h1 class="header" style="text-align:center;">🩺 Health Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#7f8c8d;">Your Personal Health Companion</p>', unsafe_allow_html=True)
st.markdown("---")

# Main Feature Buttons Area (Only visible on Home page)
if nav_option == "Home":
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("💬 AI Chat", key="chat_btn", use_container_width=True, help="Ask health-related questions"):
                st.session_state.current_section = "chat"
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("🦠 Disease Info", key="diseases_btn", use_container_width=True, help="Learn about chronic conditions"):
                st.session_state.current_section = "diseases"
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("🤒 Symptom Checker", key="symptoms_btn", use_container_width=True, help="Check your symptoms"):
                st.session_state.current_section = "symptoms"
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if st.button("📄 Health Reports", key="reports_btn", use_container_width=True, help="View health metrics"):
                st.session_state.current_section = "reports"
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("💊 Treatment Plans", key="treatments_btn", use_container_width=False, help="Get personalized plans"):
        st.session_state.current_section = "treatments"
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

# Section Content
if nav_option == "Home":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.info("Welcome! Use the buttons above to explore health features")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Login":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 User Login")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login", key="login_btn"):
        if username and password:
            st.success(f"Welcome back, {username}! 🎉")
        else:
            st.warning("Please enter both username and password")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧾 User Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name", placeholder="John Doe")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    
    with col2:
        height = st.number_input("Height (cm)", min_value=50, max_value=250)
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
        if height > 0:
            bmi = weight / ((height / 100) ** 2)
            st.metric(label="BMI", value=f"{bmi:.2f}")
    
    if st.button("Calculate BMI", key="bmi_btn"):
        if height > 0:
            st.success(f"Your BMI: {bmi:.2f}")
            if bmi < 18.5:
                st.warning("Underweight")
            elif 18.5 <= bmi <= 24.9:
                st.success("Healthy weight")
            else:
                st.error("Overweight")
    
    if st.button("Save Profile", key="save_profile"):
        st.session_state.profile = {
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight
        }
        st.success("Profile saved successfully! ✅")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧠 Symptom Checker")
    symptoms = st.text_area("Describe your symptoms:", placeholder="e.g., headache, fever, cough")
    
    if st.button("Analyze Symptoms", key="analyze_btn"):
        with st.spinner("Analyzing..."):
            prompt = f"Medical analysis request: {symptoms}. Provide possible conditions and recommendations."
            response = llm.invoke(prompt)
            st.session_state.symptoms_history.append((symptoms, response))
            st.success("Analysis complete!")
    
    if st.session_state.symptoms_history:
        st.markdown('<div class="symptom-history">', unsafe_allow_html=True)
        st.subheader("📜 Symptom History")
        for symptom, analysis in st.session_state.symptoms_history:
            st.markdown(f"**Symptoms:** {symptom}")
            st.write(analysis)
            st.divider()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Chat":
    st.markdown('<div class="card chat-container">', unsafe_allow_html=True)
    st.subheader("🤖 Health Chatbot")
    user_input = st.text_input("Ask a question:", placeholder="e.g., How to lower cholesterol?")
    
    if st.button("Send", key="send_btn"):
        st.session_state.messages.append(("user", user_input))
        with st.spinner("Thinking..."):
            response = llm.invoke(user_input)
            st.session_state.messages.append(("bot", response))
    
    for role, msg in reversed(st.session_state.messages):
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot"><b>AI:</b> {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🫀 Chronic Disease Management")
    condition = st.selectbox("Select Condition", 
        ["Diabetes", "Hypertension", "Asthma", "Arthritis"])
    
    if condition == "Diabetes":
        st.markdown('<div class="glucose-chart">', unsafe_allow_html=True)
        glucose = st.number_input("Blood Glucose Level (mg/dL)", min_value=40, max_value=400)
        if st.button("Log Glucose", key="log_glucose"):
            st.session_state.glucose_log.append(glucose)
            st.success(f"Logged: {glucose} mg/dL")
        if st.session_state.glucose_log:
            df = pd.DataFrame(st.session_state.glucose_log, columns=["Glucose"])
            st.line_chart(df)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif condition == "Hypertension":
        st.markdown('<div class="bp-chart">', unsafe_allow_html=True)
        systolic = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=200)
        diastolic = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=140)
        if st.button("Log BP", key="log_bp"):
            st.session_state.bp_log.append((systolic, diastolic))
            st.success(f"Logged: {systolic}/{diastolic} mmHg")
        if st.session_state.bp_log:
            df = pd.DataFrame(st.session_state.bp_log, columns=["Systolic", "Diastolic"])
            st.line_chart(df)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif condition == "Asthma":
        st.markdown('<div class="asthma-chart">', unsafe_allow_html=True)
        triggers = st.multiselect("Triggers", ["Pollen", "Dust", "Smoke", "Cold Air"])
        severity = st.slider("Severity (1-10)", 1, 10)
        if st.button("Log Episode", key="log_asthma"):
            st.session_state.asthma_log.append({"triggers": triggers, "severity": severity})
            st.success("Episode logged successfully")
        if st.session_state.asthma_log:
            df = pd.DataFrame(st.session_state.asthma_log)
            st.bar_chart(df["severity"])
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Health Reports")
    days = st.slider("Select period (days)", 1, 30, 7)
    
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    heart_rates = [random.randint(60, 100) for _ in range(days)]
    glucose = [round(random.uniform(70, 140), 1) for _ in range(days)]
    bp = [(random.randint(110, 130), random.randint(70, 90)) for _ in range(days)]
    
    df = pd.DataFrame({
        "Date": dates,
        "Heart Rate": heart_rates,
        "Glucose": glucose,
        "Systolic BP": [x[0] for x in bp],
        "Diastolic BP": [x[1] for x in bp]
    })
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Average Heart Rate", f"{sum(heart_rates)//len(heart_rates)} bpm")
        st.line_chart(df.set_index("Date")[["Heart Rate"]])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Average Glucose", f"{sum(glucose)/len(glucose):.1f} mg/dL")
        st.line_chart(df.set_index("Date")[["Glucose"]])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Treatments":
    st.markdown('<div class="card treatment-plan">', unsafe_allow_html=True)
    st.subheader("💊 Treatment Planner")
    condition = st.text_input("Medical Condition", placeholder="e.g., Type 2 Diabetes")
    details = st.text_area("Patient Details", placeholder="Age, allergies, comorbidities")
    
    if st.button("Generate Plan", key="generate_plan"):
        prompt = f"Create treatment plan for {condition} in a patient with: {details}"
        response = llm.invoke(prompt)
        st.session_state.treatment_plan = response
        st.success("Plan generated successfully!")
    
    if st.session_state.treatment_plan:
        st.markdown("### 📄 Current Plan")
        st.write(st.session_state.treatment_plan)
    st.markdown('</div>', unsafe_allow_html=True)

elif nav_option == "Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚙️ Settings")
    st.write("Configuration options will be added soon")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("© 2025 Health Assistant | Made with ❤️ by Your Team", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
