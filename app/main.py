# app/main.py (Versão Limpa para Cloud Run)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

from app.routers import chat, analysis_router, pdf_router, customer_router

app = FastAPI()

# (Opcional) Cria a pasta de static se necessário
os.makedirs("app/static/budgets", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos routers
app.include_router(chat.router, prefix="/chat")
app.include_router(analysis_router.router)
app.include_router(pdf_router.router)
app.include_router(customer_router.router)

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root():
    return {"message": "API de Orçamentos de Móveis - Online"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "planeja-pdf-ai-backend"}