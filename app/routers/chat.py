from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.conversation import Conversation
from schemas.chat import PromptRequest, ConversationResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
# Configuração do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-1.5-flash')

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
        
@router.post("/ask")
async def ask(
    request: PromptRequest,
    db: Session = Depends(get_db)
):
    try:
        # Geração da resposta
        response = text_model.generate_content(request.prompt)
        
        # Salva o registro no banco
        db_conversation = Conversation(
            user_id = request.user_id,
            prompt = request.prompt,
            response = response.text
        )
        db.add(db_conversation)
        db.commit()
        
        return {"response": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/history", response_model=list[ConversationResponse])
async def get_history(user_id: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.created_at.desc())\
        .all()
        
    return conversations