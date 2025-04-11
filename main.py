from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

text_model = genai.GenerativeModel('gemini-1.5-flash')

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Api iniciada."}

@app.post("/ask")
async def ask(request: PromptRequest):
    response = text_model.generate_content(request.prompt)
    return {"response": response.text}