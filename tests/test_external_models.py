import os
import sys
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Carregar variáveis de ambiente
load_dotenv(override=True)

from app.database import ExternalBase
from app.models.external_data import Budget, Category, Product, Customer, User

# Conexão com o banco externo
EXTERNAL_DATABASE_URL = os.getenv('EXTERNAL_DATABASE_URL')

@pytest.fixture
def external_db_session():
    """Cria uma sessão de teste com o banco de dados externo"""
    engine = create_engine(EXTERNAL_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()

def test_table_exists(external_db_session):
    """Verifica se as tabelas existem no banco de dados externo"""
    inspector = inspect(external_db_session.bind)
    
    tables = {
        'Budget': Budget.__tablename__,
        'Category': Category.__tablename__,
        'Product': Product.__tablename__, 
        'Customer': Customer.__tablename__,
        'User': User.__tablename__
    }
    
    for model_name, table_name in tables.items():
        assert inspector.has_table(table_name), f"Tabela {table_name} para o modelo {model_name} não existe!"
        print(f"✅ Tabela {table_name} existe")

def test_budget_query(external_db_session):
    """Testa uma consulta simples na tabela Budget"""
    first_budget = external_db_session.query(Budget).first()
    print(f"Primeiro orçamento: ID={first_budget.id}, Nome={first_budget.name}" if first_budget else "Nenhum orçamento encontrado")
    
    # Não fazemos assert aqui porque o banco pode estar vazio
    # O importante é que a consulta execute sem erros

def test_relationships(external_db_session):
    """Testa as relações entre as tabelas"""
    budget = external_db_session.query(Budget).first()
    if budget:
        print(f"Orçamento: {budget.name}")
        print(f"Categorias: {[c.name for c in budget.categories]}")
        print(f"Usuário: {budget.user.name if budget.user else 'Nenhum'}")
    else:
        print("Nenhum orçamento encontrado para testar relacionamentos")

if __name__ == "__main__":
    # Executar os testes manualmente
    session = next(external_db_session())
    test_table_exists(session)
    test_budget_query(session)
    test_relationships(session)
    print("Todos os testes concluídos!")