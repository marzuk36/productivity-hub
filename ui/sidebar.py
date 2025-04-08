import streamlit as st
from firestore_utils import (
    get_folders, get_notes, get_codes, create_folder,
    save_content, get_user_folder_ref
)

def folder_sidebar():
    st.sidebar.markdown("### 📁 Folders")

    folders = get_folders()
    selected_folder = st.session_state.get("selected_folder")

    for folder in folders:
        cols = st.sidebar.columns([0.7, 0.15, 0.15])
        if cols[0].button(folder, key=f"folder-{folder}"):
            st.session_state["selected_folder"] = folder
            st.session_state["selected_note"] = None
            st.session_state["selected_code"] = None
            st.rerun()

        if cols[1].button("✏️", key=f"rename-folder-{folder}"):
            st.session_state["renaming_folder"] = folder

        if cols[2].button("🗑️", key=f"delete-folder-{folder}"):
            ref = get_user_folder_ref(folder)
            for sub in ["notes", "code_snippets"]:
                for doc in ref.collection(sub).stream():
                    doc.reference.delete()
            ref.delete()
            if st.session_state.get("selected_folder") == folder:
                st.session_state["selected_folder"] = None
            st.rerun()

        if st.session_state.get("renaming_folder") == folder:
            new_name = st.text_input("New folder name", folder, key=f"folder-rename-input-{folder}")
            if st.button("✅ Confirm Rename", key=f"confirm-rename-folder-{folder}"):
                old_ref = get_user_folder_ref(folder)
                data = old_ref.get().to_dict()
                notes = old_ref.collection("notes").stream()
                codes = old_ref.collection("code_snippets").stream()
                new_ref = get_user_folder_ref(new_name)
                new_ref.set(data or {})
                for note in notes:
                    new_ref.collection("notes").document(note.id).set(note.to_dict())
                    note.reference.delete()
                for code in codes:
                    new_ref.collection("code_snippets").document(code.id).set(code.to_dict())
                    code.reference.delete()
                old_ref.delete()
                st.session_state["selected_folder"] = new_name
                del st.session_state["renaming_folder"]
                st.rerun()

    with st.sidebar.expander("➕ New Folder"):
        new_folder = st.text_input("Folder name", key="new-folder-name")
        if st.button("Create", key="create-folder-btn"):
            if new_folder and new_folder not in folders:
                create_folder(new_folder)
                st.session_state["selected_folder"] = new_folder
                st.rerun()

    folder = st.session_state.get("selected_folder")
    selected_note = st.session_state.get("selected_note")
    selected_code = st.session_state.get("selected_code")

    if folder:
        st.sidebar.markdown("### 📝 Notes")
        notes = get_notes(folder)
        for note in notes:
            note_id = note.id
            cols = st.sidebar.columns([0.7, 0.15, 0.15])
            if cols[0].button(note_id, key=f"note-{note_id}"):
                st.session_state["selected_note"] = note_id
                st.session_state["selected_code"] = None
                st.rerun()

            if cols[1].button("✏️", key=f"rename-note-{note_id}"):
                st.session_state["renaming_note"] = note_id

            if cols[2].button("🗑️", key=f"delete-note-{note_id}"):
                get_user_folder_ref(folder).collection("notes").document(note_id).delete()
                if selected_note == note_id:
                    st.session_state["selected_note"] = None
                st.rerun()

            if st.session_state.get("renaming_note") == note_id:
                new_id = st.text_input("Rename note", note_id, key=f"input-rename-note-{note_id}")
                if st.button("✅ Rename", key=f"confirm-rename-note-{note_id}"):
                    content = note.to_dict().get("content", "")
                    ref = get_user_folder_ref(folder)
                    ref.collection("notes").document(new_id).set({"content": content})
                    ref.collection("notes").document(note_id).delete()
                    st.session_state["selected_note"] = new_id
                    del st.session_state["renaming_note"]
                    st.rerun()

        if st.sidebar.button("➕ New Note"):
            import uuid
            new_id = f"Note-{uuid.uuid4().hex[:6]}"
            save_content(folder, new_id, "", is_code=False)
            st.session_state["selected_note"] = new_id
            st.rerun()

        st.sidebar.markdown("### 💻 Code Snippets")
        codes = get_codes(folder)
        for code in codes:
            code_id = code.id
            cols = st.sidebar.columns([0.7, 0.15, 0.15])
            if cols[0].button(code_id, key=f"code-{code_id}"):
                st.session_state["selected_code"] = code_id
                st.session_state["selected_note"] = None
                st.rerun()

            if cols[1].button("✏️", key=f"rename-code-{code_id}"):
                st.session_state["renaming_code"] = code_id

            if cols[2].button("🗑️", key=f"delete-code-{code_id}"):
                get_user_folder_ref(folder).collection("code_snippets").document(code_id).delete()
                if selected_code == code_id:
                    st.session_state["selected_code"] = None
                st.rerun()

            if st.session_state.get("renaming_code") == code_id:
                new_id = st.text_input("Rename code", code_id, key=f"input-rename-code-{code_id}")
                if st.button("✅ Rename", key=f"confirm-rename-code-{code_id}"):
                    content = code.to_dict().get("content", "")
                    ref = get_user_folder_ref(folder)
                    ref.collection("code_snippets").document(new_id).set({"content": content})
                    ref.collection("code_snippets").document(code_id).delete()
                    st.session_state["selected_code"] = new_id
                    del st.session_state["renaming_code"]
                    st.rerun()

        if st.sidebar.button("➕ New Code"):
            import uuid
            new_id = f"Code-{uuid.uuid4().hex[:6]}"
            save_content(folder, new_id, "", is_code=True)
            st.session_state["selected_code"] = new_id
            st.rerun()

    if selected_note:
        return folder, selected_note, False
    elif selected_code:
        return folder, selected_code, True
    else:
        return None, None, False
