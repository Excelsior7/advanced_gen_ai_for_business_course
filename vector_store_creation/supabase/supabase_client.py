from supabase.client import create_client, Client
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from .env file
load = load_dotenv(dotenv_path=".env")

url: str = os.getenv("SUPABASE_URL_AI")
key: str = os.getenv("SUPABASE_KEY_AI")

supabase: Client = create_client(url, key)