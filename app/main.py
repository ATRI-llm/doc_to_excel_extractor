from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Document Extraction Service"
)

app.include_router(router)