import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from datetime import datetime
from fpdf import FPDF
import json
import os
import random
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS - Violet and Pink Theme
st.markdown("""
    <style>
        body { background-color: #f5e6fa; font-family: 'Segoe UI', sans-serif; }
        .main { background-color: #ffffff; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .card { background-color: #ffffff; padding: 25px; margin: 20px 0; border-left: 6px solid #8e44ad; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .navbar { display: flex; justify-content: center; gap: 20px; padding: 15px 0; background: linear-gradient(to right, #8e44ad, #ec7063); border-radius: 10px; margin-bottom: 25px; }
        .nav-button { background-color: #ffffff; color: #8e44ad; border: none; width: 50px; height: 50px; font-size: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s ease; }
        .nav-button:hover { background-color: #f9ebf7; transform: scale(1.1); }
        h1, h2, h3 { color: #8e44ad; }
        label { font-weight: bold; color: #34495e; }
        input, select, textarea { border-radius: 8px; border: 1px solid #ccc; padding: 10px; width: 100%; font-size: 14px; }
        button { background-color: #8e44ad; color: white; border: none; padding: 10px 20px; font-size: 14px; border-radius: 8px; cursor: pointer; }
        button:hover { background-color: #732d91; }
        .user-bubble, .bot-bubble { padding: 10px 15px; border-radius: 12px; max-width: 70%; margin: 6px 0; font-size: 14px; }
        .user-bubble { background-color: #dcd6f7; align-self: flex-end; }
        .bot-bubble { background-color: #f2d7d5; align-self: flex-start; }
        .chat-container { display: flex; flex-direction: column; gap: 10px; }
        .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #8e44ad; margin: 10px 0; }
        .trend-up { color: #27ae60; }
        .trend-down { color: #e74c3c; }
    </style>
""", unsafe_allow_html=True)

# Language translations for healthcare domain
LANGUAGES = {
    "en": {
        "title": "🩺 Health Assistant",
        "subtitle": "Ask about symptoms, treatments, diagnostics, and wellness.",
        "home_welcome": "🩺 Welcome to Your Personalized Health Assistant",
        "highlights": "### 🧠 Highlights:",
        "chat": "🤖 AI Chatbot",
        "symptoms": "🧠 Symptom Checker",
        "treatment": "💊 Treatment Planner",
        "diseases": "🫀 Chronic Disease Management",
        "reports": "📈 Progress Reports",
        "settings": "⚙️ Settings & Preferences",
        "footer": "© 2025 MyHospital Health Assistant | Built with ❤️ using Streamlit & Watsonx",
        "save_profile": "Save Profile",
        "generate_ai_report": "Generate AI Report Summary",
        "export_pdf": "📄 Export Report as PDF"
    },
    "es": {
        "title": "🩺 Asistente de Salud",
        "subtitle": "Pregunte sobre síntomas, tratamientos y bienestar general.",
        "home_welcome": "🩺 Bienvenido a su Asistente de Salud Personalizado",
        "highlights": "### 🧠 Destacados:",
        "chat": "🤖 Chatbot con IA",
        "symptoms": "🧠 Revisión de Síntomas",
        "treatment": "💊 Plan de Tratamiento",
        "diseases": "🫀 Manejo de Enfermedades Crónicas",
        "reports": "📈 Informes de Progreso",
        "settings": "⚙️ Configuración y Preferencias",
        "footer": "© 2025 Asistente de Salud | Hecho con ❤️ usando Streamlit & Watsonx",
        "save_profile": "Guardar Perfil",
        "generate_ai_report": "Generar Informe con IA",
        "export_pdf": "📄 Exportar Informe como PDF"
    },
    "fr": {
        "title": "🩺 Assistant Santé",
        "subtitle": "Posez des questions sur les symptômes, traitements et bien-être.",
        "home_welcome": "🩺 Bienvenue dans votre Assistant Santé Personnel",
        "highlights": "### 🧠 Points forts :",
        "chat": "🤖 Chatbot avec IA",
        "symptoms": "🧠 Analyse des Symptômes",
        "treatment": "💊 Plan de Traitement",
        "diseases": "🫀 Suivi des Maladies Chroniques",
        "reports": "📈 Rapports de Suivi",
        "settings": "⚙️ Paramètres et Préférences",
        "footer": "© 2025 Assistant Santé | Réalisé avec ❤️ en utilisant Streamlit & Watsonx",
        "save_profile": "Enregistrer le Profil",
        "generate_ai_report": "Générer un Résumé IA",
        "export_pdf": "📄 Exporter le Rapport en PDF"
    }
}

# Initialize session state
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}
if "current_section" not in st.session_state:
    st.session_state.current_section = "profile"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "health_data" not in st.session_state:
    st.session_state.health_data = {}
if "language" not in st.session_state:
    st.session_state.language = "en"
if "glucose_log" not in st.session_state:
    st.session_state.glucose_log = []
if "bp_log" not in st.session_state:
    st.session_state.bp_log = []
if "asthma_log" not in st.session_state:
    st.session_state.asthma_log = []
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = {
        "heart_rates": [72],
        "glucose_levels": [90],
        "dates": [datetime.now().strftime("%Y-%m-%d")]
    }

# Load Watsonx credentials
try:
    credentials = {
        "url": st.secrets["WATSONX_URL"],
        "apikey": st.secrets["WATSONX_APIKEY"]
    }
    project_id = st.secrets["WATSONX_PROJECT_ID"]
    
    model_map = {
        "chat": "ibm/granite-13b-instruct-v2",
        "symptoms": "ibm/granite-13b-instruct-v2",
        "treatment": "ibm/granite-13b-instruct-v2",
        "diseases": "ibm/granite-13b-instruct-v2",
        "reports": "ibm/granite-13b-instruct-v2"
    }
    
    def get_llm(model_name):
        return WatsonxLLM(
            model_id=model_map[model_name],
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.TEMPERATURE: 0.7,
                GenParams.MIN_NEW_TOKENS: 5,
                GenParams.MAX_NEW_TOKENS: 300,
                GenParams.STOP_SEQUENCES: ["Human:", "Observation"],
            },
        )
except KeyError:
    st.warning("⚠️ Watsonx credentials missing.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Error initializing LLM: {str(e)}")
    st.stop()

# Function to export data as PDF including user profile
def export_health_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # Add Title
    pdf.cell(0, 10, txt="HealthAI - Personalized Health Report", ln=True, align='C')
    pdf.ln(10)
    
    # Add User Info
    if "profile_data" in st.session_state and st.session_state.profile_data:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt="User Information", ln=True)
        pdf.set_font("Arial", '', 12)
        for key, value in st.session_state.profile_data.items():
            pdf.cell(0, 10, txt=f"{key.capitalize()}: {value}", ln=True)
    
    # Add Metrics
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Recent Health Metrics", ln=True)
    pdf.set_font("Arial", '', 12)
    
    if st.session_state.health_data:
        for key, value in st.session_state.health_data.items():
            pdf.cell(0, 10, txt=f"{key.replace('_', ' ').capitalize()}: {value}", ln=True)
    else:
        pdf.cell(0, 10, txt="No health metrics recorded yet.", ln=True)
    
    pdf.output("health_report.pdf")
    return open("health_report.pdf", "rb").read()

# Navigation Bar
def render_navbar():
    lang = st.session_state.language
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("챗", key="btn_chat", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "chat"
    with col2:
        if st.button("🧠", key="btn_symptoms", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "symptoms"
    with col3:
        if st.button("💊", key="btn_treatment", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "treatment"
    with col4:
        if st.button("🫀", key="btn_diseases", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "diseases"
    with col5:
        if st.button("📊", key="btn_reports", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "reports"
    with col6:
        if st.button("🧾", key="btn_profile", use_container_width=True):
            st.session_state.current_section = "profile"
    with col7:
        if st.button("⚙️", key="btn_settings", use_container_width=True):
            st.session_state.current_section = "settings"
    st.markdown('</div>', unsafe_allow_html=True)

# Header
lang = st.session_state.language
st.markdown(f'<h1 style="text-align:center;">{LANGUAGES[lang]["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; font-size:16px;">{LANGUAGES[lang]["subtitle"]}</p>', unsafe_allow_html=True)

# Show navigation bar only if profile is complete
render_navbar()

# Functions
def save_profile(name, age, gender, height, weight):
    st.session_state.profile_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "bmi": round(weight / ((height / 100) ** 2), 1)
    }
    st.session_state.profile_complete = True
    st.success("✅ Profile saved successfully!")

def reset_profile():
    st.session_state.profile_complete = False
    st.session_state.profile_data = {}
    st.session_state.messages = []
    st.session_state.glucose_log = []
    st.session_state.bp_log = []
    st.session_state.asthma_log = []
    st.session_state.health_data = {}
    st.session_state.analytics_data = {
        "heart_rates": [72],
        "glucose_levels": [90],
        "dates": [datetime.now().strftime("%Y-%m-%d")]
    }
    st.rerun()

# ------------------------------ SETTINGS ------------------------------
if st.session_state.current_section == "settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h2>⚙️ {LANGUAGES[lang]["settings"]}</h2>', unsafe_allow_html=True)

    st.markdown("### 🌍 Language & Localization")
    language = st.selectbox(
        "Select Language",
        options=["en", "es", "fr"],
        format_func=lambda x: {"en": "English 🇬🇧", "es": "Español 🇪🇸", "fr": "Français 🇫🇷"}[x],
        help="Choose the display language for the app interface."
    )

    st.markdown("### 🎨 Theme Preferences")
    theme = st.selectbox(
        "Color Theme",
        ["Light"],
        disabled=True,
        help="Currently only Light theme is available. More themes coming soon!"
    )

    st.markdown("### 🔤 Text Display")
    font_size = st.slider(
        "Font Size (px)",
        min_value=12,
        max_value=24,
        value=16,
        step=1,
        help="Adjust the base font size for easier reading."
    )

    # Save Button
    if st.button("💾 Save Preferences"):
        st.session_state.language = language
        st.session_state.font_size = font_size
        st.success("✅ Your preferences have been saved successfully!")

    st.markdown("#### Tip: Changes apply immediately to the app interface.")

    st.markdown('</div>')
# ------------------------------ USER PROFILE ------------------------------
elif st.session_state.current_section == "profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧾 Complete Your Profile</h2>', unsafe_allow_html=True)
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
    
    if st.button("Save Profile"):
        if name and age > 0 and height > 0 and weight > 0:
            save_profile(name, age, gender, height, weight)
        else:
            st.error("❌ Please fill in all fields.")
    
    if st.session_state.profile_complete:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🔄 Reset Profile"):
            reset_profile()
    
    st.markdown('</div>')

# If profile not completed, stop further access
elif not st.session_state.profile_complete:
    st.info("ℹ️ Please complete your profile before continuing.")
    if st.button("Go to Profile"):
        st.session_state.current_section = "profile"
    st.stop()

# ------------------------------ CHATBOT ------------------------------
elif st.session_state.current_section == "chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🤖 Enhanced Health Assistant Chatbot</h2>', unsafe_allow_html=True)

    # Display chat messages
    for role, content in st.session_state.messages:
        bubble_class = "user-bubble" if role == "user" else "bot-bubble"
        st.markdown(f'<div class="{bubble_class}"><b>{role.capitalize()}:</b> {content}</div>', unsafe_allow_html=True)

    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your question:", placeholder="Ask about symptoms, medications, wellness tips, etc.")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))

        # Build context from profile
        profile_info = "\n".join([f"{k.capitalize()}: {v}" for k, v in st.session_state.profile_data.items()])

        # Categorize query type
        query_lower = user_input.lower()
        category = "general"

        if any(word in query_lower for word in ["symptom", "pain", "ache", "fever", "headache"]):
            category = "symptoms"
        elif any(word in query_lower for word in ["treat", "medication", "therapy", "prescribe"]):
            category = "treatment"
        elif any(word in query_lower for word in ["glucose", "blood sugar", "insulin", "bp", "pressure"]):
            category = "diseases"
        elif any(word in query_lower for word in ["ai", "report", "analyze", "summary"]):
            category = "reports"

        # Prepare enhanced prompt
        prompt = f"""
You are a professional medical assistant AI helping a patient with their health queries.
Use the following guidelines:
- Be empathetic, informative, and clear.
- Always mention that you're not a substitute for real medical advice.
- If unsure, recommend consulting a physician.

Patient Profile:
{profile_info}

Chat History:
{''.join([f'{r.capitalize()}: {c}\n' for r, c in st.session_state.messages[-6:]])}

User Question: "{user_input}"

Based on the question category ("{category}"), provide a detailed response that includes:
1. Medical interpretation of the query
2. Possible causes or implications
3. Suggested actions or precautions
4. When to consult a doctor

Answer:"""

        try:
            llm = get_llm("chat")
            with st.spinner("🧠 Analyzing query..."):
                response = llm.invoke(prompt).strip()
                if not response or "error" in response.lower():
                    response = "I'm unable to respond at this time due to technical issues. Please try again later."
                st.session_state.messages.append(("assistant", response))
                st.rerun()

        except Exception as e:
            st.session_state.messages.append(("assistant", f"🚨 Error processing request: {str(e)}"))
            st.rerun()

    st.markdown('</div>')

# ------------------------------ SYMPTOM CHECKER ------------------------------
elif st.session_state.current_section == "symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧠 Symptom Checker (Disease Identifier)</h2>', unsafe_allow_html=True)
    
    symptom_description = st.text_area(
        "Describe your symptoms (e.g., headache, fever, fatigue):",
        placeholder="Example: 'I have chest pain, shortness of breath, and feel dizzy.'"
    )
    
    if st.button("Check Symptoms"):
        if symptom_description.strip() == "":
            st.warning("⚠️ Please describe your symptoms.")
        else:
            # Build prompt to ask for possible conditions
            prompt = f"""
You are a medical AI assistant. Based on the following symptoms, list the most likely conditions or diseases from most to least probable.

Patient Profile:
Name: {st.session_state.profile_data.get('name', 'Unknown')}
Age: {st.session_state.profile_data.get('age', 'Unknown')}
Gender: {st.session_state.profile_data.get('gender', 'Unknown')}

Symptoms: {symptom_description}

Provide a structured response with:
1. Most likely condition with brief explanation
2. Alternative possibilities
3. Likelihood percentages
4. Recommended next steps

Keep it concise and professional.
"""
            try:
                llm = get_llm("symptoms")
                response = llm.invoke(prompt).strip()
                
                if not response or response.lower() in ["online", "none", "no result"]:
                    st.error("🚨 Could not retrieve valid diagnosis from AI. Try again later.")
                else:
                    st.markdown(f"🩺 **Diagnosis Results:**\n\n{response}")
                    
                    # Store in health analytics
                    st.session_state.analytics_data["dates"].append(datetime.now().strftime("%Y-%m-%d"))
                    st.session_state.analytics_data["heart_rates"].append(random.randint(60, 100))
                    st.session_state.analytics_data["glucose_levels"].append(random.randint(70, 130))
                    
            except Exception as e:
                st.error(f"🚨 Error getting diagnosis: {str(e)}")
    
    st.markdown('</div>')

# ------------------------------ TREATMENT PLANNER ------------------------------
elif st.session_state.current_section == "treatment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>💊 Personalized Treatment Suggestions</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        condition = st.text_input("Condition or Diagnosis")
    with col2:
        duration = st.selectbox("Duration", ["Acute (short-term)", "Chronic (long-term)"])
    
    st.subheader("Patient Profile")
    profile_text = ""
    for key, value in st.session_state.profile_data.items():
        profile_text += f"{key.capitalize()}: {value}\n"
    
    st.markdown(f'<div class="metric-card">{profile_text}</div>', unsafe_allow_html=True)
    
    if st.button("Generate Treatment Plan"):
        if condition.strip() == "":
            st.warning("⚠️ Please enter a condition.")
        else:
            # Build treatment plan prompt
            prompt = f"""
Based on the following patient profile and condition, create a personalized treatment plan:

Patient Profile:
Name: {st.session_state.profile_data.get('name', 'Unknown')}
Age: {st.session_state.profile_data.get('age', 'Unknown')}
Gender: {st.session_state.profile_data.get('gender', 'Unknown')}
BMI: {st.session_state.profile_data.get('bmi', 'Unknown')}

Condition: {condition}
Duration: {duration}

Include:
1. Medications (with dosages and frequency)
2. Lifestyle modifications
3. Follow-up care recommendations
4. Potential complications to monitor
"""
            try:
                llm = get_llm("treatment")
                response = llm.invoke(prompt).strip()
                
                if not response or response.lower() in ["online", "none", "no result"]:
                    st.error("🚨 Could not retrieve valid treatment plan.")
                else:
                    st.markdown(f"💡 **Personalized Treatment Plan:**\n\n{response}")
                    
            except Exception as e:
                st.error(f"🚨 Error generating treatment plan: {str(e)}")
    
    st.markdown('</div>')

# ------------------------------ DISEASE MANAGEMENT ------------------------------
elif st.session_state.current_section == "diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🫀 Chronic Disease Logs</h2>', unsafe_allow_html=True)
    
    condition = st.selectbox("Condition", ["Diabetes", "Hypertension", "Asthma"])
    
    if condition == "Diabetes":
        glucose = st.number_input("Blood Glucose Level (mg/dL)", min_value=40, max_value=400, step=5)
        if st.button("Log Glucose"):
            st.session_state.glucose_log.append(glucose)
            st.success(f"Logged: {glucose} mg/dL")
            
            # Generate AI advice
            prompt = f"My blood sugar is {glucose}. Is it normal? What should I do?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n\n{advice}")
            
    elif condition == "Hypertension":
        systolic = st.number_input("Systolic BP", min_value=90, max_value=200, value=120)
        diastolic = st.number_input("Diastolic BP", min_value=60, max_value=130, value=80)
        
        if st.button("Log BP"):
            st.session_state.bp_log.append((systolic, diastolic))
            st.success(f"Logged: {systolic}/{diastolic} mmHg")
            
            # Generate AI advice
            prompt = f"My blood pressure is {systolic}/{diastolic} mmHg. What does that mean?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n\n{advice}")
            
    elif condition == "Asthma":
        triggers = st.text_area("Triggers Today (e.g., pollen, dust)")
        severity = st.slider("Severity (1-10)", 1, 10)
        
        if st.button("Log Asthma Episode"):
            st.session_state.asthma_log.append({"triggers": triggers, "severity": severity})
            st.success("Episode logged.")
            
            # Generate AI advice
            prompt = f"What are some ways to avoid asthma triggers like {triggers}?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n\n{advice}")
    
    st.markdown('</div>')

# ------------------------------ PROGRESS REPORTS ------------------------------
elif st.session_state.current_section == "reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>📈 Health Analytics Dashboard</h2>', unsafe_allow_html=True)

    # --------------------------
    # New: Manual Data Input Section
    # --------------------------
    st.markdown("### 📝 Log New Health Metrics")
    col_input1, col_input2, col_input3 = st.columns(3)
    with col_input1:
        new_date = st.date_input("Select Date", value=datetime.today())
    with col_input2:
        new_hr = st.number_input("Heart Rate (bpm)", min_value=40, max_value=140, step=1)
    with col_input3:
        new_glucose = st.number_input("Blood Glucose (mg/dL)", min_value=50, max_value=200, step=1)

    if st.button("➕ Add Metric"):
        if new_hr > 0 and new_glucose > 0:
            st.session_state.analytics_data["dates"].append(new_date.strftime("%Y-%m-%d"))
            st.session_state.analytics_data["heart_rates"].append(new_hr)
            st.session_state.analytics_data["glucose_levels"].append(new_glucose)
            st.success("✅ Metric added successfully!")
        else:
            st.warning("⚠️ Please enter valid values for both metrics.")

    # --------------------------
    # Existing Visualization Code (unchanged)
    # --------------------------
    dates = st.session_state.analytics_data["dates"]
    heart_rates = st.session_state.analytics_data["heart_rates"]
    glucose_levels = st.session_state.analytics_data["glucose_levels"]

    df = pd.DataFrame({
        'Date': dates,
        'Heart Rate': heart_rates,
        'Blood Glucose': glucose_levels
    })

    # Heart rate chart
    st.markdown("### ❤️ Heart Rate Trends")
    fig_hr = px.line(df, x='Date', y='Heart Rate', title='Heart Rate Over Time', markers=True)
    fig_hr.update_layout(yaxis_range=[40, 140], template="plotly_white")
    st.plotly_chart(fig_hr, use_container_width=True)

    # Blood glucose chart
    st.markdown("### 🩸 Blood Glucose Levels")
    fig_glucose = px.line(df, x='Date', y='Blood Glucose', title='Blood Glucose Levels Over Time', markers=True)
    fig_glucose.update_layout(yaxis_range=[50, 200], template="plotly_white")
    st.plotly_chart(fig_glucose, use_container_width=True)

    # BMI Metric
    if st.session_state.profile_data.get('bmi'):
        bmi = st.session_state.profile_data['bmi']
        st.markdown(f"### 📏 BMI: {bmi} kg/m²")
        if bmi < 18.5:
            st.warning("Underweight")
        elif 18.5 <= bmi < 24.9:
            st.success("Healthy Weight")
        elif 25 <= bmi < 29.9:
            st.warning("Overweight")
        else:
            st.error("Obese")

    # Metric summary with trend indicators
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Latest Metrics")
        latest_date = dates[-1] if len(dates) > 0 else "N/A"
        latest_hr = heart_rates[-1] if len(heart_rates) > 0 else "N/A"
        latest_glucose = glucose_levels[-1] if len(glucose_levels) > 0 else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <strong>Date:</strong> {latest_date}<br>
            <strong>Heart Rate:</strong> {latest_hr} bpm<br>
            <strong>Blood Glucose:</strong> {latest_glucose} mg/dL
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📈 Trend Analysis")
        hr_trend = "↑" if len(heart_rates) > 1 and heart_rates[-1] > heart_rates[-2] else "↓" if len(heart_rates) > 1 else "-"
        glucose_trend = "↑" if len(glucose_levels) > 1 and glucose_levels[-1] > glucose_levels[-2] else "↓" if len(glucose_levels) > 1 else "-"

        st.markdown(f"""
        <div class="metric-card">
            <strong>Heart Rate Trend:</strong> {hr_trend} 
            <span class="{'trend-up' if hr_trend == '↑' else 'trend-down'}">{heart_rates[-1] if len(heart_rates) > 0 else '?'}</span><br>
            <strong>Glucose Trend:</strong> {glucose_trend} 
            <span class="{'trend-up' if glucose_trend == '↑' else 'trend-down'}">{glucose_levels[-1] if len(glucose_levels) > 0 else '?'}</span>
        </div>
        """, unsafe_allow_html=True)

    # Statistical Summary
    st.markdown("### 📋 Summary Statistics")
    col3, col4 = st.columns(2)
    with col3:
        avg_hr = round(sum(heart_rates) / len(heart_rates), 1) if heart_rates else "N/A"
        min_hr = min(heart_rates) if heart_rates else "N/A"
        max_hr = max(heart_rates) if heart_rates else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <strong>Average Heart Rate:</strong> {avg_hr} bpm<br>
            <strong>Min/Max HR:</strong> {min_hr}-{max_hr} bpm
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_gluc = round(sum(glucose_levels) / len(glucose_levels), 1) if glucose_levels else "N/A"
        min_gluc = min(glucose_levels) if glucose_levels else "N/A"
        max_gluc = max(glucose_levels) if glucose_levels else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <strong>Average Glucose:</strong> {avg_gluc} mg/dL<br>
            <strong>Min/Max Glucose:</strong> {min_gluc}-{max_gluc} mg/dL
        </div>
        """, unsafe_allow_html=True)

    # Generate AI Insights
    if st.button("Generate Enhanced AI Insights"):
        prompt = f"""
You are a medical AI assistant analyzing health trends. Provide comprehensive insights based on the following patient data:

Patient Profile:
- Name: {st.session_state.profile_data.get('name', 'Unknown')}
- Age: {st.session_state.profile_data.get('age', 'Unknown')}
- Gender: {st.session_state.profile_data.get('gender', 'Unknown')}
- BMI: {st.session_state.profile_data.get('bmi', 'Unknown')}

Recent Metrics:
- Last 7 Heart Rates: {', '.join(map(str, heart_rates[-7:]))}
- Average Heart Rate: {round(sum(heart_rates)/len(heart_rates), 1) if heart_rates else 'N/A'}
- Last 7 Glucose Levels: {', '.join(map(str, glucose_levels[-7:]))}
- Average Glucose Level: {round(sum(glucose_levels)/len(glucose_levels), 1) if glucose_levels else 'N/A'}

Include:
1. Interpretation of trends (increasing/decreasing/stable)
2. Potential health implications
3. Personalized lifestyle or dietary recommendations
4. Suggestions for further testing or specialist consultation
5. Risk assessment based on BMI and metrics

Keep the response professional, easy to understand, and tailored to the individual's profile.
"""

        try:
            llm = get_llm("reports")
            analysis = llm.invoke(prompt)
            st.markdown(f"🧠 **AI Analysis:**{analysis}")
        except Exception as e:
            st.error(f"🚨 Error generating analysis: {str(e)}")

    # Export PDF
    if st.session_state.profile_complete:
        st.download_button(
            label=LANGUAGES[lang]["export_pdf"],
            data=export_health_report(),
            file_name="health_report.pdf",
            mime="application/pdf"
        )

    st.markdown('</div>')
# Footer
lang = st.session_state.language
st.markdown(f'<p style="text-align:center; font-size:14px;">{LANGUAGES[lang]["footer"]}</p>', unsafe_allow_html=True)

# Debug Mode
with st.expander("🔧 Debug Mode"):
    st.write("Session State:", st.session_state)
