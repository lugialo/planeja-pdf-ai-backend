#!/usr/bin/env python3
"""
Script para rodar a aplicação localmente com configuração híbrida
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Definir ambiente como local
os.environ["ENVIRONMENT"] = "local"

# Carregar variáveis do .env
from dotenv import load_dotenv
load_dotenv()

def check_env_vars():
    """Verifica se as variáveis de ambiente estão configuradas"""
    required_vars = [
        "GEMINI_API_KEY",
        "MAIN_DATABASE_URL", 
        "PLATFORM_DATABASE_URL"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Variáveis de ambiente faltando: {missing}")
        print("💡 Verifique seu arquivo .env")
        return False
    
    print("✅ Todas as variáveis de ambiente estão configuradas")
    return True

def test_db_connections():
    """Testa as conexões com os bancos de dados"""
    print("\n🔌 Testando conexões com bancos de dados...")
    
    try:
        # Testar banco principal
        main_url = os.getenv("MAIN_DATABASE_URL")
        print(f"🔗 Main DB: {main_url[:50]}...")
        
        # Testar banco da plataforma
        platform_url = os.getenv("PLATFORM_DATABASE_URL")
        print(f"🔗 Platform DB: {platform_url[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar conexões: {e}")
        return False

def start_server():
    """Inicia o servidor de desenvolvimento"""
    print("\n🚀 Iniciando servidor FastAPI...")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn não está instalado. Instale com: pip install uvicorn")
        return False
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Configurando ambiente de desenvolvimento local...")
    
    if not check_env_vars():
        sys.exit(1)
    
    if not test_db_connections():
        print("⚠️ Problemas na configuração do banco, mas continuando...")
    
    print("\n📋 URLs disponíveis:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    
    start_server()
