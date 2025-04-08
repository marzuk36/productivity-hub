from firebase_config import db
import streamlit as st
from datetime import datetime
import uuid

def get_user_chat_ref():
    return db.collection("users").document(st.session_state["localId"]).collection("chats")

def create_thread():
    thread_id = str(uuid.uuid4())
    chat_ref = get_user_chat_ref().document(thread_id)
    chat_ref.set({"created_at": datetime.utcnow(), "title": "New Chat"})
    return thread_id

def get_threads():
    return [(doc.id, doc.to_dict().get("title", "Untitled")) for doc in get_user_chat_ref().stream()]

def get_messages(thread_id):
    return list(get_user_chat_ref().document(thread_id).collection("messages").order_by("timestamp").stream())

def save_message(thread_id, role, content):
    get_user_chat_ref().document(thread_id).collection("messages").add({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })

def rename_thread(thread_id, new_title):
    get_user_chat_ref().document(thread_id).update({"title": new_title})

def delete_thread(thread_id):
    thread_ref = get_user_chat_ref().document(thread_id)
    messages = thread_ref.collection("messages").stream()
    for msg in messages:
        msg.reference.delete()
    thread_ref.delete()