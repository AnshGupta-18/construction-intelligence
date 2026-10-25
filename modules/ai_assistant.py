
import streamlit as st
from groq import Groq


def render_ai_assistant():
    st.subheader("🤖 AI Construction Assistant")

    st.write(
        "Ask questions about construction materials, project planning, "
        "site inspections, and general construction safety."
    )

    # Initialize chat history
    if "construction_chat" not in st.session_state:
        st.session_state.construction_chat = []

    # Display previous messages
    for message in st.session_state.construction_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept a new question
    prompt = st.chat_input(
        "Ask a construction-related question...",
        key="construction_question"
    )

    if prompt:
        st.session_state.construction_chat.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Read API key from Streamlit secrets
            api_key = st.secrets.get("GROQ_API_KEY")

            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY is missing from .streamlit/secrets.toml"
                )

            client = Groq(api_key=api_key)

            system_message = {
                "role": "system",
                "content": (
                    "You are an AI construction knowledge assistant. "
                    "Answer questions about construction materials, "
                    "project planning, building methods, and general "
                    "site safety clearly and accurately. "
                    "Do not claim to certify structural safety. "
                    "For critical structural decisions, recommend "
                    "consulting a qualified construction professional."
                )
            }

            messages = [
                system_message,
                *st.session_state.construction_chat
            ]

            with st.chat_message("assistant"):
                with st.spinner("Generating AI response..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1000
                    )

                    answer = response.choices[0].message.content

                    if not answer:
                        answer = "The AI model returned an empty response."

                st.markdown(answer)

            st.session_state.construction_chat.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as error:
            st.error("Groq API request failed.")
            st.code(f"{type(error).__name__}: {error}")

    # Clear conversation history
    if st.button("Clear Chat", key="clear_construction_chat"):
        st.session_state.construction_chat = []
        st.rerun()
