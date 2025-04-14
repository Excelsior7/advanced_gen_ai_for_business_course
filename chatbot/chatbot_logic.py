import os
import sys
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import END, Graph, StateGraph
from dotenv import load_dotenv
import streamlit as st

# Add the parent directory to sys.path to import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_store_creation.supabase.supabase_client import supabase

# Load environment variables
load_dotenv(dotenv_path=".env")

def query_mental_models(query_text: str, match_threshold: float = 0., match_count: int = 3) -> List[Dict]:
    """
    Query the Supabase vector store for mental models relevant to the query.
    Returns a list of relevant mental models.
    """
    # Create embeddings for the query using OpenAI
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    query_embedding = embeddings.embed_query(query_text)
    
    # Query Supabase for relevant mental models
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count
        }
    ).execute()
    
    return response.data

# Set up Langraph for chatbot logic
def create_chat_graph():
    """Create a graph with memory for the chatbot using Langraph."""
    
    llm = ChatOpenAI(
        model_name="gpt-4-turbo",
        temperature=0.5,
        api_key=st.secrets["OPENAI_API_KEY"],
    )
    
    # Define the state schema
    class ChatState(Dict):
        """State for the chat graph."""
        user_input: str
        context: Optional[str] = None
        memory: List[Dict] = []
        assistant_response: Optional[str] = None
        retrieved_models: Optional[List[Dict]] = None
    
    # Define the nodes
    def retriever(state: ChatState) -> ChatState:
        """Retrieve relevant mental models based on the user query."""
        query = state["user_input"]
        mental_models = query_mental_models(query)
        
        # Format the retrieved mental models as context
        context = ""
        for model in mental_models:
            context += f"\nMental Model: {model['title']}\n"
            context += f"Description: {model['body']}\n"
            if model.get('source'):
                context += f"Source: {model['source']}\n"
            context += "---\n"
        
        return {"context": context, "retrieved_models": mental_models}
    
    def generator(state: ChatState) -> ChatState:
        """Generate a response based on the user input and retrieved context."""
        memory = state.get("memory", [])
        context = state.get("context", "")
        query = state["user_input"]
        
        # Build the prompt with context and conversation history
        prompt = "You are an assistant specialized in explaining mental models and concepts.\n\n"
        
        if context:
            prompt += "Here are some relevant mental models I found:\n" + context + "\n"
        
        prompt += "Please use these mental models to answer the user's question.\n"
        prompt += "If the mental models don't directly address the question, use your knowledge to provide a helpful response.\n\n"
        
        # Add conversation history
        if memory:
            prompt += "Conversation history:\n"
            for message in memory:
                role = "User" if message["role"] == "user" else "Assistant"
                prompt += f"{role}: {message['content']}\n"
        
        prompt += f"\nUser's question: {query}\n"
        prompt += "Assistant: "
        
        # Get response from LLM
        response = llm.invoke(prompt).content
        
        return {"assistant_response": response}
    
    def update_memory(state: ChatState) -> ChatState:
        """Update the memory with the current conversation."""
        new_memory = state.get("memory", []).copy()
        
        # Add the user message
        new_memory.append({"role": "user", "content": state["user_input"]})
        
        # Add the assistant message if available
        if "assistant_response" in state:
            new_memory.append({"role": "assistant", "content": state["assistant_response"]})
        
        return {"memory": new_memory}
    
    # Build the graph
    graph = (
        StateGraph(ChatState)
        .add_node("retriever", retriever)
        .add_node("generator", generator)
        .add_node("memory_updater", update_memory)
        .add_edge("retriever", "generator")
        .add_edge("generator", "memory_updater")
        .add_edge("memory_updater", END)
    )

    # Set the entry point
    graph = graph.set_entry_point("retriever")
    
    return graph.compile() 