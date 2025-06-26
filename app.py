# app.py 

# Importing Libraries
import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import os
import random
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS - Enhanced Violet and Pink Theme with Borders and Latin Math Font
st.markdown("""
<style>
* {box-sizing: border-box; margin: 0; padding: 0;}
body {background: linear-gradient(to right bottom, #f5e6fa, #ffe5f5); font-family: 'Latin Modern Math', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #2c3e50; line-height: 1.6; padding: 20px;}
h1,h2,h3,h4,h5,h6 {color: #8e44ad; font-weight: 600; margin-bottom: 10px;}
p {font-size: 16px; color: #34495e;}
a {color: #8e44ad; text-decoration: none;} a:hover {text-decoration: underline;}
.main {background-color: #ffffffcc; backdrop-filter: blur(10px); border-radius: 16px; padding: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); max-width: 1200px; margin: auto; animation: fadeIn 0.5s ease-in-out; border: 2px solid #ddd;}
@keyframes fadeIn {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);}}
.card {background-color: #fff; border-left: 6px solid #8e44ad; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: all 0.3s ease; border: 1px solid #eee;} 
.card:hover {transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.1);}
.navbar {display: flex; justify-content: center; gap: 20px; padding: 15px 0; background: linear-gradient(to right, #8e44ad, #ec7063); border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 16px rgba(0,0,0,0.15); position: sticky; top: 0; z-index: 999; transition: all 0.3s ease;}
.nav-button {background-color: #ffffff; color: #8e44ad; border: none; width: 60px; height: 60px; font-size: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}
.nav-button:hover {background-color: #f9ebf7; transform: scale(1.1);}
.nav-button:disabled {opacity: 0.5; cursor: not-allowed;}
label {font-weight: bold; color: #34495e; display: block; margin-top: 15px; margin-bottom: 6px;}
input,select,textarea,.stTextInput input,.stNumberInput input,.stDateInput input {border-radius: 8px; border: 1px solid #ccc; padding: 12px 14px; width: 100%; font-size: 14px; outline: none; transition: all 0.3s ease;}
input:focus,select:focus,textarea:focus,.stTextInput input:focus,.stNumberInput input:focus,.stDateInput input:focus {border-color: #8e44ad; box-shadow: 0 0 0 2px rgba(142,68,173,0.2);}
button {background-color: #8e44ad; color: white; border: none; padding: 12px 20px; font-size: 14px; border-radius: 8px; cursor: pointer; transition: background-color 0.3s ease, transform 0.2s ease;}
button:hover {background-color: #732d91; transform: translateY(-2px);}
button:active {transform: translateY(0);}
.chat-container {display: flex; flex-direction: column; gap: 10px; max-height: 400px; overflow-y: auto; padding-right: 10px;}
.user-bubble,.bot-bubble {padding: 12px 18px; border-radius: 16px; max-width: 75%; font-size: 14px; word-wrap: break-word; line-height: 1.5;}
.user-bubble {align-self: flex-end; background-color: #dcd6f7; border-radius: 16px 8px 8px 16px;}
.bot-bubble {align-self: flex-start; background-color: #f2d7d5; border-radius: 8px 16px 16px 8px;}
.metric-card {background-color: #f8f9fa; padding: 18px; border-radius: 10px; border-left: 4px solid #8e44ad; margin: 12px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.05); transition: transform 0.2s ease;}
.metric-card:hover {transform: translateX(5px);}
.trend-up {color: #27ae60; font-weight: bold;}
.trend-down {color: #e74c3c; font-weight: bold;}
.icon-button {display: inline-flex; align-items: center; gap: 8px; background-color: #8e44ad; color: white; padding: 10px 16px; border-radius: 8px; font-size: 14px; cursor: pointer; transition: all 0.3s ease;}
.icon-button:hover {background-color: #732d91; transform: scale(1.02);}
::-webkit-scrollbar {width: 8px;}
::-webkit-scrollbar-track {background: #f1f1f1; border-radius: 4px;}
::-webkit-scrollbar-thumb {background: #ddd; border-radius: 4px;}
::-webkit-scrollbar-thumb:hover {background: #bbb;}
@media (max-width: 768px) {.navbar {flex-wrap: wrap;} .nav-button {width: 50px; height: 50px; font-size: 20px;} .main {padding: 20px;} .card {padding: 20px;}}
.stAlert {border-radius: 10px; padding: 12px 16px; margin: 10px 0; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);}
.st-success {background-color: #dff0d8; color: #3c763d; border-left: 4px solid #3c763d;}
.st-warning {background-color: #fcf8e3; color: #8a6d3b; border-left: 4px solid #8a6d3b;}
.st-error {background-color: #f2dede; color: #a94442; border-left: 4px solid #a94442;}
footer {text-align: center; margin-top: 40px; font-size: 14px; color: #555; padding: 20px; border-top: 1px solid #eee;}
.plotly-graph-div {background-color: #fff !important; border-radius: 10px; padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);}
.stTabs > div > div {background-color: transparent; border-bottom: 2px solid #ddd;}
.stTabs > div > div > button {color: #8e44ad; font-weight: 600;}
.stTabs > div > div > button[aria-selected="true"] {color: #732d91; border-bottom: 2px solid #732d91;}
.stDownloadButton > button {background-color: #2ecc71 !important; border-color: #2ecc71 !important;}
.stDownloadButton > button:hover {background-color: #27ae60 !important;}
.ai-analysis {background-color: #fefefe; padding: 16px; border-left: 4px solid #8e44ad; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); font-size: 14px; white-space: pre-wrap;}
.stDateInput input {padding: 10px;}
.tooltip-label {display: flex; align-items: center; gap: 6px; font-weight: bold; color: #34495e; cursor: help;}
.tooltip-text {visibility: hidden; width: 200px; background: #333; color: #fff; text-align: center; border-radius: 4px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -100px; opacity: 0; transition: opacity 0.3s;}
.tooltip-label:hover .tooltip-text {visibility: visible; opacity: 1;}
.floating-btn {position: fixed; bottom: 20px; right: 20px; z-index: 999; background-color: #8e44ad; color: white; border: none; border-radius: 50%; width: 60px; height: 60px; font-size: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); transition: all 0.3s ease;}
.floating-btn:hover {background-color: #732d91; transform: scale(1.1);}
table {width: 100%; border-collapse: collapse; margin: 15px 0;}
th,td {padding: 12px; text-align: left; border-bottom: 1px solid #ddd;}
th {background-color: #f2f2f2; color: #333;}
tr:hover {background-color: #f9f9f9;}
.progress-bar {height: 12px; background-color: #eee; border-radius: 6px; overflow: hidden; margin: 10px 0;}
.progress-fill {height: 100%; background-color: #8e44ad; border-radius: 6px; transition: width 0.5s ease-in-out;}
.custom-checkbox {display: flex; align-items: center; gap: 10px; margin: 10px 0;}
.custom-checkbox input[type="checkbox"] {appearance: none; width: 20px; height: 20px; border: 2px solid #aaa; border-radius: 4px; cursor: pointer;}
.custom-checkbox input[type="checkbox"]:checked {background-color: #8e44ad; border-color: #732d91;}
.custom-checkbox input[type="checkbox"]:checked::after {content: "✔"; color: white; display: block; text-align: center; font-size: 14px;}
.toast {position: fixed; bottom: 20px; right: 20px; background-color: #2ecc71; color: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); animation: toastIn 0.3s ease-in-out forwards; z-index: 1000;}
@keyframes toastIn {from {transform: translateY(20px); opacity: 0;} to {transform: translateY(0); opacity: 1;}}
.js-plotly-plot .plotly .hoverlayer .xtitle, .js-plotly-plot .plotly .hoverlayer .ytitle {fill: #8e44ad !important;}
.js-plotly-plot .plotly .modebar {background-color: #ffffffee !important; border: 1px solid #ddd; border-radius: 6px;}
.js-plotly-plot .plotly .modebar button:hover svg path {fill: #8e44ad !important;}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
# Navigation Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Go to",
    ["Profile", "Chat", "Symptoms", "Treatment", "Diseases", "Reports", "Settings"]
)

# Initialize Session State Variables
DEFAULT_SESSION_STATE = {
    "profile_complete": False,
    "profile_data": {},
    "messages": [],
    "health_data": {},
    "language": "en",
    "glucose_log": [],
    "bp_log": [],
    "asthma_log": [],
    "analytics_data": {
        "dates": [datetime.now().strftime("%Y-%m-%d")],
        "heart_rates": [72],
        "glucose_levels": [90],
        "blood_pressure_systolic": [120],
        "blood_pressure_diastolic": [80],
        "peak_flow": [400],
        "hba1c": [5.7]
    }
}

# Ensure all default keys exist in session state
for key, default_value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Reset Profile Function
def reset_profile():
    st.session_state.profile_complete = False
    st.session_state.profile_data = {}
    st.session_state.messages = []
    st.session_state.glucose_log = []
    st.session_state.bp_log = []
    st.session_state.asthma_log = []
    st.session_state.health_data = {}
    st.session_state.analytics_data = {"heart_rates": [72], "glucose_levels": [90], "dates": [datetime.now().strftime("%Y-%m-%d")]}

    
    st.rerun()


#Global

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









# Function to export data as PDF including user profile



def export_health_report(ai_summary=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Title with border and background
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 15, txt="Health Report Summary", ln=True, align='C', fill=True)
    pdf.ln(10)

    # --------------------------
    # Patient Profile Section
    # --------------------------
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "👤 Patient Profile", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(180, 180, 180)
    pdf.rect(x=10, y=pdf.get_y() - 5, w=190, h=40, style='D')
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    for k, v in st.session_state.profile_data.items():
        if v:  # Skip empty fields
            pdf.cell(0, 8, txt=f"• {k.capitalize()}: {v}", ln=True)
    pdf.ln(10)

    # --------------------------
    # Latest Metrics Section
    # --------------------------
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "📊 Latest Metrics", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.rect(x=10, y=pdf.get_y() - 5, w=190, h=50, style='D')
    pdf.ln(5)

    dates = st.session_state.analytics_data.get("dates", [])
    heart_rates = st.session_state.analytics_data.get("heart_rates", [])
    glucose_levels = st.session_state.analytics_data.get("glucose_levels", [])
    peak_flow = st.session_state.analytics_data.get("peak_flow", [])
    hba1c = st.session_state.analytics_data.get("hba1c", [])

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=f"• Date: {dates[-1] if len(dates) > 0 else 'N/A'}", ln=True)
    pdf.cell(0, 8, txt=f"• Heart Rate: {heart_rates[-1] if len(heart_rates) > 0 else 'N/A'} bpm", ln=True)
    pdf.cell(0, 8, txt=f"• Blood Glucose: {glucose_levels[-1] if len(glucose_levels) > 0 else 'N/A'} mg/dL", ln=True)
    pdf.cell(0, 8, txt=f"• Peak Flow: {peak_flow[-1] if len(peak_flow) > 0 else 'N/A'} L/min", ln=True)
    pdf.cell(0, 8, txt=f"• HbA1c: {hba1c[-1] if len(hba1c) > 0 else 'N/A'} %", ln=True)
    pdf.ln(10)

    # --------------------------
    # AI Summary Section (if available)
    # --------------------------
    if ai_summary:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "🧠 AI Report Summary", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.rect(x=10, y=pdf.get_y() - 5, w=190, h=60, style='D')  # Border around summary
        pdf.ln(5)

        pdf.set_font("Arial", size=12)
        for line in ai_summary.split('\n'):
            if line.strip():
                pdf.multi_cell(0, 8, txt=line.strip())
        pdf.ln(10)

    # --------------------------
    # Footer
    # --------------------------
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, txt="Generated by Health Analytics Dashboard © All rights reserved", align='C')

    return pdf.output(dest='S').encode('latin-1')




















# Pages
if page == "Profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧾 Complete Your Profile")
    
    # Profile Fields
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name", placeholder="Enter your full name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1, help="Your current age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        email = st.text_input("Email Address", placeholder="Enter your email address")
        phone = st.text_input("Phone Number", placeholder="Enter your phone number")
    
    with col2:
        height = st.number_input("Height (cm)", min_value=50, max_value=300, step=1, help="Your height in centimeters")
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300, step=1, help="Your weight in kilograms")
        allergies = st.text_area("Allergies", placeholder="List any allergies (e.g., peanuts, pollen)")
        medical_history = st.text_area("Medical History", placeholder="Briefly describe any significant medical conditions or surgeries")
    
    # Save Profile Button
    if st.button("Save Profile", key="save_profile"):
        if name.strip() == "" or age <= 0 or height <= 0 or weight <= 0:
            st.error("❌ Please fill in all required fields.")
        else:
            bmi = round(weight / ((height / 100) ** 2), 1)
            st.session_state.profile_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "email": email,
                "phone": phone,
                "height": height,
                "weight": weight,
                "bmi": bmi,
                "allergies": allergies,
                "medical_history": medical_history
            }
            st.session_state.profile_complete = True
            st.success("✅ Profile saved successfully!")
    
    # Reset Profile Button
    if st.button("🔄 Reset Profile", key="reset_profile"):
        reset_profile()
        st.info("ℹ️ Profile has been reset.")
    
    # Display Profile Summary if Completed
    if st.session_state.profile_complete:
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown("#### 📋 Profile Summary")
        profile_summary = f"""
        - **Name**: {st.session_state.profile_data.get('name', 'N/A')}
        - **Age**: {st.session_state.profile_data.get('age', 'N/A')}
        - **Gender**: {st.session_state.profile_data.get('gender', 'N/A')}
        - **Email**: {st.session_state.profile_data.get('email', 'N/A')}
        - **Phone**: {st.session_state.profile_data.get('phone', 'N/A')}
        - **Height**: {st.session_state.profile_data.get('height', 'N/A')} cm
        - **Weight**: {st.session_state.profile_data.get('weight', 'N/A')} kg
        - **BMI**: {st.session_state.profile_data.get('bmi', 'N/A')}
        - **Allergies**: {st.session_state.profile_data.get('allergies', 'N/A')}
        - **Medical History**: {st.session_state.profile_data.get('medical_history', 'N/A')}
        """
        st.markdown(profile_summary)
    
    st.markdown('</div>', unsafe_allow_html=True)

























elif page == "Chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🗨️ Chat Interface")
    
    # Section Header
    st.markdown("""
    <p style="font-size: 18px; color: #34495e;">
        Interact with our AI-powered health assistant for personalized advice and answers to your health queries.
    </p>
    """, unsafe_allow_html=True)
    
    # Display Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for role, message in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="user-bubble"><strong>You:</strong><br>{message}</div>', unsafe_allow_html=True)
        elif role == "assistant":
            st.markdown(f'<div class="bot-bubble"><strong>Assistant:</strong><br>{message}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # User Input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input("Ask your question here:", placeholder="Type your query...", key="user_input")
    col1, col2 = st.columns([1, 6])
    with col1:
        send_button = st.button("Send", key="send_message")
    with col2:
        clear_button = st.button("Clear Chat", key="clear_chat")
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle Send Button
    if send_button:
        if user_input.strip() == "":
            st.warning("Please enter a valid query.")
        else:
            # Add user message to chat history
            st.session_state.messages.append(("user", user_input))

            # Generate AI response
            try:
                llm = get_llm("chat")
                profile_info = json.dumps(st.session_state.profile_data) if st.session_state.profile_complete else "{}"
                chat_history = ''.join([f'{r.capitalize()}: {c}' for r, c in st.session_state.messages[-6:]])
                prompt = f"""
                You are a professional medical assistant AI helping a patient with their health queries.
                Use the following guidelines:
                - Be empathetic, informative, and clear.
                - Always mention that you're not a substitute for real medical advice.
                - If unsure, recommend consulting a physician.

                Patient Profile: {profile_info}
                Chat History: {chat_history}
                User Question: "{user_input}"

                Answer:
                """
                with st.spinner("🧠 Generating response..."):
                    response = llm.invoke(prompt).strip()
                if not response or "error" in response.lower():
                    response = "I'm unable to respond at this time due to technical issues. Please try again later."
                
                # Add assistant response to chat history
                st.session_state.messages.append(("assistant", response))
                st.rerun()
            except Exception as e:
                st.error(f"🚨 Error generating response: {str(e)}")

    # Handle Clear Chat Button
    if clear_button:
        st.session_state.messages = []
        st.success("Chat history cleared successfully!")

    # Export Chat History Button
    if st.session_state.messages:
        chat_log = "\n".join([f"{role.capitalize()}: {msg}" for role, msg in st.session_state.messages])
        st.download_button(
            label="Export Chat Log",
            data=chat_log,
            file_name="chat_log.txt",
            mime="text/plain"
        )

    st.markdown('</div>', unsafe_allow_html=True)

























elif page == "Symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Symptom Checker")
    
    # Section Header
    st.markdown("""
    <p style="font-size: 18px; color: #34495e;">
        Enter your symptoms, and our AI-powered assistant will analyze them to provide potential causes and recommendations.
    </p>
    """, unsafe_allow_html=True)
    
    # Step 1: Input Symptoms
    st.subheader("Step 1: Describe Your Symptoms")
    col1, col2 = st.columns(2)
    
    with col1:
        symptom_1 = st.text_input("Symptom 1", placeholder="e.g., Headache")
        symptom_2 = st.text_input("Symptom 2", placeholder="e.g., Fatigue")
        symptom_3 = st.text_input("Symptom 3", placeholder="e.g., Nausea")
    
    with col2:
        duration = st.selectbox("Duration", ["Less than 1 day", "1-3 days", "4-7 days", "More than 7 days"])
        severity = st.select_slider("Severity", options=["Mild", "Moderate", "Severe"], value="Moderate")
        location = st.text_input("Location of Symptoms", placeholder="e.g., Head, Abdomen")
    
    # Step 2: Additional Information
    st.subheader("Step 2: Provide Additional Details (Optional)")
    age_group = st.selectbox("Age Group", ["Child (0-12)", "Teen (13-19)", "Adult (20-64)", "Senior (65+)"])
    medical_conditions = st.multiselect(
        "Pre-existing Medical Conditions",
        ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "None"]
    )
    medications = st.text_area("Current Medications", placeholder="List any medications you are taking")
    
    # Analyze Button
    if st.button("🧠 Analyze Symptoms", key="analyze_symptoms"):
        # Validate Inputs
        symptoms = [symptom_1, symptom_2, symptom_3]
        valid_symptoms = [s.strip() for s in symptoms if s.strip()]
        
        if not valid_symptoms:
            st.error("❌ Please enter at least one symptom.")
        else:
            # Prepare Prompt for LLM
            try:
                llm = get_llm("symptoms")
                profile_info = json.dumps(st.session_state.profile_data) if st.session_state.profile_complete else "{}"
                prompt = f"""
                You are a professional medical assistant AI analyzing patient-reported symptoms.
                Use the following guidelines:
                - Be empathetic, informative, and clear.
                - Always mention that you're not a substitute for real medical advice.
                - If unsure, recommend consulting a physician.

                Patient Profile: {profile_info}
                Reported Symptoms: {', '.join(valid_symptoms)}
                Duration: {duration}
                Severity: {severity}
                Location: {location}
                Age Group: {age_group}
                Pre-existing Conditions: {', '.join(medical_conditions) if medical_conditions else 'None'}
                Current Medications: {medications}

                Provide a detailed analysis including:
                1. Possible causes or conditions based on symptoms.
                2. Recommended actions or precautions.
                3. When to consult a doctor.

                Output format:
                ### 🔍 Symptom Analysis
                - **Possible Causes**: [List possible causes]
                - **Recommendations**: [Provide actionable advice]
                - **When to See a Doctor**: [Specify urgency]

                Answer:
                """
                with st.spinner("🧠 Analyzing symptoms..."):
                    response = llm.invoke(prompt).strip()
                
                if not response or "error" in response.lower():
                    response = "I'm unable to analyze symptoms at this time due to technical issues. Please try again later."
                
                st.markdown("### 🧠 Symptom Analysis")
                st.markdown(response)
            except Exception as e:
                st.error(f"🚨 Error analyzing symptoms: {str(e)}")

    # Export Analysis Button
    if "symptom_analysis" in st.session_state and st.session_state.symptom_analysis:
        st.download_button(
            label="Export Analysis",
            data=st.session_state.symptom_analysis,
            file_name="symptom_analysis.txt",
            mime="text/plain"
        )

    st.markdown('</div>', unsafe_allow_html=True)








    

elif page == "Treatment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💊 Personalized Treatment Planner")
    
    # Section Header
    st.markdown("""
    <p style="font-size: 18px; color: #34495e;">
        Create a personalized, phase-wise treatment plan based on your condition and duration.
    </p>
    """, unsafe_allow_html=True)
    
    # Step 1: Input Condition and Duration
    st.subheader("Step 1: Describe Your Condition")
    col1, col2 = st.columns(2)
    
    with col1:
        condition = st.text_input("Condition or Diagnosis", placeholder="e.g., Diabetes, Hypertension")
        duration = st.selectbox("Duration", ["Acute (short-term)", "Chronic (long-term)"])
    
    with col2:
        severity = st.select_slider("Severity", options=["Mild", "Moderate", "Severe"], value="Moderate")
        age_group = st.selectbox("Age Group", ["Child (0-12)", "Teen (13-19)", "Adult (20-64)", "Senior (65+)"])
    
    # Step 2: Additional Information
    st.subheader("Step 2: Provide Additional Details (Optional)")
    medical_conditions = st.multiselect(
        "Pre-existing Medical Conditions",
        ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "None"]
    )
    medications = st.text_area("Current Medications", placeholder="List any medications you are taking")
    
    # Generate Treatment Plan Button
    if st.button("🧠 Generate Treatment Plan", key="generate_treatment"):
        # Validate Inputs
        if not condition.strip():
            st.error("❌ Please enter a valid condition.")
        else:
            # Prepare Prompt for LLM
            try:
                llm = get_llm("treatment")
                profile_name = st.session_state.profile_data.get("name", "Unknown")
                prompt = f"""
                You are a professional medical assistant AI creating a personalized, phase-wise treatment plan.
                Use the following guidelines:
                - Be empathetic, informative, and clear.
                - Always mention that you're not a substitute for real medical advice.
                - If unsure, recommend consulting a physician.

                Patient Name: {profile_name}
                Condition: {condition}
                Duration: {duration}
                Severity: {severity}
                Age Group: {age_group}
                Pre-existing Conditions: {', '.join(medical_conditions) if medical_conditions else 'None'}
                Current Medications: {medications}

                Provide a detailed, phase-wise treatment plan including:
                ### Phase 1: Immediate Actions
                - Medications (with dosages and frequency).
                - Lifestyle modifications.

                ### Phase 2: Short-Term Goals (1-2 weeks)
                - Follow-up care recommendations.
                - Monitoring parameters.

                ### Phase 3: Long-Term Management (Beyond 2 weeks)
                - Sustained lifestyle changes.
                - Potential complications to monitor.

                Output format:
                ### 🩺 Personalized Treatment Plan for {profile_name}
                #### Phase 1: Immediate Actions
                - [Provide actionable steps]

                #### Phase 2: Short-Term Goals
                - [Provide short-term goals]

                #### Phase 3: Long-Term Management
                - [Provide long-term strategies]

                Answer:
                """
                with st.spinner("🧠 Generating treatment plan..."):
                    response = llm.invoke(prompt).strip()
                
                if not response or "error" in response.lower():
                    response = "I'm unable to generate a treatment plan at this time due to technical issues. Please try again later."
                
                st.markdown(f"### 🩺 Personalized Treatment Plan for {profile_name}")
                st.markdown(response)
            except Exception as e:
                st.error(f"🚨 Error generating treatment plan: {str(e)}")

    # Export Treatment Plan Button
    if "treatment_plan" in st.session_state and st.session_state.treatment_plan:
        st.download_button(
            label="Export Treatment Plan",
            data=st.session_state.treatment_plan,
            file_name="treatment_plan.txt",
            mime="text/plain"
        )

    # Section: Log Daily Metrics
    st.subheader("Step 3: Log Daily Metrics (Optional)")
    metric_type = st.selectbox("Select Metric Type", ["Glucose Levels", "Blood Pressure", "Peak Flow", "HbA1c"])
    col1, col2 = st.columns(2)
    
    with col1:
        if metric_type == "Glucose Levels":
            glucose_value = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=300, step=1)
            glucose_date = st.date_input("Date", value=datetime.today())
        elif metric_type == "Blood Pressure":
            systolic = st.number_input("Systolic BP", min_value=90, max_value=200, step=1)
            diastolic = st.number_input("Diastolic BP", min_value=60, max_value=130, step=1)
            bp_date = st.date_input("Date", value=datetime.today())
        elif metric_type == "Peak Flow":
            peak_flow_value = st.number_input("Peak Flow (L/min)", min_value=100, max_value=800, step=1)
            peak_flow_date = st.date_input("Date", value=datetime.today())
        elif metric_type == "HbA1c":
            hba1c_value = st.number_input("HbA1c (%)", min_value=4.0, max_value=12.0, step=0.1)
            hba1c_date = st.date_input("Date", value=datetime.today())
    
    with col2:
        if st.button("✅ Log Metric"):
            if metric_type == "Glucose Levels":
                st.session_state.glucose_log.append({"value": glucose_value, "date": glucose_date.strftime("%Y-%m-%d")})
                st.success("Glucose level logged successfully!")
            elif metric_type == "Blood Pressure":
                st.session_state.bp_log.append({
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "date": bp_date.strftime("%Y-%m-%d")
                })
                st.success("Blood pressure logged successfully!")
            elif metric_type == "Peak Flow":
                st.session_state.asthma_log.append({
                    "peak_flow": peak_flow_value,
                    "date": peak_flow_date.strftime("%Y-%m-%d")
                })
                st.success("Peak flow logged successfully!")
            elif metric_type == "HbA1c":
                st.session_state.hba1c_log.append({
                    "hba1c": hba1c_value,
                    "date": hba1c_date.strftime("%Y-%m-%d")
                })
                st.success("HbA1c logged successfully!")

    # Section: Historical Data Visualization
    st.subheader("Step 4: Historical Data Visualization")
    visualization_type = st.selectbox("Select Metric to Visualize", ["Glucose Levels", "Blood Pressure", "Peak Flow", "HbA1c"])
    
    if visualization_type == "Glucose Levels" and st.session_state.glucose_log:
        df_gluc = pd.DataFrame(st.session_state.glucose_log)
        fig = px.line(df_gluc, x='date', y='value', title='Glucose Levels Over Time')
        fig.update_layout(yaxis_title="Glucose (mg/dL)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    elif visualization_type == "Blood Pressure" and st.session_state.bp_log:
        df_bp = pd.DataFrame(st.session_state.bp_log)
        fig = px.line(df_bp, x='date', y=['systolic', 'diastolic'], title='Blood Pressure Over Time')
        fig.update_layout(yaxis_title="Pressure (mmHg)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    elif visualization_type == "Peak Flow" and st.session_state.asthma_log:
        df_asthma = pd.DataFrame(st.session_state.asthma_log)
        fig = px.line(df_asthma, x='date', y='peak_flow', title='Peak Flow Over Time')
        fig.update_layout(yaxis_title="Peak Flow (L/min)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    elif visualization_type == "HbA1c" and st.session_state.hba1c_log:
        df_hba1c = pd.DataFrame(st.session_state.hba1c_log)
        fig = px.line(df_hba1c, x='date', y='hba1c', title='HbA1c Over Time')
        fig.update_layout(yaxis_title="HbA1c (%)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    # Section: Reset Logs
    st.subheader("Step 5: Reset Logged Metrics")
    if st.button("🔄 Reset All Logs", key="reset_logs"):
        st.session_state.glucose_log = []
        st.session_state.bp_log = []
        st.session_state.asthma_log = []
        st.session_state.hba1c_log = []
        st.success("All logs have been reset.")

    # Footer
    st.markdown('<footer>© Health Assistant 2023</footer>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)















elif page == "Diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🫀 Chronic Disease Management")
    
    # Section Header
    st.markdown("""
    <p style="font-size: 18px; color: #34495e;">
        Log and manage chronic conditions like diabetes, hypertension, and asthma. 
    </p>
    """, unsafe_allow_html=True)
    
    # Step 1: Select Condition
    st.subheader("Step 1: Select Your Condition")
    condition = st.selectbox(
        "Condition",
        ["Diabetes", "Hypertension", "Asthma"],
        help="Choose the condition you want to manage."
    )
    
    # Step 2: Log Episode Details
    st.subheader("Step 2: Log Episode Details")
    if condition == "Diabetes":
        glucose_level = st.number_input("Glucose Level (mg/dL)", min_value=50, max_value=400, step=1)
        insulin_dose = st.number_input("Insulin Dose (units)", min_value=0, max_value=100, step=1)
        episode_date = st.date_input("Date of Episode", value=datetime.today())
        
        if st.button("✅ Log Diabetes Episode"):
            st.session_state.glucose_log.append({
                "glucose_level": glucose_level,
                "insulin_dose": insulin_dose,
                "date": episode_date.strftime("%Y-%m-%d")
            })
            st.success(f"✅ Logged: Glucose {glucose_level} mg/dL, Insulin {insulin_dose} units on {episode_date.strftime('%Y-%m-%d')}")
            
            # Generate AI Health Advice
            prompt = f"""
            My glucose level is {glucose_level} mg/dL. I took {insulin_dose} units of insulin.
            What does this mean? How should I adjust my insulin or diet?
            Patient Profile: {json.dumps(st.session_state.profile_data)}
            """
            try:
                llm = get_llm("diseases")
                advice = llm.invoke(prompt).strip()
                st.markdown(f"🧠 **AI Health Advice:** {advice}")
            except Exception as e:
                st.error(f"🚨 Error generating health advice: {str(e)}")

    elif condition == "Hypertension":
        systolic = st.number_input("Systolic BP", min_value=90, max_value=200, step=1)
        diastolic = st.number_input("Diastolic BP", min_value=60, max_value=130, step=1)
        episode_date = st.date_input("Date of Episode", value=datetime.today())
        
        if st.button("✅ Log Hypertension Episode"):
            st.session_state.bp_log.append({
                "systolic": systolic,
                "diastolic": diastolic,
                "date": episode_date.strftime("%Y-%m-%d")
            })
            st.success(f"✅ Logged: {systolic}/{diastolic} mmHg on {episode_date.strftime('%Y-%m-%d')}")
            
            # Generate AI Health Advice
            prompt = f"""
            My blood pressure is {systolic}/{diastolic} mmHg. What does that mean?
            Patient Profile: {json.dumps(st.session_state.profile_data)}
            """
            try:
                llm = get_llm("diseases")
                advice = llm.invoke(prompt).strip()
                st.markdown(f"🧠 **AI Health Advice:** {advice}")
            except Exception as e:
                st.error(f"🚨 Error generating health advice: {str(e)}")

    elif condition == "Asthma":
        triggers = st.text_area("Triggers Today (e.g., pollen, dust, exercise)")
        severity = st.slider("Severity (1-10)", 1, 10, key="severity_slider")
        peak_flow = st.number_input("Peak Flow (L/min)", min_value=100, max_value=800, step=1)
        episode_date = st.date_input("Date of Episode", value=datetime.today())
        
        if st.button("✅ Log Asthma Episode"):
            st.session_state.asthma_log.append({
                "triggers": triggers,
                "severity": severity,
                "peak_flow": peak_flow,
                "date": episode_date.strftime("%Y-%m-%d")
            })
            st.success(f"✅ Episode logged on {episode_date.strftime('%Y-%m-%d')}")
            
            # Generate AI Health Advice
            prompt = f"""
            What are some ways to avoid asthma triggers like '{triggers}'?
            How can I manage severity level {severity} episodes?
            Patient Profile: {json.dumps(st.session_state.profile_data)}
            """
            try:
                llm = get_llm("diseases")
                advice = llm.invoke(prompt).strip()
                st.markdown(f"🧠 **AI Health Advice:** {advice}")
            except Exception as e:
                st.error(f"🚨 Error generating health advice: {str(e)}")

    # Step 3: Historical Data Visualization
    st.subheader("Step 3: Historical Data Visualization")
    visualization_type = st.selectbox("Select Metric to Visualize", ["Glucose Levels", "Blood Pressure", "Peak Flow"])
    
    if visualization_type == "Glucose Levels" and st.session_state.glucose_log:
        df_gluc = pd.DataFrame(st.session_state.glucose_log)
        fig = px.line(df_gluc, x='date', y='glucose_level', title='Glucose Levels Over Time')
        fig.update_layout(yaxis_title="Glucose (mg/dL)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    elif visualization_type == "Blood Pressure" and st.session_state.bp_log:
        df_bp = pd.DataFrame(st.session_state.bp_log)
        fig = px.line(df_bp, x='date', y=['systolic', 'diastolic'], title='Blood Pressure Over Time')
        fig.update_layout(yaxis_title="Pressure (mmHg)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
    
    elif visualization_type == "Peak Flow" and st.session_state.asthma_log:
        df_asthma = pd.DataFrame(st.session_state.asthma_log)
        fig = px.line(df_asthma, x='date', y='peak_flow', title='Peak Flow Over Time')
        fig.update_layout(yaxis_title="Peak Flow (L/min)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)

    # Step 4: Reset Logs
    st.subheader("Step 4: Reset Logged Episodes")
    if st.button("🔄 Reset All Logs", key="reset_logs"):
        st.session_state.glucose_log = []
        st.session_state.bp_log = []
        st.session_state.asthma_log = []
        st.success("All logs have been reset.")

    # Export Logs Button
    if st.session_state.glucose_log or st.session_state.bp_log or st.session_state.asthma_log:
        logs_data = ""
        if st.session_state.glucose_log:
            logs_data += "Glucose Logs:\n" + "\n".join([
                f"{log['date']}: {log['glucose_level']} mg/dL, Insulin {log['insulin_dose']} units"
                for log in st.session_state.glucose_log
            ]) + "\n\n"
        if st.session_state.bp_log:
            logs_data += "Blood Pressure Logs:\n" + "\n".join([
                f"{log['date']}: {log['systolic']}/{log['diastolic']} mmHg"
                for log in st.session_state.bp_log
            ]) + "\n\n"
        if st.session_state.asthma_log:
            logs_data += "Asthma Logs:\n" + "\n".join([
                f"{log['date']}: Triggers - {log['triggers']}, Severity - {log['severity']}, Peak Flow - {log['peak_flow']} L/min"
                for log in st.session_state.asthma_log
            ])
        
        st.download_button(
            label="Export Logs",
            data=logs_data,
            file_name="disease_logs.txt",
            mime="text/plain"
        )

    st.markdown('</div>', unsafe_allow_html=True)









elif page == "Reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Ultimate Health Analytics Dashboard")
    # Section Header
    st.markdown("""
    <p style="font-size: 18px; color: #34495e;">
        Analyze your health metrics, generate detailed reports, and visualize trends.
    </p>
    """, unsafe_allow_html=True)

    # Initialize session state analytics data if not exists
    if "analytics_data" not in st.session_state:
        st.session_state.analytics_data = {
            "dates": [datetime.now().strftime("%Y-%m-%d")],
            "heart_rates": [72],
            "glucose_levels": [90],
            "blood_pressure_systolic": [120],
            "blood_pressure_diastolic": [80],
            "peak_flow": [400],
            "hba1c": [5.7],
            "symptoms": ["Headache", "Fatigue", "Nausea"],
            "symptom_frequency": [3, 2, 1],  # Example symptom frequencies
        }

    # Ensure all lists in analytics_data are the same length
    def pad_or_truncate_lists(data_dict):
        """Ensure all lists in the dictionary are of the same length."""
        max_length = max(len(lst) for lst in data_dict.values())
        for key in data_dict:
            current_length = len(data_dict[key])
            if current_length < max_length:
                # Pad with None if the list is shorter
                data_dict[key].extend([None] * (max_length - current_length))
            elif current_length > max_length:
                # Truncate if the list is longer
                data_dict[key] = data_dict[key][:max_length]
        return data_dict

    # Apply padding/truncation to analytics_data
    st.session_state.analytics_data = pad_or_truncate_lists(st.session_state.analytics_data)

    # Step 1: Log New Metrics
    st.subheader("Step 1: Log New Health Metrics")
    col1, col2 = st.columns(2)
    with col1:
        metric_type = st.selectbox(
            "Select Metric Type",
            ["Heart Rate", "Blood Glucose", "Blood Pressure", "Peak Flow", "HbA1c"]
        )
        if metric_type == "Heart Rate":
            value = st.number_input("Heart Rate (bpm)", min_value=40, max_value=140, step=1)
        elif metric_type == "Blood Glucose":
            value = st.number_input("Blood Glucose (mg/dL)", min_value=50, max_value=300, step=1)
        elif metric_type == "Blood Pressure":
            systolic = st.number_input("Systolic BP (mmHg)", min_value=90, max_value=200, step=1)
            diastolic = st.number_input("Diastolic BP (mmHg)", min_value=60, max_value=130, step=1)
        elif metric_type == "Peak Flow":
            value = st.number_input("Peak Flow (L/min)", min_value=100, max_value=800, step=1)
        elif metric_type == "HbA1c":
            value = st.number_input("HbA1c (%)", min_value=4.0, max_value=12.0, step=0.1)

    with col2:
        log_date = st.date_input("Log Date", value=datetime.today())
        if st.button("✅ Log Metric"):
            if metric_type == "Heart Rate":
                st.session_state.analytics_data["heart_rates"].append(value)
                st.session_state.analytics_data["dates"].append(log_date.strftime("%Y-%m-%d"))
                st.success(f"Logged Heart Rate: {value} bpm on {log_date.strftime('%Y-%m-%d')}")
            elif metric_type == "Blood Glucose":
                st.session_state.analytics_data["glucose_levels"].append(value)
                st.session_state.analytics_data["dates"].append(log_date.strftime("%Y-%m-%d"))
                st.success(f"Logged Blood Glucose: {value} mg/dL on {log_date.strftime('%Y-%m-%d')}")
            elif metric_type == "Blood Pressure":
                st.session_state.analytics_data["blood_pressure_systolic"].append(systolic)
                st.session_state.analytics_data["blood_pressure_diastolic"].append(diastolic)
                st.session_state.analytics_data["dates"].append(log_date.strftime("%Y-%m-%d"))
                st.success(f"Logged Blood Pressure: {systolic}/{diastolic} mmHg on {log_date.strftime('%Y-%m-%d')}")
            elif metric_type == "Peak Flow":
                st.session_state.analytics_data["peak_flow"].append(value)
                st.session_state.analytics_data["dates"].append(log_date.strftime("%Y-%m-%d"))
                st.success(f"Logged Peak Flow: {value} L/min on {log_date.strftime('%Y-%m-%d')}")
            elif metric_type == "HbA1c":
                st.session_state.analytics_data["hba1c"].append(value)
                st.session_state.analytics_data["dates"].append(log_date.strftime("%Y-%m-%d"))
                st.success(f"Logged HbA1c: {value}% on {log_date.strftime('%Y-%m-%d')}")

    # Step 2: Display Latest Metrics
    st.subheader("### 📋 Latest Metrics")
    dates = st.session_state.analytics_data.get("dates", [])
    heart_rates = st.session_state.analytics_data.get("heart_rates", [])
    glucose_levels = st.session_state.analytics_data.get("glucose_levels", [])
    peak_flow = st.session_state.analytics_data.get("peak_flow", [])
    hba1c = st.session_state.analytics_data.get("hba1c", [])

    latest_date = dates[-1] if len(dates) > 0 else "N/A"
    latest_hr = heart_rates[-1] if len(heart_rates) > 0 and isinstance(heart_rates[-1], (int, float)) else "N/A"
    latest_glucose = glucose_levels[-1] if len(glucose_levels) > 0 and isinstance(glucose_levels[-1], (int, float)) else "N/A"
    latest_peak = peak_flow[-1] if len(peak_flow) > 0 and isinstance(peak_flow[-1], (int, float)) else "N/A"
    latest_hba1c = hba1c[-1] if len(hba1c) > 0 and isinstance(hba1c[-1], (int, float)) else "N/A"

    st.markdown(f"""
    <div class="metric-card">
        <strong>Date:</strong> {latest_date}<br>
        <strong>Heart Rate:</strong> {latest_hr} bpm<br>
        <strong>Blood Glucose:</strong> {latest_glucose} mg/dL<br>
        <strong>Peak Flow:</strong> {latest_peak} L/min<br>
        <strong>HbA1c:</strong> {latest_hba1c} %
    </div>
    """, unsafe_allow_html=True)

    # Step 3: Trend Analysis
    st.subheader("### 📈 Trend Analysis")
    hr_trend = (
        "↑"
        if len(heart_rates) > 1
        and isinstance(heart_rates[-1], (int, float))
        and isinstance(heart_rates[-2], (int, float))
        and heart_rates[-1] > heart_rates[-2]
        else "↓"
        if len(heart_rates) > 1
        and isinstance(heart_rates[-1], (int, float))
        and isinstance(heart_rates[-2], (int, float))
        and heart_rates[-1] < heart_rates[-2]
        else "-"
    )
    glucose_trend = (
        "↑"
        if len(glucose_levels) > 1
        and isinstance(glucose_levels[-1], (int, float))
        and isinstance(glucose_levels[-2], (int, float))
        and glucose_levels[-1] > glucose_levels[-2]
        else "↓"
        if len(glucose_levels) > 1
        and isinstance(glucose_levels[-1], (int, float))
        and isinstance(glucose_levels[-2], (int, float))
        and glucose_levels[-1] < glucose_levels[-2]
        else "-"
    )
    peak_trend = (
        "↑"
        if len(peak_flow) > 1
        and isinstance(peak_flow[-1], (int, float))
        and isinstance(peak_flow[-2], (int, float))
        and peak_flow[-1] > peak_flow[-2]
        else "↓"
        if len(peak_flow) > 1
        and isinstance(peak_flow[-1], (int, float))
        and isinstance(peak_flow[-2], (int, float))
        and peak_flow[-1] < peak_flow[-2]
        else "-"
    )
    hba1c_trend = (
        "↑"
        if len(hba1c) > 1
        and isinstance(hba1c[-1], (int, float))
        and isinstance(hba1c[-2], (int, float))
        and hba1c[-1] > hba1c[-2]
        else "↓"
        if len(hba1c) > 1
        and isinstance(hba1c[-1], (int, float))
        and isinstance(hba1c[-2], (int, float))
        and hba1c[-1] < hba1c[-2]
        else "-"
    )

    st.markdown(f"""
    <div class="metric-card">
        <strong>Heart Rate Trend:</strong> {hr_trend}<br>
        <strong>Glucose Trend:</strong> {glucose_trend}<br>
        <strong>Peak Flow Trend:</strong> {peak_trend}<br>
        <strong>HbA1c Trend:</strong> {hba1c_trend}
    </div>
    """, unsafe_allow_html=True)

    # Step 4: Generate AI-Driven Health Summary
    st.subheader("Step 4: Generate AI-Driven Health Summary")
    if st.button("🧠 Generate AI Report Summary"):
        try:
            profile_info = json.dumps(st.session_state.profile_data) if st.session_state.profile_complete else "{}"
            recent_hr = ', '.join(map(str, [x for x in heart_rates[-7:] if isinstance(x, (int, float))]))
            recent_glucose = ', '.join(map(str, [x for x in glucose_levels[-7:] if isinstance(x, (int, float))]))
            recent_peak = ', '.join(map(str, [x for x in peak_flow[-7:] if isinstance(x, (int, float))]))
            recent_hba1c = ', '.join(map(str, [x for x in hba1c[-7:] if isinstance(x, (int, float))]))

            prompt = f"""
            You are a professional healthcare AI assistant tasked with providing a personalized health summary.
            Patient Profile: {profile_info}
            Recent Metrics:
            - Heart Rate (bpm): [{recent_hr}]
            - Blood Glucose (mg/dL): [{recent_glucose}]
            - Peak Flow (L/min): [{recent_peak}]
            - HbA1c (%): [{recent_hba1c}]
            Instructions:
            1. Analyze trends over time and note if values are increasing, decreasing, or stable.
            2. Interpret what these trends may mean in terms of health implications.
            3. Provide simple, easy-to-understand explanations without medical jargon.
            4. Suggest practical lifestyle changes (e.g., diet, exercise).
            5. Mention when a medical checkup is recommended.
            Output format:
            ### 🔍 Trend Overview
            - Heart Rate: [Stable/Increasing/Decreasing]
            - Blood Glucose: [Stable/Increasing/Decreasing]
            - Peak Flow: [Stable/Increasing/Decreasing]
            - HbA1c: [Stable/Increasing/Decreasing]
            ### 🩺 Health Implications
            Explain what the trend might indicate about the patient's current condition.
            ### 💡 Recommendations
            Provide 2-3 lifestyle suggestions tailored to the patient's data.
            ### ⚠️ Important Notes
            Include any warnings or reminders about consulting a doctor.
            """
            llm = get_llm("reports")
            with st.spinner("🧠 Generating AI-driven health summary..."):
                response = llm.invoke(prompt).strip()
            if not response or "error" in response.lower():
                response = "I'm unable to generate a health summary at this time due to technical issues. Please try again later."
            st.markdown("### 🧠 AI Health Analysis")
            st.markdown(response)
            ai_summary = response
        except Exception as e:
            st.error(f"🚨 Error generating AI summary: {str(e)}")

    # Step 5: Visualize Historical Data with Enhanced Features
    st.subheader("Step 5: Visualize Historical Data")
    visualization_type = st.selectbox(
        "Select Metric to Visualize",
        [
            "Heart Rate Trend",
            "Blood Pressure Dual-Line",
            "Blood Glucose Trend with Reference Line",
            "Symptom Frequency Pie Chart",
        ]
    )

    # Heart Rate Trend Line Chart
    if visualization_type == "Heart Rate Trend":
        heart_rates = st.session_state.analytics_data.get("heart_rates", [])
        dates = st.session_state.analytics_data.get("dates", [])
        df_hr = pd.DataFrame({"Date": dates, "Heart Rate (bpm)": heart_rates})
        fig_hr = px.line(
            df_hr,
            x="Date",
            y="Heart Rate (bpm)",
            title="Heart Rate Trend Over Time",
            labels={"Heart Rate (bpm)": "Heart Rate (bpm)"},
        )
        fig_hr.update_traces(mode="lines+markers", hovertemplate="Date: %{x}<br>Heart Rate: %{y} bpm")
        fig_hr.add_hline(
            y=100,  # Example normal range upper limit
            line_dash="dash",
            line_color="red",
            annotation_text="Normal Range Limit",
            annotation_position="top right",
        )
        st.plotly_chart(fig_hr, use_container_width=True)

    # Blood Pressure Dual-Line Chart
    elif visualization_type == "Blood Pressure Dual-Line":
        bp_systolic = st.session_state.analytics_data.get("blood_pressure_systolic", [])
        bp_diastolic = st.session_state.analytics_data.get("blood_pressure_diastolic", [])
        dates = st.session_state.analytics_data.get("dates", [])
        df_bp = pd.DataFrame(
            {"Date": dates, "Systolic BP (mmHg)": bp_systolic, "Diastolic BP (mmHg)": bp_diastolic}
        )
        fig_bp = px.line(
            df_bp,
            x="Date",
            y=["Systolic BP (mmHg)", "Diastolic BP (mmHg)"],
            title="Blood Pressure Trends Over Time",
            labels={"value": "Pressure (mmHg)"},
        )
        fig_bp.update_traces(mode="lines+markers", hovertemplate="Date: %{x}<br>Pressure: %{y} mmHg")
        fig_bp.add_hrect(
            y0=120,
            y1=140,
            line_width=0,
            fillcolor="red",
            opacity=0.2,
            annotation_text="Normal Systolic Range",
        )
        fig_bp.add_hrect(
            y0=80,
            y1=90,
            line_width=0,
            fillcolor="blue",
            opacity=0.2,
            annotation_text="Normal Diastolic Range",
        )
        st.plotly_chart(fig_bp, use_container_width=True)

    # Blood Glucose Trend Line Chart with Reference Line
    elif visualization_type == "Blood Glucose Trend with Reference Line":
        glucose_levels = st.session_state.analytics_data.get("glucose_levels", [])
        dates = st.session_state.analytics_data.get("dates", [])
        df_gluc = pd.DataFrame({"Date": dates, "Blood Glucose (mg/dL)": glucose_levels})
        fig_gluc = px.line(
            df_gluc,
            x="Date",
            y="Blood Glucose (mg/dL)",
            title="Blood Glucose Trend Over Time",
            labels={"Blood Glucose (mg/dL)": "Blood Glucose (mg/dL)"},
        )
        fig_gluc.update_traces(mode="lines+markers", hovertemplate="Date: %{x}<br>Glucose: %{y} mg/dL")
        fig_gluc.add_hline(
            y=140,  # Example reference line for normal glucose level
            line_dash="dash",
            line_color="green",
            annotation_text="Normal Glucose Limit",
            annotation_position="top right",
        )
        st.plotly_chart(fig_gluc, use_container_width=True)

    # Symptom Frequency Pie Chart
    elif visualization_type == "Symptom Frequency Pie Chart":
        symptoms = st.session_state.analytics_data.get("symptoms", [])
        symptom_frequency = st.session_state.analytics_data.get("symptom_frequency", [])
        df_symptoms = pd.DataFrame({"Symptom": symptoms, "Frequency": symptom_frequency})
        fig_pie = px.pie(
            df_symptoms,
            names="Symptom",
            values="Frequency",
            title="Symptom Frequency Distribution",
            hole=0.3,  # Donut chart style
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="Symptom: %{label}<br>Frequency: %{value}",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Metrics Summary Section
    st.subheader("Metrics Summary")
    heart_rates = st.session_state.analytics_data.get("heart_rates", [])
    glucose_levels = st.session_state.analytics_data.get("glucose_levels", [])
    bp_systolic = st.session_state.analytics_data.get("blood_pressure_systolic", [])
    bp_diastolic = st.session_state.analytics_data.get("blood_pressure_diastolic", [])

    # Helper function to determine metric status
    def get_metric_status(value, low, high):
        """Return color and status based on value range."""
        if low <= value <= high:
            return "✅ Normal", "green"
        else:
            return "⚠️ Abnormal", "red"

    hr_status, hr_color = get_metric_status(heart_rates[-1], 60, 100) if heart_rates else ("-", "gray")
    glucose_status, glucose_color = get_metric_status(glucose_levels[-1], 70, 140) if glucose_levels else ("-", "gray")
    bp_status, bp_color = get_metric_status(bp_systolic[-1], 90, 120) if bp_systolic else ("-", "gray")

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="background-color: {hr_color}; padding: 10px; border-radius: 5px; text-align: center;">
                <strong>Heart Rate</strong><br>
                Value: {heart_rates[-1] if heart_rates else 'N/A'} bpm<br>
                Trend: {hr_trend}<br>
                Status: {hr_status}
            </div>
            <div style="background-color: {glucose_color}; padding: 10px; border-radius: 5px; text-align: center;">
                <strong>Blood Glucose</strong><br>
                Value: {glucose_levels[-1] if glucose_levels else 'N/A'} mg/dL<br>
                Trend: {glucose_trend}<br>
                Status: {glucose_status}
            </div>
            <div style="background-color: {bp_color}; padding: 10px; border-radius: 5px; text-align: center;">
                <strong>Blood Pressure</strong><br>
                Value: {bp_systolic[-1]}/{bp_diastolic[-1] if bp_diastolic else 'N/A'} mmHg<br>
                Trend: {hr_trend}<br>
                Status: {bp_status}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Step 6: Export Report
    st.subheader("Step 6: Export Report")
    if st.session_state.profile_complete:
        # Export PDF
        pdf_data = export_health_report(ai_summary=ai_summary)
        st.download_button(
            label="📄 Export Report as PDF",
            data=pdf_data,
            file_name="health_report.pdf",
            mime="application/pdf"
        )
        # Export CSV
        csv_data = ""
        metrics_df = pd.DataFrame({
            "Date": dates,
            "Heart Rate (bpm)": heart_rates,
            "Blood Glucose (mg/dL)": glucose_levels,
            "Systolic BP (mmHg)": st.session_state.analytics_data.get("blood_pressure_systolic", []),
            "Diastolic BP (mmHg)": st.session_state.analytics_data.get("blood_pressure_diastolic", []),
            "Peak Flow (L/min)": peak_flow,
            "HbA1c (%)": hba1c
        })
        csv_data = metrics_df.to_csv(index=False)
        st.download_button(
            label="💾 Export Metrics as CSV",
            data=csv_data,
            file_name="health_metrics.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Complete your profile to enable report export.")

    # Footer
    lang = st.session_state.language
    st.markdown(f'<p style="text-align:center; font-size:14px;">{LANGUAGES[lang]["footer"]}</p>', unsafe_allow_html=True)

    # Debug Mode
    with st.expander("🔧 Debug Mode"):
        st.write("Session State:", st.session_state)
    st.markdown('</div>', unsafe_allow_html=True)
 



    # Footer
    lang = st.session_state.language
    st.markdown(f'<p style="text-align:center; font-size:14px;">{LANGUAGES[lang]["footer"]}</p>', unsafe_allow_html=True)

    # Debug Mode
    with st.expander("🔧 Debug Mode"):
        st.write("Session State:", st.session_state)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<footer>© Health Assistant 2023</footer>', unsafe_allow_html=True)
