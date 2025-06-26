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
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Profile", "Chat", "Symptoms", "Treatment", "Diseases", "Reports", "Settings"])

# Initialize session state variables
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}
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
    st.session_state.analytics_data = {"heart_rates": [72], "glucose_levels": [90], "dates": [datetime.now().strftime("%Y-%m-%d")]}

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

# Pages
if page == "Profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧾 User Profile")
    # Existing profile logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🗨️ Chat Interface")
    # Existing chat logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Symptom Checker")
    # Existing symptom checker logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Treatment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💊 Treatment Planner")
    # Existing treatment planner logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🫀 Chronic Disease Management")
    # Existing chronic disease management logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Reports & Analytics")
    # Existing reports logic here
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")
    # Existing settings logic here
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<footer>© Health Assistant 2023</footer>', unsafe_allow_html=True)
