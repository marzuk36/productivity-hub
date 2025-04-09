import streamlit as st
from chat_firestore_utils import (
    create_thread, get_threads, get_messages,
    save_message, delete_thread, rename_thread
)
from llm_connector import stream_deepseek_response
import json

def chat_interface():
    st.title("🤖Fazio")

    # Chat mode selector
    mode = st.radio("Chat mode", ["🧠 With History", "⚡ Quick Chat (no save)"], horizontal=True)

    # With History Mode
    if mode == "🧠 With History":
        st.sidebar.subheader("💬 Chat Threads")
        threads = get_threads()
        thread_map = {t[1]: t[0] for t in threads}
        selected_title = st.sidebar.selectbox("Choose a thread", list(thread_map.keys()) if threads else [])

        if st.sidebar.button("➕ New Chat"):
            create_thread()
            st.rerun()

        if selected_title:
            thread_id = thread_map[selected_title]

            with st.sidebar.expander("📝 Rename This Thread"):
                new_title = st.text_input("New name", selected_title, label_visibility="collapsed", key="rename_input")
                if new_title and new_title != selected_title:
                    rename_thread(thread_id, new_title)
                    st.rerun()

            if st.sidebar.button("🗑️ Delete This Thread"):
                delete_thread(thread_id)
                st.rerun()

            st.markdown(f"### 🧠 Chat: {selected_title}")

            messages = get_messages(thread_id)
            for m in messages:
                role = m.to_dict()["role"]
                content = m.to_dict()["content"]
                with st.chat_message(role):
                    st.markdown(content, unsafe_allow_html=True)

            prompt = st.chat_input("Type your message...")
            if prompt:
                st.chat_message("user").markdown(prompt)
                save_message(thread_id, "user", prompt)

                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    full_response = ""
                    deepseek_messages = [{"role": m.to_dict()["role"], "content": m.to_dict()["content"]} for m in messages]
                    deepseek_messages.append({"role": "user", "content": prompt})

                    for chunk in stream_deepseek_response(deepseek_messages):
                        if chunk:
                            if chunk.decode("utf-8").strip() == "data: [DONE]":
                                break
                            try:
                                json_data = json.loads(chunk.decode("utf-8").replace("data: ", ""))
                                delta = json_data["choices"][0]["delta"].get("content", "")
                                full_response += delta
                                placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                            except Exception:
                                continue

                    placeholder.markdown(full_response, unsafe_allow_html=True)
                    save_message(thread_id, "assistant", full_response)

        else:
            st.info("Create or select a chat thread.")

    # Quick Chat Mode (no saving)
    elif mode == "⚡ Quick Chat (no save)":
        st.markdown("### ⚡ Quick Chat (ephemeral)")

        chat_history = st.session_state.get("quick_chat", [])
        for role, content in chat_history:
            with st.chat_message(role):
                st.markdown(content, unsafe_allow_html=True)

        prompt = st.chat_input("Say something...")
        if prompt:
            st.chat_message("user").markdown(prompt)
            st.session_state.quick_chat = chat_history + [("user", prompt)]

            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                message_payload = [{"role": "user", "content": prompt}]

                for chunk in stream_deepseek_response(message_payload):
                    if chunk:
                        if chunk.decode("utf-8").strip() == "data: [DONE]":
                            break
                        try:
                            json_data = json.loads(chunk.decode("utf-8").replace("data: ", ""))
                            delta = json_data["choices"][0]["delta"].get("content", "")
                            full_response += delta
                            placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                        except Exception:
                            continue

                placeholder.markdown(full_response, unsafe_allow_html=True)
                st.session_state.quick_chat.append(("assistant", full_response))
