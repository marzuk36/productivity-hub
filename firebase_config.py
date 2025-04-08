import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

firebase_json = json.loads(st.secrets["FIREBASE_CONFIG_JSON"])
cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)
db = firestore.client()
