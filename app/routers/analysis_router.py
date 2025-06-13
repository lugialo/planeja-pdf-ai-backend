from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
import os

from database import get_external_db
from services import analysis_service

router = APIRouter(prefix="/analysis", tags=["Analysis & Insights"])
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    text_model = genai.GenerativeModel('gemini-2.5-pro-preview-06-05')
except Exception as e:
    text_model = None
    print(f"Alerta: Chave da API do Gemini não configurada. {e}")
    
@router.get("/{user_id}/sales-trends")
async def get_sales_trends_analysis(
    user_id: str = Path(..., description="ID do usuário para o qual a análise será gerada"),
    days: int = Query(90, ge=1, le=365, description="Número de dias para análise"),
    edb: Session = Depends(get_external_db)
):
    if not text_model:
        raise HTTPException(status_code=503, detail="Alerta: Chave da API do Gemini não configurada")
    
    # Obtém os dados agregados vindos do service
    try:
        trends_data = analysis_service.get_sales_trends_data(
            db=edb, 
            user_id=user_id, 
            days_to_analyze=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar dados externos: {e}")
    
    # Constrói o prompt para a API do Gemini
    
    prompt = f"""
    Você é um analista de negócios especialista em empresas de móveis planejados.
    Analise os seguintes dados de vendas do usuário com ID '{trends_data['user_id']}', chamado de {trends_data['user_name']} nos últimos {trends_data['period_days']} dias e forneça insights acionáveis para ele.

    Dados Consolidados do Usuário:
    - Número de Orçamentos Aprovados: {trends_data['summary']['approved_budgets_count']}
    - Faturamento Total (Vendas): R$ {trends_data['summary']['total_sales_value']:.2f}
    - Ticket Médio por Orçamento: R$ {trends_data['summary']['average_budget_value']:.2f}

    Top 5 Categorias Mais Populares (por nº de orçamentos deste usuário):
    {', '.join([f'{cat["name"]} ({cat["count"]})' for cat in trends_data["top_categories"]]) if trends_data["top_categories"] else "Nenhuma"}

    Top 5 Produtos Mais Populares (por nº de orçamentos deste usuário):
    {', '.join([f'{prod["name"]} ({prod["count"]})' for prod in trends_data["top_products"]]) if trends_data["top_products"] else "Nenhum"}

    Com base nestes dados pessoais de desempenho, gere uma análise em 3 partes para este usuário:
    1.  **Resumo Executivo**: Uma visão geral e rápida dos seus resultados.
    2.  **Pontos de Destaque**: Identifique os seus pontos mais fortes e os pontos de atenção no seu desempenho.
    3.  **Sugestões Estratégicas e Pessoais**: Dê 2 a 3 sugestões claras e práticas que este usuário pode implementar para melhorar seus resultados.

    Use um tom de coaching, direcionado diretamente ao usuário. Lembre-se de cumprimentá-lo utilizando o nome dele, {trends_data['user_name']}
    """
    
    # Chama a API e retorna a resposta
    try:
        response = text_model.generate_content(prompt)
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar análise com a API do Gemini: {str(e)}")
    
@router.get("/debug-db-tables")
async def debug_db_connection(edb: Session = Depends(get_external_db)):
    """
    Endpoint de teste para verificar TODAS as tabelas que a aplicação consegue ver no schema 'public'.
    """
    try:
        # Consulta SQL modificada para ser mais ampla
        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        result = edb.execute(query).fetchall()
        
        # Converte o resultado para uma lista simples de nomes de tabela
        tables = [row[0] for row in result]
        
        return {
            "message": "Consulta executada com sucesso. Estas são todas as tabelas encontradas no schema 'public'.",
            "database_connected": str(edb.bind.url), # Mostra a URL de conexão que está sendo usada
            "tables_in_public_schema": tables
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar consulta de debug: {str(e)}")