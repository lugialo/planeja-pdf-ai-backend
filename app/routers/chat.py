from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models.conversation import Conversation
from models.session import Session
from schemas.chat import SessionResponse, PromptRequest, ConversationResponse, CreateSessionRequest
import google.generativeai as genai
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()
# Configuração do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
        
# Cria uma nova sessão
@router.post("/session/new")
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())

    # Gera o título com base no primeiro prompt
    try:
        title_response = text_model.generate_content(request.first_prompt)
        title = title_response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar título: {str(e)}")

    new_session = Session(
        id=session_id,
        user_id=request.user_id,
        title=title
    )

    db.add(new_session)
    db.commit()
    return {"session_id": session_id, "title": title}

# Rota para obter histórico por sessão
@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    conversations = db.query(Conversation)\
        .filter(Conversation.session_id == session_id)\
        .order_by(Conversation.created_at.asc())\
        .all()
        
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "conversations": conversations
    }
        
@router.post("/ask")
async def ask(
    request: PromptRequest,
    db: Session = Depends(get_db)
):
    try:
        # Verifica se a sessão existe
        session = db.query(Session).filter(Session.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Sessão inválida")
        
        # Geração da resposta
        response = text_model.generate_content(request.prompt)
        
        # Salva na conversa
        db_conversation = Conversation(
            session_id=request.session_id,  # Agora usa session_id
            prompt=request.prompt,
            response=response.text
        )
        
        # Atualiza título da sessão se for o primeiro prompt
        if not session.title:
            session.title = request.prompt[:50] + "..."
            db.add(session)
            
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