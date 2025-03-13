import json
from typing import List, Dict
import re

def load_mental_models(file_path: str) -> List[Dict]:
    """Load mental models from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_structured_text(mental_model: Dict) -> str:
    """Create a structured text representation of the mental model."""
    parts = [
        f"Title: {mental_model['title']}",
        f"Description: {mental_model['mental_model']}"
    ]
    
    if mental_model['source']:
        parts.append(f"Source: {mental_model['source']}")
        
    return " | ".join(parts)

def preprocess_mental_models(mental_models: List[Dict]) -> List[Dict]:
    """Preprocess mental models for embedding."""
    processed_models = []
    
    for model in mental_models:
        # Clean the text fields
        cleaned_model = {
            'title': clean_text(model['title']),
            'mental_model': clean_text(model['mental_model']),
            'source': clean_text(model['source']) if model['source'] else None
        }
        
        # Create a structured text representation for embedding
        cleaned_model['text_for_embedding'] = create_structured_text(cleaned_model)
        
        processed_models.append(cleaned_model)
    
    return processed_models

def save_processed_models(processed_models: List[Dict], output_file: str):
    """Save processed mental models to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_models, f, ensure_ascii=False, indent=4)


# Load mental models
mental_models = load_mental_models("vector_store_creation/mental_models.json")

# Preprocess mental models
processed_models = preprocess_mental_models(mental_models)

# Save processed models
save_processed_models(processed_models, "processed_mental_models.json")

# Print sample
print("\nSample processed mental model:")
print(processed_models[0]['text_for_embedding']) 