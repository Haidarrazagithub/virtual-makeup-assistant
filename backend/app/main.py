import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI
from app.core.database import Base, engine
from app.models.product import Product
from app.models.chat import ChatSession, ChatMessage
from app.models.look import SavedLook

# Auto-create all tables in the SQLite database
Base.metadata.create_all(bind=engine)

from app.api.v1.router import api_router

app = FastAPI(
    title="BeautyLens AI",
    version="0.1.0"
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "BeautyLens AI"
    }
