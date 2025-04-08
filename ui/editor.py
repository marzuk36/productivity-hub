import streamlit as st
from streamlit_ace import st_ace
from firestore_utils import get_content, save_content
from datetime import datetime

def show_editor(folder, name, is_code):
    st.markdown(f"### 📝 Editing: `{name}`")
    st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    current_content = get_content(folder, name, is_code)

    if is_code:
        updated_content = st_ace(value=current_content, language="python", theme="monokai", key=f"ace_{folder}_{name}")
    else:
        updated_content = st.text_area("✏️ Write your note below...", value=current_content, height=300)

    if st.button("💾 Sync"):
        save_content(folder, name, updated_content, is_code)
        st.success("Saved!")
