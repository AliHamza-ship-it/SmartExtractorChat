from supabase import create_client, Client
from config import settings

if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def create_chat_session(user_id: str, system_prompt: str, title: str = "New Chat"):
    response = supabase.table("chat_sessions").insert({
        "user_id": user_id,
        "title": title,
        "system_prompt": system_prompt
    }).execute()
    return response.data[0] if response.data else None

# NEW: Function to update the title of an existing session
def update_session_title(session_id: str, new_title: str):
    response = supabase.table("chat_sessions").update({
        "title": new_title
    }).eq("id", session_id).execute()
    return response.data

def save_message(session_id: str, role: str, content: str):
    response = supabase.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()
    return response.data

def get_session_messages(session_id: str):
    response = supabase.table("messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", desc=False) \
        .execute()
    return response.data

def get_all_sessions(user_id: str):
    response = supabase.table("chat_sessions") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()
    return response.data