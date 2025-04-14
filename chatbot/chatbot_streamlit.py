import streamlit as st
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Add the parent directory to sys.path to import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import the logic functions
from chatbot.chatbot_logic import create_chat_graph

# Load environment variables
load_dotenv(dotenv_path=".env")

# Configure page
st.set_page_config(
    page_title="Mental Models Chatbot",
    page_icon="🧠",
    layout="wide"
)

# Apply custom CSS for better UI
st.markdown("""
            <style>
                .main {
                    padding: 2rem;
                }
                .stChatMessage {
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                }
                .message-container {
                    margin-bottom: 1.5rem;
                }
                .mental-model-card {
                    background-color: #f0f2f6;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid #4b5eba;
                }
                .mental-model-title {
                    font-weight: bold;
                    margin-bottom: 0.5rem;
                }
            </style>
""", unsafe_allow_html=True)

# Set up title and description
st.title("🧠 Mental Models Chatbot")
st.markdown("Ask questions and get answers based on mental models")

# Initialize the chat graph
graph = create_chat_graph()

# Initialize memory state
memory_state = {"memory": []}

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "retrieved_models" not in st.session_state:
    st.session_state.retrieved_models = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about mental models..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Start the response generation process with a spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Run the graph
            state = {"user_input": prompt, **memory_state}
            result = graph.invoke(state)
            
            # Update memory for next run
            memory_state = {"memory": result["memory"]}
            
            # Store the retrieved models for display
            st.session_state.retrieved_models = result.get("retrieved_models", [])
            
            # Display the assistant's response
            st.markdown(result["assistant_response"])
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": result["assistant_response"]})


# Display the retrieved mental models in a sidebar
with st.sidebar:
    st.header("📚 Mental Models Used")
    
    if st.session_state.retrieved_models:
        for model in st.session_state.retrieved_models:
            with st.expander(f"**{model['title']}** (Score: {model['similarity']:.2f})"):
                st.markdown(f"**Description:** {model['body']}")
                if model.get('source'):
                    st.markdown(f"**Source:** {model['source']}")
    else:
        st.info("No mental models retrieved yet. Ask a question to see relevant mental models.")
        
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This chatbot provides answers based on a collection of mental models.
    
    It uses:
    - Streamlit for the interface
    - Langraph for memory and chat logic
    - Supabase vector store for semantic search
    """)

if __name__ == "__main__":
    # This is used when running the file directly
    pass
