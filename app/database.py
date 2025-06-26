# app/database.py (Versão correta para produção com 2 bancos)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from google.cloud.sql.connector import Connector

# --- Bases Declarativas ---
# Uma para cada banco de dados para evitar conflitos de metadados
MainBase = declarative_base()
PlatformBase = declarative_base()

# --- Conexão para o Banco Principal (Cloud SQL) ---
main_engine = None
MainSessionLocal = None

def get_main_db_connection_data():
    """Busca e processa os dados de conexão do Cloud SQL a partir da variável de ambiente."""
    db_config_str = os.getenv("MAIN_DATABASE_URL", "{}")
    return json.loads(db_config_str)

try:
    db_data = get_main_db_connection_data()
    # Só tenta criar a conexão se a configuração foi carregada
    if db_data.get("connection_name"):
        connector = Connector()
        
        def get_main_conn():
            # Função que o SQLAlchemy usará para criar cada nova conexão
            return connector.connect(
                db_data["connection_name"],
                "pg8000",
                user=db_data["user"],
                password=db_data["password"],
                db=db_data["db_name"],
            )

        main_engine = create_engine("postgresql+pg8000://", creator=get_main_conn)
        MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)
        print("INFO: Conector do Cloud SQL configurado com sucesso.")
    else:
        print("AVISO: Configuração do MAIN_DATABASE_URL não encontrada ou inválida.")
except Exception as e:
    print(f"ERRO: Falha ao configurar o conector do Cloud SQL: {e}")


# --- Conexão para o Banco da Plataforma (Supabase) ---
platform_engine = None
PlatformSessionLocal = None

PLATFORM_DATABASE_URL = os.getenv("PLATFORM_DATABASE_URL")
if PLATFORM_DATABASE_URL:
    try:
        platform_engine = create_engine(PLATFORM_DATABASE_URL)
        PlatformSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=platform_engine)
        print("INFO: Motor do banco da plataforma (Supabase) configurado com sucesso.")
    except Exception as e:
        print(f"ERRO: Falha ao configurar o motor do banco da plataforma: {e}")
else:
    print("AVISO: PLATFORM_DATABASE_URL não encontrada.")

# --- Funções de Dependência do FastAPI ---

def get_main_db():
    """Fornece uma sessão para o banco de dados principal (Cloud SQL)."""
    if not MainSessionLocal:
        raise Exception("Sessão do banco de dados principal não pôde ser configurada.")
    
    db = MainSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_platform_db():
    """Fornece uma sessão para o banco de dados da plataforma (Supabase)."""
    if not PlatformSessionLocal:
        raise Exception("Sessão do banco de dados da plataforma não pôde ser configurada.")
    
    db = PlatformSessionLocal()
    try:
        yield db
    finally:
        db.close()