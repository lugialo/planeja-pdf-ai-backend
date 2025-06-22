from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from routers import chat, analysis_router, pdf_router, customer_router

app = FastAPI()

os.makedirs("app/static/budgets", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat")

app.include_router(analysis_router.router)

app.include_router(pdf_router.router)

app.include_router(customer_router.router)

@app.get("/")
async def root():
    return {"message": "API de Orçamentos de Móveis - Online"}