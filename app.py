import streamlit as st
from auth import login, is_logged_in, refresh_id_token
from ui.sidebar import folder_sidebar
from ui.editor import show_editor

st.set_page_config(page_title="Clipboard App", layout="wide")

if not is_logged_in() and not st.session_state.get("logged_out", False):
    if refresh_id_token():
        st.rerun()

if not is_logged_in():
    st.title("🔐 Login to Clipboard App")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(email, password):
            st.session_state["logged_out"] = False  # Reset logout flag
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["📋 Clipboard", "🤖 Chat"])

if st.sidebar.button("🚪 Log Out"):
    for key in ["idToken", "refreshToken", "user_email", "localId"]:
        st.session_state.pop(key, None)
    st.session_state["logged_out"] = True  # <-- prevent auto-login
    st.rerun()

if page == "📋 Clipboard":
    folder, selected_note, is_code = folder_sidebar()
    if folder and selected_note is not None:
        show_editor(folder, selected_note, is_code)
elif page == "🤖 Chat":
    from ui.chat_page import chat_interface
    chat_interface()
