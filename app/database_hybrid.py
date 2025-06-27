# app/database_local.py - Versão para desenvolvimento local e produção

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from dotenv import load_dotenv

# Carregar variáveis do .env em desenvolvimento
load_dotenv()

# --- Bases Declarativas ---
MainBase = declarative_base()
PlatformBase = declarative_base()

# --- Detectar ambiente ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
IS_LOCAL = ENVIRONMENT == "local"

print(f"🚀 Ambiente detectado: {ENVIRONMENT}")

# --- Configuração do Banco Principal (MainBase) ---
main_engine = None
MainSessionLocal = None

if IS_LOCAL:
    # DESENVOLVIMENTO LOCAL
    MAIN_DATABASE_URL = os.getenv("MAIN_DATABASE_URL")
    if MAIN_DATABASE_URL:
        try:
            main_engine = create_engine(MAIN_DATABASE_URL)
            MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)
            print("✅ Banco principal (local) configurado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao configurar banco principal local: {e}")
    else:
        print("⚠️ MAIN_DATABASE_URL não encontrada no .env")
else:
    # PRODUÇÃO (Cloud SQL)
    try:
        from google.cloud.sql.connector import Connector
        
        def get_main_db_connection_data():
            """Busca dados de conexão do Cloud SQL do Secret Manager."""
            db_config_str = os.getenv("MAIN_DATABASE_URL", "{}")
            return json.loads(db_config_str)

        db_data = get_main_db_connection_data()
        if db_data.get("connection_name"):
            connector = Connector()
            
            def get_main_conn():
                return connector.connect(
                    db_data["connection_name"],
                    "pg8000",
                    user=db_data["user"],
                    password=db_data["password"],
                    db=db_data["db_name"],
                )

            main_engine = create_engine("postgresql+pg8000://", creator=get_main_conn)
            MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=main_engine)
            print("✅ Banco principal (Cloud SQL) configurado com sucesso")
        else:
            print("⚠️ Configuração do Cloud SQL não encontrada")
    except Exception as e:
        print(f"❌ Erro ao configurar Cloud SQL: {e}")

# --- Configuração do Banco da Plataforma (PlatformBase) ---
platform_engine = None
PlatformSessionLocal = None

PLATFORM_DATABASE_URL = os.getenv("PLATFORM_DATABASE_URL")
if PLATFORM_DATABASE_URL:
    try:
        platform_engine = create_engine(PLATFORM_DATABASE_URL)
        PlatformSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=platform_engine)
        print("✅ Banco da plataforma (Supabase) configurado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao configurar banco da plataforma: {e}")
else:
    print("⚠️ PLATFORM_DATABASE_URL não encontrada")

# --- Funções de Dependência do FastAPI ---
def get_main_db():
    """Fornece uma sessão para o banco de dados principal."""
    if not MainSessionLocal:
        raise Exception("Sessão do banco principal não configurada. Verifique MAIN_DATABASE_URL")
    
    db = MainSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_platform_db():
    """Fornece uma sessão para o banco da plataforma."""
    if not PlatformSessionLocal:
        raise Exception("Sessão do banco da plataforma não configurada. Verifique PLATFORM_DATABASE_URL")
    
    db = PlatformSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Aliases para compatibilidade
def get_external_db():
    """Alias para get_platform_db"""
    return get_platform_db()

# Para depuração
if __name__ == "__main__":
    print(f"Ambiente: {ENVIRONMENT}")
    print(f"Main engine: {main_engine is not None}")
    print(f"Platform engine: {platform_engine is not None}")
