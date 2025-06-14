import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Page config
st.set_page_config(page_title="🩺 Health AI Assistant", layout="centered", page_icon="🩺")

# Custom CSS for chat bubbles and layout
st.markdown("""
    <style>
        body {
            background-color: #f9fcff;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .user-bubble {
            background-color: #d6eaff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 70%;
            align-self: flex-end;
            word-wrap: break-word;
        }
        .bot-bubble {
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 70%;
            align-self: flex-start;
            word-wrap: break-word;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .section-title {
            color: #007acc;
            font-size: 1.2em;
            margin-top: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🩺 Menu")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧑‍⚕️ Doctor Mode", "🧍 Patient Mode", "🤖 AI Chatbot"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

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
    st.warning("⚠️ Watsonx credentials missing. Please set them in Streamlit Cloud or .streamlit/secrets.toml.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Error initializing LLM: {str(e)}")
    st.stop()

# ------------------------------ HOME PAGE ------------------------------
if page == "🏠 Home":
    st.title("Welcome to 🩺 Health AI Assistant")
    st.markdown("""
        This application offers a wide range of healthcare tools including:
        
        - 🔍 AI-powered medical Q&A  
        - 👨‍⚕️ Doctor mode for managing patients  
        - 🧍 Self-assessment for patients  
        - 💡 General health advice  

        Choose an option from the sidebar to begin!
    """)

# ------------------------------ DOCTOR MODE ------------------------------
elif page == "🧑‍⚕️ Doctor Mode":
    st.title("🧑‍⚕️ Doctor Dashboard")
    
    st.markdown("#### Add New Patient")
    patient_name = st.text_input("Patient Name")
    patient_age = st.number_input("Age", min_value=0, max_value=120)
    condition = st.text_area("Diagnosis / Notes")
    if st.button("Save Patient"):
        st.success(f"✅ Saved {patient_name}, Age: {patient_age}, Condition: {condition}")

    st.markdown("---")
    st.markdown("#### View Patients")
    if "patients" not in st.session_state:
        st.session_state.patients = []
    
    if st.session_state.patients:
        for idx, p in enumerate(st.session_state.patients):
            st.write(f"{idx+1}. **{p['name']}**, Age: {p['age']}, Diagnosis: {p['condition']}")
    else:
        st.info("No patients added yet.")

# ------------------------------ PATIENT MODE ------------------------------
elif page == "🧍 Patient Mode":
    st.title("🧍 Patient Tools")
    
    st.markdown("### Symptom Checker")
    symptom_input = st.text_area("Describe your symptoms:")
    if st.button("Check Symptoms"):
        if symptom_input.strip():
            with st.spinner("Analyzing..."):
                response = llm.invoke(f"Based on these symptoms, what could be the possible conditions? {symptom_input}")
                st.markdown(f"🔍 Possible Conditions: \n\n{response}")
        else:
            st.warning("Please describe your symptoms first.")

    st.markdown("---")
    st.markdown("### Health Tips")
    if st.button("Get Daily Tip"):
        tip = llm.invoke("Give one general health tip for today.")
        st.markdown(f"💡 Today's Tip: {tip}")

# ------------------------------ AI CHATBOT ------------------------------
elif page == "🤖 AI Chatbot":
    st.title("🤖 Health AI Assistant")
    st.markdown("Ask anything about health, wellness, biology, or medicine!")

    # Display chat history
    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="user-bubble"><b>You:</b> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble"><b>Bot:</b> {content}</div>', unsafe_allow_html=True)

    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your question:", placeholder="Type something like 'What are the symptoms of diabetes?'...")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))
        with st.spinner("Thinking..."):
            try:
                response = llm.invoke(user_input)
                st.session_state.messages.append(("assistant", response))
                st.rerun()
            except Exception as e:
                st.session_state.messages.append(("assistant", f"Error: {str(e)}"))
                st.rerun()
