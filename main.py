from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.core.config import settings
from app.database import engine, Base
from app.api.routes import router as api_router
from app.api.chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Travel Recommender Agent",
    description="سیستم هوشمند پیشنهاد مسیر سفر",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(api_router, prefix="/api")
app.include_router(chat_router, prefix="/chat")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/map")
async def map_view(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

@app.get("/chat")
async def chat_view(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 