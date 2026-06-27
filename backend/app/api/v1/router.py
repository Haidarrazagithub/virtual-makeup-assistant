from fastapi import APIRouter

from app.api.v1.endpoints.face_analysis import router as face_router
from app.api.v1.endpoints.makeup import router as makeup_router
from app.api.v1.endpoints.recommendation import router as rec_router

api_router = APIRouter()

api_router.include_router(
    face_router,
    tags=["Face Analysis"],
)

api_router.include_router(
    makeup_router,
    tags=["Makeup Rendering"],
)

api_router.include_router(
    rec_router,
    tags=["Product DB & Recommendations"],
)


