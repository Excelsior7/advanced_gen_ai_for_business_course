# Mental Models Chatbot

A chatbot application that answers questions based on mental models using RAG (Retrieval-Augmented Generation).

## Features

- Interactive chat interface built with Streamlit
- Langraph for chatbot logic and conversation memory
- Supabase vector store for semantic search of mental models
- Real-time display of relevant mental models used for answers

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_URL_AI=your_supabase_url
   SUPABASE_KEY_AI=your_supabase_key
   ```

## Running the Chatbot

To start the chatbot application:

```bash
streamlit run chatbot/chatbot_streamlit.py
```

## Project Structure

- `chatbot/`: Contains the Streamlit chatbot application
- `vector_store_creation/`: Contains scripts for creating and managing the vector store
  - `supabase/`: Contains Supabase client configuration and vector store operations
  - `embed_mental_models.py`: Script for creating embeddings for mental models

## How It Works

1. User inputs a question
2. The system creates an embedding for the question
3. Supabase vector store retrieves relevant mental models based on semantic similarity
4. LLM generates a response using the retrieved mental models as context
5. The response and the relevant mental models are shown to the user