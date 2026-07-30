from supabase import create_client, Client
from backend.config import settings

if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables.")

# Create the Supabase Client connection
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def create_chat_session(system_prompt: str, title: str = "New Chat"):
    """Creates a new chat session in Supabase."""
    response = supabase.table("chat_sessions").insert({
        "title": title,
        "system_prompt": system_prompt
    }).execute()
    return response.data[0] if response.data else None

def save_message(session_id: str, role: str, content: str):
    """Saves a single message (user or assistant) linked to a session ID."""
    response = supabase.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()
    return response.data

def get_session_messages(session_id: str):
    """Fetches all history messages for a specific session sorted chronologically."""
    response = supabase.table("messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", desc=False) \
        .execute()
    return response.data

def get_all_sessions():
    """Fetches all chat sessions for the history sidebar."""
    response = supabase.table("chat_sessions") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()
    return response.data