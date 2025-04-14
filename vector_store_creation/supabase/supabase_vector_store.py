import json
from supabase_client import supabase

# Charger le fichier JSON contenant les modèles mentaux avec leurs embeddings
def load_mental_models():
    with open("vector_store_creation/mental_models_with_embeddings.json", "r") as file:
        mental_models = json.load(file)
    return mental_models

mm = load_mental_models()

# Insérer les modèles mentaux dans la base de données Supabase
def insert_mental_models_to_supabase():
    mental_models = load_mental_models()
    
    print(f"Insertion de {len(mental_models)} modèles mentaux dans Supabase...")
    
    # Traitement par lots (optionnel, pour éviter les erreurs avec de grandes quantités de données)
    batch_size = 50
    for i in range(0, len(mental_models), batch_size):
        batch = mental_models[i:i+batch_size]
        
        # Préparer les données pour l'insertion
        data_to_insert = []
        for model in batch:
            data_to_insert.append({
                "title": model["title"],
                "body": model["description"],  # Correspondance entre "description" dans JSON et "body" dans DB
                "source": model["source"],  # Correspondance entre "description" dans JSON et "body" dans DB
                "embedding": model["embedding"]
            })
        
        # Insérer dans Supabase
        response = (
            supabase.table("documents")
            .insert(data_to_insert)
            .execute()
        )
        
        print(f"Batch {i//batch_size + 1} inséré: {len(data_to_insert)} modèles")
    
    print("Insertion terminée!")


insert_mental_models_to_supabase()