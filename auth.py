import streamlit as st
import requests
from streamlit_js_eval import streamlit_js_eval

API_KEY = st.secrets["FIREBASE_API_KEY"]
COOKIE_KEY = "refresh_token"

FIREBASE_SIGNIN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
FIREBASE_TOKEN_REFRESH = f"https://securetoken.googleapis.com/v1/token?key={API_KEY}"

def get_local_refresh_token():
    return streamlit_js_eval(js_expressions="localStorage.getItem('refresh_token')", key="get_refresh_token")

def set_local_refresh_token(token):
    streamlit_js_eval(js_expressions=f"localStorage.setItem('refresh_token', '{token}')", key="set_refresh_token")

def login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    res = requests.post(FIREBASE_SIGNIN, json=payload)
    if res.status_code == 200:
        data = res.json()
        persist_login(data)
        return True
    return False

def persist_login(data):
    st.session_state['idToken'] = data['idToken']
    st.session_state['refreshToken'] = data['refreshToken']
    st.session_state['user_email'] = data['email']
    st.session_state['localId'] = data['localId']
    set_local_refresh_token(data['refreshToken'])

def refresh_id_token():
    refresh_token = st.session_state.get("refreshToken") or get_local_refresh_token()
    if not refresh_token:
        return False

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    res = requests.post(FIREBASE_TOKEN_REFRESH, data=payload)
    if res.status_code == 200:
        data = res.json()
        st.session_state['idToken'] = data['id_token']
        st.session_state['refreshToken'] = data['refresh_token']
        st.session_state['user_email'] = data.get('user_id', '')
        st.session_state['localId'] = data.get('user_id', '')
        set_local_refresh_token(data['refresh_token'])
        return True
    return False

def is_logged_in():
    return 'idToken' in st.session_state and 'refreshToken' in st.session_state
