import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="centered", page_icon="🩺")

# Custom CSS - Classic Medical UI
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
        .header {
            background: linear-gradient(to right, #007acc, #00aaff);
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .navbar {
            display: flex;
            justify-content: center;
            background-color: #007acc;
            padding: 10px 0;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .nav-button {
            background: none;
            border: none;
            color: white;
            font-size: 16px;
            margin: 0 15px;
            cursor: pointer;
        }
        .card {
            background-color: #f9fcff;
            padding: 15px 20px;
            border-left: 5px solid #007acc;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        .bubble-user {
            background-color: #d6eaff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 70%;
            align-self: flex-end;
        }
        .bubble-bot {
            background-color: #e6f0ff;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 70%;
            align-self: flex-start;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header"><h1>🩺 MyHospital - Health Assistant</h1><p>Your virtual health companion</p></div>', unsafe_allow_html=True)

# Navigation Bar
def render_navbar():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🏠 Home", key="btn_home"):
            st.session_state.page = "Home"
    with col2:
        if st.button("🔐 Login", key="btn_login"):
            st.session_state.page = "Login"
    with col3:
        if st.button("📝 Register", key="btn_register"):
            st.session_state.page = "Register"
    with col4:
        if st.button("🧑‍⚕️ Dashboard", key="btn_dashboard"):
            st.session_state.page = "Dashboard"
    with col5:
        if st.button("🤖 Chatbot", key="btn_chatbot"):
            st.session_state.page = "Chatbot"

render_navbar()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "admin123", "role": "Admin"},
        "doctor": {"password": "doc123", "role": "Doctor"},
        "patient": {"password": "pat123", "role": "Patient"},
    }

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

# ------------------------------ HOME PAGE ------------------------------
def show_home():
    st.markdown('<h2>Welcome to MyHospital</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:16px;">We're here to help you stay healthy, informed, and empowered. Whether you're a doctor, patient, or admin, this assistant will guide you through health-related queries, symptom checks, and more.</p>
    
    <div class="card">
        <h4>💡 About This Tool</h4>
        <ul>
            <li>AI-powered medical Q&A</li>
            <li>Sign up & log in as Admin, Doctor, or Patient</li>
            <li>Get instant health advice</li>
        </ul>
    </div>
    """)

# ------------------------------ LOGIN PAGE ------------------------------
def show_login():
    st.markdown('<h3>🔐 Login</h3>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Admin", "Doctor", "Patient"])

    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username]["password"] == password and st.session_state.users[username]["role"] == role:
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.session_state.page = "Dashboard"
        else:
            st.error("Invalid credentials or role mismatch.")

# ------------------------------ REGISTER PAGE ------------------------------
def show_register():
    st.markdown('<h3>📝 Sign Up</h3>', unsafe_allow_html=True)
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.selectbox("Select Role", ["Admin", "Doctor", "Patient"])

    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not new_username or not new_password:
            st.error("Please fill all fields.")
        elif new_username in st.session_state.users:
            st.warning("Username already taken.")
        else:
            st.session_state.users[new_username] = {"password": new_password, "role": role}
            st.success("Registration successful! You can now log in.")
            st.session_state.page = "Login"

# ------------------------------ DASHBOARD ------------------------------
def show_dashboard():
    st.markdown(f'<h3>👋 Welcome, {st.session_state.role}!</h3>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.session_state.role == "Admin":
        st.write("You're logged in as an **Admin**. Manage users, data, and settings here.")
    elif st.session_state.role == "Doctor":
        st.write("You're logged in as a **Doctor**. View patient records and provide advice.")
    elif st.session_state.role == "Patient":
        st.write("You're logged in as a **Patient**. Use tools to check symptoms or get health tips.")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------ CHATBOT ------------------------------
def show_chatbot():
    st.markdown('<h3>🤖 Health AI Assistant</h3>', unsafe_allow_html=True)
    st.markdown("Ask anything about health, wellness, biology, or medicine!")

    for role, content in st.session_state.messages:
        if role == "user":
            st.markdown(f'<div class="bubble-user"><b>You:</b> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-bot"><b>Bot:</b> {content}</div>', unsafe_allow_html=True)

    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your question:", placeholder="Type something like 'What are the symptoms of diabetes?'...")
        submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))
        with st.spinner("Thinking..."):
            try:
                response = llm.invoke(user_input)
                st.session_state.messages.append(("assistant", response))
                st.experimental_rerun()
            except Exception as e:
                st.session_state.messages.append(("assistant", f"Error: {str(e)}"))
                st.experimental_rerun()

# ------------------------------ MAIN APP LOGIC ------------------------------
page = st.session_state.page
if page == "Home":
    show_home()
elif page == "Login":
    show_login()
elif page == "Register":
    show_register()
elif page == "Dashboard":
    if st.session_state.role:
        show_dashboard()
    else:
        st.warning("🔒 Please log in first.")
        st.session_state.page = "Login"
elif page == "Chatbot":
    if st.session_state.role:
        show_chatbot()
    else:
        st.warning("🔒 Please log in first.")
        st.session_state.page = "Login"
