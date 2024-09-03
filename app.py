import streamlit as st
import requests

# Initialize the session state to keep chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("LangChain Interaction")

# Create a placeholder for the chat history above the input
chat_placeholder = st.empty()

# Display chat history
with chat_placeholder.container():
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)

# User input at the bottom
user_input = st.text_input("User:", "", key="input")

# Send button
if st.button("Send"):
    if user_input:
        with st.spinner("Processing..."):
            try:
                # Send user input to the LangChain API
                response = requests.post(
                    "http://127.0.0.1:8000/interact/",
                    json={"messages": [user_input]},
                )
                response.raise_for_status()  # Raise an error for bad responses
                response_data = response.json()
                
                # Update chat history
                if "response" in response_data:
                    st.session_state.chat_history.append(("user", user_input))
                    for message in response_data["response"]:
                        st.session_state.chat_history.append(("assistant", message))
                else:
                    st.error("Unexpected response format.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error in processing your request: {e}")
    else:
        st.warning("Please enter some text.")

    # Re-display chat history after new input is processed
    chat_placeholder.empty()
    with chat_placeholder.container():
        for role, message in st.session_state.chat_history:
            with st.chat_message(role):
                st.write(message)

