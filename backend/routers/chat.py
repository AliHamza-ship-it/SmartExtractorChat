from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest, CreateSessionRequest
from backend.services.llm_service import llm_service
from backend.services import db_service
from backend.dependencies import get_current_user
import json

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
    # Note: For peak security, you should verify the session_id belongs to user.id here.
    try:
        return db_service.get_session_messages(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def chat_endpoint(request: ChatRequest, user=Depends(get_current_user)):
    current_session_id = request.session_id
    last_user_msg = request.messages[-1].content if request.messages else "New Chat"

    if not current_session_id:
        title = last_user_msg[:30] + ("..." if len(last_user_msg) > 30 else "")
        system_prompt = request.custom_system_prompt or request.system_prompt or "AI Tech Mentor"
        session = db_service.create_chat_session(user_id=user.id, system_prompt=system_prompt, title=title)
        if session:
            current_session_id = session["id"]

    if current_session_id and request.messages:
        db_service.save_message(session_id=current_session_id, role="user", content=request.messages[-1].content)

    async def event_generator():
        full_assistant_response = ""
        try:
            yield f"data: {json.dumps({'session_id': current_session_id})}\n\n"

            async for chunk in llm_service.stream_chat(
                messages=request.messages,
                system_prompt_key=request.system_prompt,
                custom_prompt=request.custom_system_prompt,
                temperature=request.temperature
            ):
                full_assistant_response += chunk
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"

            if current_session_id and full_assistant_response:
                db_service.save_message(session_id=current_session_id, role="assistant", content=full_assistant_response)

            yield "data: [DONE]\n\n"

        except Exception as e:
            err_payload = json.dumps({"error": str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")