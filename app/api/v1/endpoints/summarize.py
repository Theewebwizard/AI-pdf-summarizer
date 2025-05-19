from fastapi import APIRouter, Body
from app.core.llm_utils import summarize_text

router = APIRouter()

@router.post("/")
async def summarize(text: str = Body(...)):
    summary = summarize_text(text)
    return {"summary": summary}
