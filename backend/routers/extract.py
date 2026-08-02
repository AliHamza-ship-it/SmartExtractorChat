from fastapi import APIRouter, HTTPException
from models.schemas import ExtractRequest, ExtractResponse
from services.llm_service import llm_service

router = APIRouter(prefix="/api/extract", tags=["extract"])

@router.post("", response_model=ExtractResponse)
async def extract_endpoint(request: ExtractRequest):
    if not request.raw_text.strip():
        raise HTTPException(status_code=400, detail="Raw text cannot be empty")
        
    result = await llm_service.extract_invoice(request.raw_text)
    return result