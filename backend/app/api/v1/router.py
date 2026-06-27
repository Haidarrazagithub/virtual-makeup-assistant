from fastapi import APIRouter

from app.api.v1.endpoints.face_analysis import router as face_router
from app.api.v1.endpoints.makeup import router as makeup_router
from app.api.v1.endpoints.recommendation import router as rec_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.look import router as look_router

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

api_router.include_router(
    chat_router,
    tags=["Chat History & AI"],
)

api_router.include_router(
    look_router,
    prefix="/looks",
    tags=["Saved Looks"],
)



