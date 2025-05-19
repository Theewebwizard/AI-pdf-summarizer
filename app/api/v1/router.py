from fastapi import APIRouter
from .endpoints import upload, summarize

router = APIRouter()

router.include_router(upload.router, prefix="/upload", tags=["Upload"])
router.include_router(summarize.router, prefix="/summarize", tags=["Summarize"])