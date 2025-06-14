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
        .navbar {
            display: flex;
            justify-content: space-around;
            background-color: #007acc;
            padding: 10px 0;
        }
        .navbar button {
            background: none;
            border: none;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .navbar button:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None
if "tab" not in st.session_state:
    st.session_state.tab = "Home"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Top Navigation Bar
def render_navbar():
    cols = st.columns([1,1,1,1])
    with cols[0]:
        if st.button("🏠 Home"):
            st.session_state.tab = "Home"
    with cols[1]:
        if st.button("🔐 Login"):
            st.session_state.tab = "Login"
    with cols[2]:
        if st.button("📊 Dashboard"):
            st.session_state.tab = "Dashboard"
    with cols[3]:
        if st.button("🤖 Chatbot"):
            st.session_state.tab = "Chatbot"

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

# Dummy users (for demo only — should be replaced with secure DB in production)
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "doctor": {"password": "doc123", "role": "Doctor"},
    "patient": {"password": "pat123", "role": "Patient"},
}

# ------------------------------ LOGIN PAGE ------------------------------
def show_login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Admin", "Doctor", "Patient"])

    if st.button("Login"):
        if username in users and users[username]["password"] == password and users[username]["role"] == role:
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.session_state.tab = "Dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials or role mismatch.")

# ------------------------------ DASHBOARD ------------------------------
def show_dashboard():
    st.title(f"👋 Welcome, {st.session_state.role}!")
    if st.session_state.role == "Admin":
        st.write("You're logged in as an **Admin**. Manage users, data, and settings here.")
    elif st.session_state.role == "Doctor":
        st.write("You're logged in as a **Doctor**. View patient records and provide advice.")
    elif st.session_state.role == "Patient":
        st.write("You're logged in as a **Patient**. Use tools to check symptoms or get health tips.")

# ------------------------------ CHATBOT ------------------------------
def show_chatbot():
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

# ------------------------------ HOME PAGE ------------------------------
def show_home():
    st.title("Welcome to 🩺 Health AI Assistant")
    st.markdown("""
        This application offers a wide range of healthcare tools including:
        
        - 🔍 AI-powered medical Q&A  
        - 👨‍⚕️ Doctor mode for managing patients  
        - 🧍 Self-assessment for patients  
        - 💡 General health advice  

        Choose an option from the top menu to begin!
    """)

# ------------------------------ MAIN APP LOGIC ------------------------------
render_navbar()

if st.session_state.tab == "Home":
    show_home()
elif st.session_state.tab == "Login":
    show_login()
elif st.session_state.tab == "Dashboard":
    if st.session_state.role:
        show_dashboard()
    else:
        st.warning("🔒 Please log in first.")
        show_login()
elif st.session_state.tab == "Chatbot":
    if st.session_state.role:
        show_chatbot()
    else:
        st.warning("🔒 Please log in first.")
        show_login()
