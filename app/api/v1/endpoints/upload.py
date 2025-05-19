from fastapi import APIRouter, File, UploadFile
from app.core.pdf_utils import extract_text_from_pdf
from app.core.storage import save_file_temp

router = APIRouter()

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    path = await save_file_temp(file)
    text = extract_text_from_pdf(path)
    return {"text": text}