from fastapi import FastAPI

app = FastAPI(
    title="BeautyLens AI",
    version="0.1.0"
)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "BeautyLens AI"
    }
