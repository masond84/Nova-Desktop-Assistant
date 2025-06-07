from supabase import create_client
from typing import Dict

# KEYS
SUPABASE_URL = "https://plxafippbfwptdetsiay.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBseGFmaXBwYmZ3cHRkZXRzaWF5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MDk4NzAsImV4cCI6MjA2MDM4NTg3MH0.Z01QpVBnvCfOOi_GNP8RHFid_EDz3agsEhwQbdRx4Ps"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define the memory store class
def fetch_user_memory(user_id: str = "local-user") -> Dict[str, list]:
    response = supabase.table("user_memory").select("*").eq("user_id", user_id).execute()
    memory_by_category = {"preferences": [], "hobbies": [], "locations": []}
    for item in response.data:
        memory_by_category[item["category"]].append(item["fact"])
    return memory_by_category

def store_memory(category: str, fact: str, user_id: str = "local-user"):
    existing = fetch_user_memory(user_id)
    if fact.lower() not in [f.lower() for f in existing.get(category, [])]:
        supabase.table("user_memory").insert({
            "user_id": user_id,
            "category": category,
            "fact": fact
        }).execute()