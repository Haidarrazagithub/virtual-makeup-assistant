from fastapi import APIRouter

from app.api.v1.endpoints.face_analysis import router as face_router
from app.api.v1.endpoints.face_mesh import router as face_mesh_router
from app.api.v1.endpoints.lipstick import router as lipstick_router
from app.api.v1.endpoints.blush import router as blush_router

api_router = APIRouter()

api_router.include_router(
    face_router,
    tags=["Face Analysis"]
)

api_router.include_router(
    face_mesh_router,
    tags=["Face Mesh"]
)

api_router.include_router(
    lipstick_router,
    tags=["Lipstick"]
)

api_router.include_router(
    blush_router,
    tags=["Blush"]
)
