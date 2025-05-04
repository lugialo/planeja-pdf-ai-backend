from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from routers import chat

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas de chat
app.include_router(chat.router, prefix="/chat")

@app.get("/")
async def root():
    return {"message": "API de Orçamentos de Móveis - Online"}