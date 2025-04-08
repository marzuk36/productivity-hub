import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

try:
    firebase_json = json.loads(st.secrets["FIREBASE_CONFIG_JSON"])
    cred = credentials.Certificate(firebase_json)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error("🔥 Firebase initialization failed!")
    st.code(str(e))
