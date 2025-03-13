import json
import os
from typing import List, Dict
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_processed_models(file_path: str) -> List[Dict]:
    """Load processed mental models from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_embeddings_batch(texts: List[str], model: str = "text-embedding-3-small", 
                           batch_size: int = 100, sleep_time: int = 1) -> List[List[float]]:
    """Create embeddings for a list of texts in batches to avoid rate limits."""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        response = client.embeddings.create(
            model=model,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
        
        # Sleep to avoid hitting rate limits
        if i + batch_size < len(texts):
            time.sleep(sleep_time)
                
    
    return embeddings

def prepare_for_supabase(mental_models: List[Dict], embeddings: List[List[float]]) -> List[Dict]:
    """Prepare mental models with embeddings for Supabase storage."""
    supabase_records = []
    
    for i, model in enumerate(mental_models):
        if i < len(embeddings):
            record = {
                "title": model["title"],
                "description": model["mental_model"],
                "source": model["source"],
                "embedding": embeddings[i]
            }
            supabase_records.append(record)
    
    return supabase_records

def save_embeddings(data: List[Dict], output_file: str):
    """Save embeddings to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in a .env file.")

# Load processed mental models
processed_models = load_processed_models("vector_store_creation/processed_mental_models.json")

# Extract texts for embedding
texts_to_embed = [model["text_for_embedding"] for model in processed_models]

# Create embeddings
print(f"Creating embeddings for {len(texts_to_embed)} mental models...")
embeddings = create_embeddings_batch(texts_to_embed)

# Prepare data for Supabase
supabase_records = prepare_for_supabase(processed_models, embeddings)

# Save embeddings
save_embeddings(supabase_records, "mental_models_with_embeddings.json")

print(f"\nEmbeddings created and saved for {len(supabase_records)} mental models.")
print("Embedding dimension:", len(embeddings[0]) if embeddings else 0)
print("Sample record (without full embedding):")
if supabase_records:
    sample = supabase_records[0].copy()
    sample["embedding"] = sample["embedding"][:5] + ["..."]
    print(json.dumps(sample, indent=2))