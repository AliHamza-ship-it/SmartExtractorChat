from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest, CreateSessionRequest
from services.llm_service import llm_service
from services import db_service
from dependencies import get_current_user
import json
import logging
import asyncio 

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/sessions")
def list_sessions(user=Depends(get_current_user)):
    try:
        return db_service.get_all_sessions(user_id=user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions")
def create_session(request: CreateSessionRequest, user=Depends(get_current_user)):
    try:
        return db_service.create_chat_session(
            user_id=user.id,
            system_prompt=request.system_prompt, 
            title=request.title
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, user=Depends(get_current_user)):
    try:
        return db_service.get_session_messages(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def chat_endpoint(request: ChatRequest, user=Depends(get_current_user)):
    current_session_id = request.session_id
    last_user_msg = request.messages[-1].content if request.messages else "New Chat"
    
    is_new_session = False

    # 1. Create a new session if one doesn't exist
    if not current_session_id:
        is_new_session = True
        # Set a temporary placeholder title 
        title = "New Chat"
        system_prompt = request.custom_system_prompt or request.system_prompt or "AI Tech Mentor"
        session = db_service.create_chat_session(user_id=user.id, system_prompt=system_prompt, title=title)
        if session:
            current_session_id = session["id"]

    # 2. Save the user's prompt to the database immediately
    if current_session_id and request.messages:
        db_service.save_message(session_id=current_session_id, role="user", content=last_user_msg)
        
    # NEW 3: Background Worker to Generate Title
    async def generate_and_update_title(session_id: str, prompt: str):
        try:
            new_title = await llm_service.generate_chat_title(prompt)
            db_service.update_session_title(session_id, new_title)
        except Exception as e:
            logger.error(f"Background title generation failed: {e}")

    # Launch the title generator in the background ONLY if it's a new session
    if is_new_session and current_session_id:
        asyncio.create_task(generate_and_update_title(current_session_id, last_user_msg))

    # 4. Background Worker Function for chat response
    async def generate_and_save_worker(queue: asyncio.Queue, session_id: str, messages, sys_prompt, cust_prompt, temp):
        full_assistant_response = ""
        try:
            async for chunk in llm_service.stream_chat(messages, sys_prompt, cust_prompt, temp):
                full_assistant_response += chunk
                await queue.put(chunk)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            await queue.put(f"[ERROR] {str(e)}")
        finally:
            await queue.put(None)
            if session_id and full_assistant_response:
                try:
                    clean_response = full_assistant_response.replace('\x00', '')
                    db_service.save_message(session_id=session_id, role="assistant", content=clean_response)
                except Exception as e:
                    logger.error(f"Failed to save assistant message in background: {e}")

    # 5. Setup communication Queue and launch the chat response worker
    stream_queue = asyncio.Queue()
    asyncio.create_task(
        generate_and_save_worker(
            stream_queue, 
            current_session_id, 
            request.messages, 
            request.system_prompt, 
            request.custom_system_prompt, 
            request.temperature
        )
    )

    # 6. HTTP Event Generator
    async def event_generator():
        try:
            yield f"data: {json.dumps({'session_id': current_session_id})}\n\n"
            
            while True:
                chunk = await stream_queue.get()
                
                if chunk is None:
                    yield "data: [DONE]\n\n"
                    break
                
                if chunk.startswith("[ERROR]"):
                    err_payload = json.dumps({"error": chunk})
                    yield f"data: {err_payload}\n\n"
                    break
                
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"
                
        except asyncio.CancelledError:
            logger.info("Client cleanly disconnected (Chat switched). Background DB insertion will finish.")
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")