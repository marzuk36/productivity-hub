import requests
import json
import streamlit as st

API_KEY = st.secrets["DEEPSEEK_API_KEY"]
API_URL = "https://api.deepseek.com/v1/chat/completions"

def stream_deepseek_response(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "stream": True
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload), stream=True)
    return response.iter_lines()
