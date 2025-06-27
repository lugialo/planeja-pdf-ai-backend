#!/usr/bin/env python3

"""
Script para testar o DataContextService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_context_service import DataContextService
from unittest.mock import Mock

# Criar um mock da sessão do banco de dados
mock_db = Mock()
user_id = "test_user"

# Criar instância do serviço
service = DataContextService(mock_db, user_id)

# Testar diferentes tipos de prompts
test_prompts = [
    "Olá, tudo bem?",
    "Oi, como você está?",
    "Bom dia!",
    "Obrigado pela ajuda",
    "Quantos orçamentos eu tenho?",
    "Mostre meus clientes",
    "Quais são os produtos mais vendidos?",
    "Analise as vendas do mês passado",
    "Como foi o faturamento?",
    "Qual foi o valor total dos orçamentos aprovados?"
]

print("=== TESTE DO DATACONTEXTSERVICE ===\n")

for prompt in test_prompts:
    print(f"Prompt: '{prompt}'")
    intent = service.analyze_prompt_intent(prompt)
    
    needs_external_data = any([
        intent['needs_budgets'], 
        intent['needs_customers'], 
        intent['needs_categories'], 
        intent['needs_products']
    ])
    
    print(f"Intent: {intent}")
    print(f"Precisa de dados externos: {needs_external_data}")
    print("-" * 50)
