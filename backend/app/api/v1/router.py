from fastapi import APIRouter

from app.api.v1.endpoints.face_analysis import router as face_router

api_router = APIRouter()

api_router.include_router(
    face_router,
    tags=["Face Analysis"]
)
