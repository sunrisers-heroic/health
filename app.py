import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from datetime import datetime
from fpdf import FPDF

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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_section" not in st.session_state:
    st.session_state.current_section = "chat"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "health_data" not in st.session_state:
    st.session_state.health_data = {}
if "language" not in st.session_state:
    st.session_state.language = "en"

# Load Watsonx credentials
try:
    credentials = {
        "url": st.secrets["WATSONX_URL"],
        "apikey": st.secrets["WATSONX_APIKEY"]
    }
    project_id = st.secrets["WATSONX_PROJECT_ID"]

    model_map = {
        "chat": "ibm/granite-13b-instruct-latest",
        "symptoms": "ibm/granite-13b-instruct-latest",
        "treatment": "ibm/granite-13b-instruct-latest",
        "diseases": "ibm/granite-13b-instruct-latest",
        "reports": "ibm/granite-13b-instruct-latest"
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

# Navigation Bar
lang = st.session_state.language
st.markdown('<div class="navbar">', unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    if st.button("챗", key="btn_chat"): st.session_state.current_section = "chat"
with col2:
    if st.button("🧠", key="btn_symptoms"): st.session_state.current_section = "symptoms"
with col3:
    if st.button("💊", key="btn_treatment"): st.session_state.current_section = "treatment"
with col4:
    if st.button("🫀", key="btn_diseases"): st.session_state.current_section = "diseases"
with col5:
    if st.button("📊", key="btn_reports"): st.session_state.current_section = "reports"
with col6:
    if st.button("🧾", key="btn_profile"): st.session_state.current_section = "profile"
with col7:
    if st.button("⚙️", key="btn_settings"): st.session_state.current_section = "settings"
st.markdown('</div>', unsafe_allow_html=True)

# Header
st.markdown(f'<h1 style="text-align:center;">{LANGUAGES[lang]["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; font-size:16px;">{LANGUAGES[lang]["subtitle"]}</p>', unsafe_allow_html=True)

# Function to export data as PDF
def export_health_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Health Report", ln=True, align='C')
    pdf.ln(10)
    for key, value in st.session_state.health_data.items():
        pdf.cell(0, 10, txt=f"{key.capitalize()}: {value}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# ------------------------------ SETTINGS ------------------------------
if st.session_state.current_section == "settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h2>⚙️ {LANGUAGES[lang]["settings"]}</h2>', unsafe_allow_html=True)
    language = st.selectbox("Language", options=["en", "es", "fr"], format_func=lambda x: {"en": "English", "es": "Español", "fr": "Français"}[x])
    theme = st.selectbox("Theme", ["Light"])
    font_size = st.slider("Font Size", 12, 24)
    if st.button(LANGUAGES[lang]["save_profile"]):
        st.session_state.language = language
        st.success("Preferences updated!")
    st.markdown('</div>')

# ------------------------------ PROGRESS REPORTS ------------------------------
elif st.session_state.current_section == "reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h2>📈 {LANGUAGES[lang]["reports"]}</h2>', unsafe_allow_html=True)
    heart_rate = st.slider("Heart Rate", 40, 200, step=1)
    glucose = st.slider("Blood Glucose Level", 40, 400, step=5)
    systolic = st.slider("Systolic BP", 90, 200, value=120)
    diastolic = st.slider("Diastolic BP", 60, 130, value=80)
    steps = st.slider("Steps Walked", 0, 50000, step=1000)
    sleep = st.slider("Hours Slept", 0.0, 12.0, step=0.5)
    
    if st.button("Save Data"):
        st.session_state.health_data.update({
            "heart_rate": heart_rate,
            "glucose": glucose,
            "systolic": systolic,
            "diastolic": diastolic,
            "steps_walked": steps,
            "hours_slept": sleep
        })
        st.success("Data saved successfully.")

    if st.button(LANGUAGES[lang]["generate_ai_report"]):
        summary = get_llm("reports").invoke(f"Give a short health analysis based on: {st.session_state.health_data}")
        st.markdown(f"🧠 **AI Analysis:**\n{summary}")

    if st.session_state.health_data:
        st.download_button(LANGUAGES[lang]["export_pdf"], data=export_health_report(), file_name="health_report.pdf", mime="application/pdf")

    st.markdown('</div>')

# ------------------------------ CHATBOT ------------------------------
elif st.session_state.current_section == "chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🤖 AI Chatbot</h2>', unsafe_allow_html=True)

    # Display chat messages
    for role, content in st.session_state.messages:
        bubble_class = "user-bubble" if role == "user" else "bot-bubble"
        st.markdown(f'<div class="{bubble_class}"><b>{role.capitalize()}:</b> {content}</div>', unsafe_allow_html=True)

    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your question:", placeholder="Type something like 'What are my symptoms?'...")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))
        with st.spinner("Thinking..."):
            try:
                llm = get_llm("chat")
                response = llm.invoke(user_input)
                st.session_state.messages.append(("assistant", response))
                st.rerun()
            except Exception as e:
                st.session_state.messages.append(("assistant", f"Error: {str(e)}"))
                st.rerun()

    st.markdown('</div>')

# ------------------------------ SYMPTOM CHECKER ------------------------------
elif st.session_state.current_section == "symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧠 Symptom Checker</h2>', unsafe_allow_html=True)
    query = st.text_area("Describe your symptoms or ask a question:")
    if st.button("Get Advice"):
        llm = get_llm("symptoms")
        res = llm.invoke(query)
        st.markdown(f"🧠 **AI Response:**\n{res}")
    st.markdown('</div>')

# ------------------------------ TREATMENT PLANNER ------------------------------
elif st.session_state.current_section == "treatment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>💊 Treatment Suggestions</h2>', unsafe_allow_html=True)
    treatment_query = st.text_input("Ask about conditions, medications, or lifestyle changes:")
    if st.button("Generate Ideas"):
        llm = get_llm("treatment")
        res = llm.invoke(treatment_query)
        st.markdown(f"💡 **Suggestions:**\n{res}")
    st.markdown('</div>')

# ------------------------------ DISEASE MANAGEMENT ------------------------------
elif st.session_state.current_section == "diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🫀 Chronic Disease Logs</h2>', unsafe_allow_html=True)
    condition = st.selectbox("Condition", ["Diabetes", "Hypertension", "Asthma"])
    if condition == "Diabetes":
        glucose = st.number_input("Blood Sugar Level (mg/dL)", 40, 400, step=5)
        if st.button("Log Glucose"):
            st.session_state.glucose_log = st.session_state.get("glucose_log", []) + [glucose]
            st.success(f"Logged: {glucose} mg/dL")
            prompt = f"My blood sugar is {glucose}. Is it normal? What should I do?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n{advice}")
    elif condition == "Hypertension":
        systolic = st.number_input("Systolic BP", 90, 200, value=120)
        diastolic = st.number_input("Diastolic BP", 60, 130, value=80)
        if st.button("Log BP"):
            st.session_state.bp_log = st.session_state.get("bp_log", []) + [(systolic, diastolic)]
            st.success(f"Logged: {systolic}/{diastolic} mmHg")
            prompt = f"My blood pressure is {systolic}/{diastolic} mmHg. What does that mean?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n{advice}")
    elif condition == "Asthma":
        severity = st.slider("Severity (1-10)", 1, 10)
        triggers = st.text_area("Triggers Today (e.g., pollen, dust)")
        if st.button("Log Episode"):
            st.session_state.asthma_log = st.session_state.get("asthma_log", []) + [{"triggers": triggers, "severity": severity}]
            st.success("Episode logged.")
            prompt = f"What are some ways to avoid asthma triggers like {triggers}?"
            try:
                advice = get_llm("diseases").invoke(prompt)
            except:
                advice = "AI is currently unavailable."
            st.markdown(f"🤖 **AI Advice:**\n{advice}")
    st.markdown('</div>')

# ------------------------------ USER PROFILE ------------------------------
elif st.session_state.current_section == "profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧾 User Profile</h2>', unsafe_allow_html=True)
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
    if st.button("Save Profile"):
        st.session_state.profile = {"name": name, "age": age, "gender": gender, "height": height, "weight": weight}
        st.success("Profile saved!")
    st.markdown('</div>')

# Footer
st.markdown(f'<p style="text-align:center; font-size:14px;">{LANGUAGES[lang]["footer"]}</p>', unsafe_allow_html=True)
