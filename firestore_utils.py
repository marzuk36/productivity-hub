from firebase_config import db
import streamlit as st

def get_user_folder_ref(folder_name):
    user_id = st.session_state['localId']
    return db.collection("users").document(user_id).collection("folders").document(folder_name)

def get_folders():
    user_id = st.session_state['localId']
    folders_ref = db.collection("users").document(user_id).collection("folders")
    return [doc.id for doc in folders_ref.stream()]

def get_notes(folder_name):
    return get_user_folder_ref(folder_name).collection("notes").stream()

def get_codes(folder_name):
    return get_user_folder_ref(folder_name).collection("code_snippets").stream()

def get_content(folder, name, is_code):
    col = "code_snippets" if is_code else "notes"
    doc = get_user_folder_ref(folder).collection(col).document(name).get()
    return doc.to_dict().get("content", "") if doc.exists else ""

def save_content(folder, name, content, is_code):
    col = "code_snippets" if is_code else "notes"
    get_user_folder_ref(folder).collection(col).document(name).set({"content": content})

def create_folder(folder_name):
    get_user_folder_ref(folder_name).set({})