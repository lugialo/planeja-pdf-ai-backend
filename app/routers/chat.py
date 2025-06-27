from fastapi import APIRouter, Depends, HTTPException
import uuid
from sqlalchemy.orm import Session
from app.database import get_main_db, get_platform_db
from app.models.conversation import Conversation
from app.models.session import Session as SessionModel
from app.schemas.chat import SessionResponse, PromptRequest, ConversationResponse, CreateSessionRequest, CreateSessionResponse
from app.services.data_context_service import DataContextService
import google.generativeai as genai
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv(override=True)
# Configuração do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')

# Cria uma nova sessão
@router.post("/session/new", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest, 
    db: Session = Depends(get_main_db),
    platform_db: Session = Depends(get_platform_db)
):
    session_id = str(uuid.uuid4())

    # Cria o serviço de contexto de dados (usa o banco da plataforma)
    data_service = DataContextService(platform_db, request.user_id)
    
    # Constrói o contexto completo para o primeiro prompt
    full_context = data_service.build_context_for_ai(request.first_prompt)
    
    # Gera o título com base no primeiro prompt
    try:
        title_prompt = f"Crie um título curto (maxímo de 5 palavras) para um prompt que segue: '{request.first_prompt}. Seja direto na criação do título.'"
        title_response = text_model.generate_content(title_prompt)
        title = title_response.text.strip()
        
        # Remove aspas se houver
        title = title.strip('"').strip("'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar título: {str(e)}")

    # Cria a sessão
    new_session = SessionModel(
        id=session_id,
        user_id=request.user_id,
        title=title
    )
    
    try:
        # Gera a primeira resposta ANTES de salvar no banco
        first_response = text_model.generate_content(full_context)
        response_text = first_response.text
        
        # Agora salva tudo em uma única transação
        db.add(new_session)
        db.flush()  # Força a sessão ser gravada sem commit ainda
        
        # Cria a primeira conversa na mesma transação
        first_conversation = Conversation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            prompt=request.first_prompt,
            response=response_text
        )
        
        db.add(first_conversation)
        db.commit()  # Commit de tudo junto
        
        # Verificar se ambos foram salvos
        session_check = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        conversation_check = db.query(Conversation).filter(Conversation.session_id == session_id).first()
        
        if not session_check:
            raise Exception("Sessão não foi salva corretamente no banco")
        if not conversation_check:
            raise Exception("Conversa não foi salva corretamente no banco")
            
        print(f"✅ Sessão e primeira conversa criadas: {session_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar sessão e conversa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessão: {str(e)}")
    
    return {
        "session_id": session_id, 
        "title": title,
        "first_response": response_text
    }

# Rota para obter histórico por sessão
@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_main_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
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
    db: Session = Depends(get_main_db),
    platform_db: Session = Depends(get_platform_db)
):
    try:
        # Verifica se a sessão existe (no banco principal)
        session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Sessão inválida")
        
        # Cria o serviço de contexto de dados (usa o banco da plataforma)
        data_service = DataContextService(platform_db, session.user_id)
        
        # Constrói o contexto completo para o prompt
        full_context = data_service.build_context_for_ai(request.prompt)
        
        # Adiciona histórico da conversa para contexto
        recent_conversations = db.query(Conversation)\
            .filter(Conversation.session_id == request.session_id)\
            .order_by(Conversation.created_at.desc())\
            .limit(5)\
            .all()
        
        if recent_conversations:
            conversation_history = "\n\nHistórico da conversa (mais recente primeiro):"
            for conv in reversed(recent_conversations):  # Inverte para ordem cronológica
                conversation_history += f"\nUsuário: {conv.prompt}"
                conversation_history += f"\nAssistente: {conv.response[:200]}..."
            
            full_context += conversation_history
        
        # Gera a resposta ANTES de salvar no banco
        response = text_model.generate_content(full_context)
        
        # Salva a conversa em uma transação
        db_conversation = Conversation(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            prompt=request.prompt,
            response=response.text
        )
        
        # Atualiza título da sessão se necessário
        if not session.title or session.title.strip() == "":
            session.title = request.prompt[:50] + ("..." if len(request.prompt) > 50 else "")
            db.add(session)
            
        db.add(db_conversation)
        db.commit()
        
        print(f"✅ Conversa salva para sessão: {request.session_id}")
        
        return {"response": response.text}
        
    except HTTPException:
        raise  # Re-levanta HTTPException específicas
    except Exception as e:
        db.rollback()
        print(f"❌ Erro no endpoint /ask: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
@router.get("/history", response_model=list[SessionResponse])
async def get_history(user_id: str, db: Session = Depends(get_main_db)):
    sessions = db.query(SessionModel)\
        .filter(SessionModel.user_id == user_id)\
        .order_by(SessionModel.created_at.desc())\
        .all()
        
    result = []
    for session in sessions:
        conversations = db.query(Conversation)\
            .filter(Conversation.session_id == session.id)\
            .order_by(Conversation.created_at.asc())\
            .all()
            
        result.append({
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at,
            "conversations": conversations
        })
        
    return result

@router.post("/debug/analyze")
async def debug_analyze_prompt(
    prompt: str,
    user_id: str,
    platform_db: Session = Depends(get_platform_db)
):
    """Endpoint para debug - analisa um prompt e retorna os dados encontrados"""
    try:
        data_service = DataContextService(platform_db, user_id)
        
        # Análise do intent
        intent = data_service.analyze_prompt_intent(prompt)
        
        # Busca de dados
        budget_data = None
        if intent['needs_budgets'] or 'orçamento' in prompt.lower() or 'quantos' in prompt.lower():
            budget_data = data_service.get_budget_data(
                time_period=intent['time_period'],
                status_filter=intent['status_filter']
            )
        
        # Contexto completo
        full_context = data_service.build_context_for_ai(prompt)
        
        return {
            "prompt": prompt,
            "user_id": user_id,
            "intent": intent,
            "budget_data": budget_data,
            "full_context": full_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no debug: {str(e)}")

@router.get("/debug/test-db/{user_id}")
async def test_database_connection(
    user_id: str,
    platform_db: Session = Depends(get_platform_db)
):
    """Endpoint simples para testar conexão com banco de dados"""
    try:
        from app.models.external_data import ExternalBudget
        
        # Busca simples
        budgets = platform_db.query(ExternalBudget).filter(ExternalBudget.userId == user_id).all()
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_budgets_found": len(budgets),
            "sample_budgets": [
                {
                    "id": b.id,
                    "name": b.name,
                    "status": b.status.value if hasattr(b.status, 'value') else str(b.status),
                    "total": float(b.total)
                } for b in budgets[:3]
            ] if budgets else []
        }
        
    except Exception as e:
        return {
            "status": "error",
            "user_id": user_id,
            "error": str(e)
        }

@router.get("/debug/check-migration-status")
async def check_migration_status(db: Session = Depends(get_main_db)):
    """Verifica se as migrações foram aplicadas corretamente"""
    try:
        from sqlalchemy import text
        
        # Verifica se as tabelas existem
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('sessions', 'conversations', 'alembic_version')
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        # Verifica a versão do Alembic
        alembic_version = None
        if 'alembic_version' in tables:
            version_result = db.execute(text("SELECT version_num FROM alembic_version"))
            version_row = version_result.fetchone()
            if version_row:
                alembic_version = version_row[0]
        
        # Verifica estrutura das tabelas
        table_structures = {}
        for table in ['sessions', 'conversations']:
            if table in tables:
                columns_result = db.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """))
                
                table_structures[table] = [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == 'YES',
                        "default": row[3]
                    }
                    for row in columns_result.fetchall()
                ]
        
        # Teste de inserção simples na tabela sessions
        test_session_id = str(uuid.uuid4())
        try:
            test_session = SessionModel(
                id=test_session_id,
                user_id="test_user",
                title="Test Session"
            )
            db.add(test_session)
            db.commit()
            
            # Remove o teste
            db.query(SessionModel).filter(SessionModel.id == test_session_id).delete()
            db.commit()
            
            insert_test = "SUCCESS"
        except Exception as e:
            db.rollback()
            insert_test = f"FAILED: {str(e)}"
        
        return {
            "status": "success",
            "tables_found": tables,
            "alembic_version": alembic_version,
            "expected_version": "7ae593497572",  # Nossa versão atual
            "table_structures": table_structures,
            "session_insert_test": insert_test,
            "migration_applied": 'sessions' in tables and 'conversations' in tables,
            "version_match": alembic_version == "7ae593497572"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Erro ao verificar status das migrações"
        }

@router.post("/debug/force-migration")
async def force_migration():
    """CUIDADO: Força a aplicação das migrações. Use apenas em desenvolvimento!"""
    try:
        import subprocess
        import os
        
        # Verifica se estamos em produção
        environment = os.getenv("ENVIRONMENT", "production")
        if environment == "production":
            return {
                "status": "blocked",
                "message": "Migrations em produção devem ser executadas no deploy"
            }
        
        # Executa as migrações
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="/app"  # Caminho do container
        )
        
        return {
            "status": "executed",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }