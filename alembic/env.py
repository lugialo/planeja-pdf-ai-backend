# alembic/env.py

from logging.config import fileConfig
import os
import json

# Importações necessárias para a conexão segura
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine

from alembic import context

from app.database import MainBase
from app.models.conversation import Conversation
from app.models.session import Session

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = MainBase.metadata

# --- Lógica de Conexão Online para Cloud Run ---

def run_migrations_online() -> None:
    """Executa as migrações em modo 'online'.
    
    Esta função foi adaptada para se conectar ao Cloud SQL a partir do Cloud Run,
    buscando as credenciais do Secret Manager.
    """
    
    # Inicializa o conector do Cloud SQL
    connector = Connector()
    # Função para obter as credenciais do Secret Manager
    def get_connection_data():
        project_id = os.getenv('GCP_PROJECT', 'gen-lang-client-0700951327') # Fallback para o seu ID
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/MAIN_DATABASE_URL/versions/latest"
        response = client.access_secret_version(name=name)
        payload = response.payload.data.decode("UTF-8")
        return json.loads(payload)

    db_data = get_connection_data()

    # Função que o SQLAlchemy usará para criar a conexão
    def get_conn():
        return connector.connect(
            db_data["connection_name"],
            "pg8000",
            user=db_data["user"],
            password=db_data["password"],
            db=db_data["db_name"],
        )

    # Cria a engine do SQLAlchemy usando a função de conexão do Cloud SQL Connector
    connectable = create_engine(
        "postgresql+pg8000://",
        creator=get_conn,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# O modo offline não é usado no deploy, mas mantemos a função
def run_migrations_offline() -> None:
    pass


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()