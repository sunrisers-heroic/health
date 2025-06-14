import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

# Page config
st.set_page_config(page_title="🩺 Health AI Assistant", layout="centered", page_icon="🩺")

# Custom CSS for chat bubbles with a health-themed color palette
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
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🩺 Health AI Assistant")
st.markdown("Ask anything about health, wellness, medical advice, or general biology!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load Watsonx credentials from Streamlit secrets
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

# Display chat messages
for message in st.session_state.messages:
    if isinstance(message, tuple):
        role, content = message
        if role == "user":
            st.markdown(f'<div class="user-bubble"><b>You:</b> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-bubble"><b>Bot:</b> {content}</div>', unsafe_allow_html=True)
    else:
        if message.type == "human":
            st.markdown(f'<div class="user-bubble"><b>You:</b> {message.content}</div>', unsafe_allow_html=True)
        elif message.type == "ai":
            st.markdown(f'<div class="bot-bubble"><b>Bot:</b> {message.content}</div>', unsafe_allow_html=True)

# Chat input form
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Your question:", placeholder="Type something like 'What are the symptoms of diabetes?'...")
    submit_button = st.form_submit_button(label="Send")

# Handle submission
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
