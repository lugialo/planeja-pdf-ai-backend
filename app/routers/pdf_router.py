from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
import io
import json
import google.generativeai as genai
import os
from datetime import datetime, timedelta

from app.database import get_platform_db
from app.models.external_data import ExternalUser, ExternalCustomer 
from app.schemas.pdf_schema import BudgetGenerationRequest
from app.services import document_service

# Configuração do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-1.5-pro')

router = APIRouter(prefix="/documents", tags=["Geração de Documentos"])

@router.post("/generate-budget")
async def generate_dynamic_budget_document(
    request: BudgetGenerationRequest,
    edb: Session = Depends(get_platform_db)
):
    customer = edb.query(ExternalCustomer).filter(ExternalCustomer.id == request.customer_id).first()
    user_with_settings = edb.query(ExternalUser).options(
        joinedload(ExternalUser.settings)
    ).filter(ExternalUser.id == request.user_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    if not user_with_settings or not user_with_settings.settings:
        raise HTTPException(status_code=404, detail="Usuário ou suas configurações não encontrados.")
    
    settings = user_with_settings.settings

    prompt_for_gemini = f"""
    Você é um especialista em vendas de móveis planejados. Sua tarefa é criar um orçamento detalhado com base no pedido de um cliente.
    Pedido do Cliente: "{request.description}"
    Gere uma lista de categorias e produtos para este orçamento. Calcule o preço de cada produto e o total geral.
    Responda APENAS com um objeto JSON válido, sem nenhum texto ou formatação adicional antes ou depois. O JSON deve ter a seguinte estrutura:
    {{
      "name": "Orçamento para Home Office",
      "categories": [
        {{
          "name": "Mobiliário Principal",
          "products": [
            {{"name": "Escrivaninha em L em MDF amadeirado", "price": 1800.00}},
            {{"name": "Estante de livros alta (5 prateleiras)", "price": 1250.50}},
            {{"name": "Gaveteiro com 3 gavetas e rodízios", "price": 750.00}}
          ]
        }}
      ],
      "total": 3800.50
    }}
    """

    try:
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
        }
        
        response = text_model.generate_content(
            prompt_for_gemini,
            safety_settings=safety_settings
        )
        
        raw_text = response.text
        print(f"Raw Gemini Response: '{raw_text}'")

        json_start = raw_text.find('{')
        json_end = raw_text.rfind('}')

        if json_start == -1 or json_end == -1:
            raise ValueError("Não foi encontrado um objeto JSON válido na resposta da IA.")
            
        json_text = raw_text[json_start:json_end+1]
        
        ai_budget_data = json.loads(json_text)

    except (json.JSONDecodeError, ValueError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar ou processar dados da IA: {str(e)}")

    budget_data = {
        "budget": {
            "id": f"{datetime.now().strftime('%Y%m%d')}",
            "name": ai_budget_data.get("name", "Orçamento Personalizado"),
            "categories": ai_budget_data.get("categories", []),
            "total": ai_budget_data.get("total", 0.0),
            "createdAt": datetime.now()
        },
        "customer": customer,
        "settings": settings,
        "timedelta": timedelta
    }
    
    if request.output_format == 'docx':
        file_bytes = document_service.generate_budget_docx(budget_data, "temp/budget.docx")
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        file_extension = "docx"
    else: # O padrão é PDF
        file_bytes = document_service.generate_budget_pdf(budget_data)
        media_type = "application/pdf"
        file_extension = "pdf"

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=orcamento.{file_extension}"}
    )