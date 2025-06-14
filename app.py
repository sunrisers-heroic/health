import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS for better UI
st.markdown("""
    <style>
        body {
            background-color: #f9fbfd;
            font-family: Arial, sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }
        .card {
            background-color: #f9fcff;
            padding: 15px 20px;
            border-left: 5px solid #007acc;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"

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

# ------------------------------ SIDEBAR NAVIGATION ------------------------------
st.sidebar.title("🩺 Health Assistant")
page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "🔐 Login",
    "🧾 User Profile & Dashboard",
    "📊 Health Data Tracking",
    "💊 Medication Tracker",
    "📅 Appointment Scheduler",
    "🧠 AI Symptom Checker",
    "🧘 Mental Health Support",
    "🏋️ Fitness Planner",
    "📈 Progress Reports",
    "🫀 Chronic Disease Management",
    "👥 Community & Support",
    "🌐 Settings & Preferences"
])

# ------------------------------ LOGIN PAGE ------------------------------
if page == "🔐 Login":
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.session_state.user_logged_in = True
        st.success("Logged in successfully!")

# ------------------------------ HOME PAGE ------------------------------
if page == "🏠 Home":
    st.title("🩺 Welcome to Your Personalized Health Assistant")
    st.markdown("""
        This app helps you manage your health comprehensively — from symptom checks to fitness planning.
        
        Use the sidebar to navigate through different sections. Each module supports tracking, logging, and insights.

        ### 🧠 Highlights:
        - 💬 AI-Powered Symptom Checker  
        - 📊 Real-Time Health Metrics  
        - 🎯 Customizable Wellness Plans  
        - 🔐 Secure, Private, and Simple  

        Get started by exploring any of the tools below!
    """)

# ------------------------------ USER PROFILE ------------------------------
elif page == "🧾 User Profile & Dashboard":
    st.title("🧾 User Profile & Dashboard")
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
        st.session_state.profile = {
            "name": name, "age": age, "gender": gender,
            "height": height, "weight": weight
        }
        st.success("Profile saved!")

# ------------------------------ HEALTH DATA TRACKING ------------------------------
elif page == "📊 Health Data Tracking":
    st.title("📊 Health Data Tracking")
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

# ------------------------------ MEDICATION TRACKER ------------------------------
elif page == "💊 Medication Tracker":
    st.title("💊 Medication Tracker")
    med_name = st.text_input("Medication Name")
    dosage = st.text_input("Dosage")
    time = st.time_input("Time to Take")
    note = st.text_area("Notes")
    
    if st.button("Add Medication"):
        st.session_state.medications.append({
            "name": med_name,
            "dosage": dosage,
            "time": str(time),
            "note": note
        })
        st.success("Medication added!")
    
    st.subheader("Your Medications")
    if st.session_state.medications:
        for idx, med in enumerate(st.session_state.medications):
            st.markdown(f"{idx+1}. **{med['name']}** - {med['dosage']} at {med['time']} ({med['note']})")
    else:
        st.info("No medications added yet.")

# ------------------------------ APPOINTMENT SCHEDULER ------------------------------
elif page == "📅 Appointment Scheduler":
    st.title("📅 Appointment Scheduler")
    date = st.date_input("Select Date")
    doctor = st.text_input("Doctor/Service")
    reason = st.text_area("Reason for Visit")
    remind = st.checkbox("Set Reminder")
    
    if st.button("Book Appointment"):
        st.session_state.appointments.append({
            "date": str(date),
            "doctor": doctor,
            "reason": reason,
            "reminder": remind
        })
        st.success(f"Appointment with {doctor} on {date} booked.")
    
    st.subheader("Upcoming Appointments")
    if st.session_state.appointments:
        for appt in st.session_state.appointments:
            st.markdown(f"- **{appt['doctor']}** on {appt['date']} ({appt['reason']})")
            if appt['reminder']:
                st.caption("🔔 Reminder set.")
    else:
        st.info("No appointments scheduled.")

# ------------------------------ AI SYMPTOM CHECKER ------------------------------
elif page == "🧠 AI Symptom Checker":
    st.title("🧠 AI Symptom Checker")
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

# ------------------------------ MENTAL HEALTH ------------------------------
elif page == "🧘 Mental Health Support":
    st.title("🧘 Mental Health Support")
    mood = st.slider("Rate your mood today", 1, 10)
    journal = st.text_area("Journal Entry")
    if st.button("Save Mood & Journal"):
        st.success("Saved!")
    st.markdown("### Breathing Exercise")
    if st.button("Start Exercise"):
        st.info("Breathe in... Hold... Breathe out...")

# ------------------------------ FITNESS PLANNER ------------------------------
elif page == "🏋️ Fitness Planner":
    st.title("🏋️ Fitness Planner")
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
    days = st.multiselect("Days Available", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    plan = st.text_area("Workout Plan")
    if st.button("Save Plan"):
        st.session_state.fitness_plan = {
            "goal": goal,
            "days": ", ".join(days),
            "plan": plan
        }
        st.success("Plan saved!")
    
    if "fitness_plan" in st.session_state:
        st.markdown("### Current Plan")
        st.write(st.session_state.fitness_plan)

# ------------------------------ PROGRESS REPORTS ------------------------------
elif page == "📈 Progress Reports":
    st.title("📈 Progress Reports")
    st.markdown("### Weekly Summary")
    st.line_chart([10, 20, 30, 25, 40])
    st.bar_chart({"Week 1": [20], "Week 2": [25], "Week 3": [30]})
    if st.button("Export Report"):
        df = pd.DataFrame([st.session_state.health_data])  # Wrap dict in list for DataFrame
        st.download_button("Download as CSV", data=df.to_csv(index=False), file_name="health_report.csv")
        st.success("Report exported as CSV!")

# ------------------------------ CHRONIC DISEASE MANAGEMENT ------------------------------
elif page == "🫀 Chronic Disease Management":
    st.title("🫀 Chronic Disease Management")
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

# ------------------------------ COMMUNITY & SUPPORT ------------------------------
elif page == "👥 Community & Support":
    st.title("👥 Community & Support")
    post = st.text_input("Write a post...")
    if st.button("Post"):
        st.session_state.posts.append(post)
    st.markdown("### Recent Posts")
    for p in st.session_state.posts:
        st.markdown(f"- {p}")

# ------------------------------ SETTINGS ------------------------------
elif page == "🌐 Settings & Preferences":
    st.title("🌐 Settings & Preferences")
    language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
    theme = st.selectbox("Theme", ["Light", "Dark"])
    font_size = st.slider("Font Size", 12, 24)
    if st.button("Save Preferences"):
        st.success("Preferences updated!")

# ------------------------------ FOOTER ------------------------------
st.markdown("---")
st.markdown("© 2025 MyHospital Health Assistant | Built with ❤️ using Streamlit & Watsonx")

# ------------------------------ DEBUG MODE (Optional) ------------------------------
with st.expander("🔧 Debug Mode"):
    st.write("Session State:", st.session_state)
