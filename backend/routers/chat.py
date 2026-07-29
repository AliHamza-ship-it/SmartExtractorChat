from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.models.schemas import ChatRequest
from backend.services.llm_service import llm_service
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            async for chunk in llm_service.stream_chat(
                messages=request.messages,
                system_prompt_key=request.system_prompt,
                custom_prompt=request.custom_system_prompt,
                temperature=request.temperature
            ):
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_payload = json.dumps({"error": str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")