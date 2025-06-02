from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://root:Asdlkj3547!@localhost:5432/planeja-pdf-ai-backend")


# Configuração do banco principal
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuração do banco de dados externo (planeja-pdf, no Supabase)
EXTERNAL_DATABASE_URL = os.getenv("EXTERNAL_DATABASE_URL")
if EXTERNAL_DATABASE_URL:
    external_engine = create_engine(EXTERNAL_DATABASE_URL)
    ExternalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    ExternalBase = declarative_base()
    try:
        with external_engine.connect() as externalConnection:
            result = externalConnection.execute(text("SELECT 1"))
            print("Conexão com o banco externo bem-sucedida.", result.scalar())
    except Exception as e:
        print("Erro ao conectar ao banco externo:", e)
else:
    external_engine = None
    ExternalSessionLocal = None
    ExternalBase = None

# def test_external_connection():
#     if external_engine is None:
#         print("External database engine is not configured.")
#         return
#     try:
#         with external_engine.connect() as connection:
#             result = connection.execute("SELECT 1")
#             print("Conexão bem-sucedida:", result.scalar())
#     except Exception as e:
#         print("Erro ao conectar ao banco externo:", e)