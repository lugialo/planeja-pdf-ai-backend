from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import re
import logging
from app.models.external_data import (
    ExternalBudget, ExternalCustomer, ExternalCategory, 
    ExternalProduct, ExternalUser, BudgetStatusEnum
)

# Configurar logging
logger = logging.getLogger(__name__)

class DataContextService:
    """Serviço para analisar prompts e buscar dados relevantes do banco"""
    
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
    
    def analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analisa o prompt para identificar que tipo de dados são necessários"""
        prompt_lower = prompt.lower()
        logger.info(f"Analisando prompt: {prompt_lower}")
        
        intent = {
            'needs_budgets': False,
            'needs_customers': False,
            'needs_categories': False,
            'needs_products': False,
            'time_period': None,
            'status_filter': None,
            'analysis_type': None
        }
        
        # Palavras-chave para orçamentos
        budget_keywords = [
            'orçamento', 'orçamentos', 'budget', 'budgets', 'vendas', 'faturamento',
            'receita', 'valor', 'total', 'aprovado', 'aceito', 'negado', 'pendente',
            'gerou', 'gerei', 'criou', 'criado', 'made', 'created', 'generated',
            'quantos', 'quanto', 'how many', 'how much', 'count', 'número'
        ]
        
        # Palavras-chave para clientes
        customer_keywords = [
            'cliente', 'clientes', 'customer', 'customers', 'comprador', 'compradores'
        ]
        
        # Palavras-chave para categorias
        category_keywords = [
            'categoria', 'categorias', 'category', 'categories', 'tipo', 'tipos'
        ]
        
        # Palavras-chave para produtos
        product_keywords = [
            'produto', 'produtos', 'product', 'products', 'item', 'itens'
        ]
        
        # Palavras-chave para períodos de tempo
        time_keywords = {
            'mês': 30,
            'mes': 30,
            'month': 30,
            'semana': 7,
            'week': 7,
            'ano': 365,
            'year': 365,
            'trimestre': 90,
            'quarter': 90
        }
        
        # Palavras-chave para status
        status_keywords = {
            'aprovado': BudgetStatusEnum.Aceito,
            'aceito': BudgetStatusEnum.Aceito,
            'accepted': BudgetStatusEnum.Aceito,
            'negado': BudgetStatusEnum.Negado,
            'rejected': BudgetStatusEnum.Negado,
            'pendente': BudgetStatusEnum.Pendente,
            'pending': BudgetStatusEnum.Pendente
        }
        
        # Palavras-chave para tipos de análise
        analysis_keywords = {
            'predição': 'prediction',
            'predicao': 'prediction',
            'prediction': 'prediction',
            'previsão': 'forecast',
            'previsao': 'forecast',
            'forecast': 'forecast',
            'tendência': 'trend',
            'tendencia': 'trend',
            'trend': 'trend',
            'comparação': 'comparison',
            'comparacao': 'comparison',
            'comparison': 'comparison'
        }
        
        # Verificar necessidade de dados
        if any(keyword in prompt_lower for keyword in budget_keywords):
            intent['needs_budgets'] = True
            logger.info("Detectado: needs_budgets = True")
        
        if any(keyword in prompt_lower for keyword in customer_keywords):
            intent['needs_customers'] = True
            logger.info("Detectado: needs_customers = True")
            
        if any(keyword in prompt_lower for keyword in category_keywords):
            intent['needs_categories'] = True
            logger.info("Detectado: needs_categories = True")
            
        if any(keyword in prompt_lower for keyword in product_keywords):
            intent['needs_products'] = True
            logger.info("Detectado: needs_products = True")
        
        # Identificar período de tempo
        for time_word, days in time_keywords.items():
            if time_word in prompt_lower:
                intent['time_period'] = days
                logger.info(f"Detectado período: {time_word} = {days} dias")
                break
        
        # Identificar filtro de status
        for status_word, status_enum in status_keywords.items():
            if status_word in prompt_lower:
                intent['status_filter'] = status_enum
                logger.info(f"Detectado status: {status_word} = {status_enum}")
                break
        
        # Identificar tipo de análise
        for analysis_word, analysis_type in analysis_keywords.items():
            if analysis_word in prompt_lower:
                intent['analysis_type'] = analysis_type
                logger.info(f"Detectado análise: {analysis_word} = {analysis_type}")
                break
        
        logger.info(f"Intent final: {intent}")
        return intent
    
    def get_budget_data(self, time_period: Optional[int] = None, 
                       status_filter: Optional[BudgetStatusEnum] = None) -> Dict[str, Any]:
        """Busca dados de orçamentos"""
        try:
            logger.info(f"Buscando orçamentos para user_id: {self.user_id}")
            query = self.db.query(ExternalBudget).filter(ExternalBudget.userId == self.user_id)
            
            if time_period:
                start_date = datetime.now() - timedelta(days=time_period)
                query = query.filter(ExternalBudget.createdAt >= start_date)
                logger.info(f"Filtro de período: últimos {time_period} dias (desde {start_date})")
            
            if status_filter:
                query = query.filter(ExternalBudget.status == status_filter)
                logger.info(f"Filtro de status: {status_filter}")
            
            budgets = query.all()
            logger.info(f"Encontrados {len(budgets)} orçamentos")
            
            # Estatísticas básicas
            total_count = len(budgets)
            total_value = sum(budget.total for budget in budgets)
            avg_value = total_value / total_count if total_count > 0 else 0
            
            # Agrupamento por status
            status_summary = {}
            for status in BudgetStatusEnum:
                count = len([b for b in budgets if b.status == status])
                value = sum(b.total for b in budgets if b.status == status)
                status_summary[status.value] = {'count': count, 'total_value': value}
            
            result = {
                'budgets': [
                    {
                        'id': b.id,
                        'name': b.name,
                        'status': b.status.value,
                        'total': b.total,
                        'created_at': b.createdAt.isoformat() if b.createdAt else None,
                        'customer_id': b.customerId
                    } for b in budgets
                ],
                'summary': {
                    'total_count': total_count,
                    'total_value': total_value,
                    'average_value': avg_value,
                    'by_status': status_summary
                }
            }
            
            logger.info(f"Resumo dos dados: {result['summary']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de orçamentos: {e}")
            return {
                'budgets': [],
                'summary': {
                    'total_count': 0,
                    'total_value': 0,
                    'average_value': 0,
                    'by_status': {}
                }
            }
    
    def get_customer_data(self) -> Dict[str, Any]:
        """Busca dados de clientes"""
        customers = self.db.query(ExternalCustomer).filter(
            ExternalCustomer.userId == self.user_id
        ).all()
        
        return {
            'customers': [
                {
                    'id': c.id,
                    'name': c.name,
                    'email': c.email,
                    'phone': c.phone,
                    'address': c.address
                } for c in customers
            ],
            'summary': {
                'total_customers': len(customers)
            }
        }
    
    def get_category_data(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """Busca dados de categorias com estatísticas"""
        query = self.db.query(
            ExternalCategory.name,
            func.count(ExternalCategory.id).label('count'),
            func.sum(ExternalBudget.total).label('total_value')
        ).join(
            ExternalBudget, ExternalCategory.budgetId == ExternalBudget.id
        ).filter(
            ExternalBudget.userId == self.user_id
        )
        
        if time_period:
            start_date = datetime.now() - timedelta(days=time_period)
            query = query.filter(ExternalBudget.createdAt >= start_date)
        
        categories = query.group_by(ExternalCategory.name).all()
        
        return {
            'categories': [
                {
                    'name': cat.name,
                    'budget_count': cat.count,
                    'total_value': float(cat.total_value or 0)
                } for cat in categories
            ],
            'summary': {
                'total_categories': len(categories)
            }
        }
    
    def get_product_data(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """Busca dados de produtos com estatísticas"""
        query = self.db.query(
            ExternalProduct.name,
            ExternalProduct.price,
            ExternalCategory.name.label('category_name'),
            func.count(ExternalProduct.id).label('usage_count')
        ).join(
            ExternalCategory, ExternalProduct.categoryId == ExternalCategory.id
        ).join(
            ExternalBudget, ExternalCategory.budgetId == ExternalBudget.id
        ).filter(
            ExternalBudget.userId == self.user_id
        )
        
        if time_period:
            start_date = datetime.now() - timedelta(days=time_period)
            query = query.filter(ExternalBudget.createdAt >= start_date)
        
        products = query.group_by(
            ExternalProduct.name, ExternalProduct.price, ExternalCategory.name
        ).all()
        
        return {
            'products': [
                {
                    'name': prod.name,
                    'price': float(prod.price),
                    'category': prod.category_name,
                    'usage_count': prod.usage_count
                } for prod in products
            ],
            'summary': {
                'total_products': len(products)
            }
        }
    
    def build_context_for_ai(self, prompt: str) -> str:
        """Constrói o contexto completo baseado no prompt"""
        logger.info(f"Construindo contexto para prompt: {prompt}")
        intent = self.analyze_prompt_intent(prompt)
        
        # Verifica se há necessidade de dados externos
        needs_external_data = any([
            intent['needs_budgets'], 
            intent['needs_customers'], 
            intent['needs_categories'], 
            intent['needs_products']
        ])
        
        # Se não precisa de dados externos, retorna contexto simples
        if not needs_external_data:
            logger.info("Nenhuma keyword de dados detectada, retornando contexto conversacional")
            return f"""Pergunta do usuário: {prompt}

Instruções:
- Você é um assistente de análise de negócios amigável
- Responda de forma natural e conversacional
- Se o usuário fizer uma saudação ou pergunta casual, responda normalmente
- Se precisar de dados específicos sobre orçamentos, clientes, produtos ou categorias, peça para o usuário ser mais específico
- Seja útil e educado em suas respostas"""
        
        # Se precisa de dados externos, constrói contexto completo
        context_parts = []
        context_parts.append(f"Pergunta do usuário: {prompt}")
        context_parts.append("\nDados disponíveis:")
        
        if intent['needs_budgets']:
            logger.info("Buscando dados de orçamentos...")
            budget_data = self.get_budget_data(
                time_period=intent['time_period'],
                status_filter=intent['status_filter']
            )
            context_parts.append("\n--- DADOS DE ORÇAMENTOS ---")
            context_parts.append(f"Total de orçamentos: {budget_data['summary']['total_count']}")
            context_parts.append(f"Valor total: R$ {budget_data['summary']['total_value']:,.2f}")
            context_parts.append(f"Valor médio: R$ {budget_data['summary']['average_value']:,.2f}")
            
            context_parts.append("\nResumo por status:")
            for status, data in budget_data['summary']['by_status'].items():
                context_parts.append(f"- {status}: {data['count']} orçamentos, R$ {data['total_value']:,.2f}")
        
        if intent['needs_customers']:
            logger.info("Buscando dados de clientes...")
            customer_data = self.get_customer_data()
            context_parts.append("\n--- DADOS DE CLIENTES ---")
            context_parts.append(f"Total de clientes: {customer_data['summary']['total_customers']}")
        
        if intent['needs_categories']:
            logger.info("Buscando dados de categorias...")
            category_data = self.get_category_data(time_period=intent['time_period'])
            context_parts.append("\n--- DADOS DE CATEGORIAS ---")
            context_parts.append("Top categorias por valor:")
            sorted_cats = sorted(category_data['categories'], 
                               key=lambda x: x['total_value'], reverse=True)[:5]
            for cat in sorted_cats:
                context_parts.append(f"- {cat['name']}: {cat['budget_count']} orçamentos, R$ {cat['total_value']:,.2f}")
        
        if intent['needs_products']:
            logger.info("Buscando dados de produtos...")
            product_data = self.get_product_data(time_period=intent['time_period'])
            context_parts.append("\n--- DADOS DE PRODUTOS ---")
            context_parts.append("Top produtos por uso:")
            sorted_prods = sorted(product_data['products'], 
                                key=lambda x: x['usage_count'], reverse=True)[:5]
            for prod in sorted_prods:
                context_parts.append(f"- {prod['name']}: R$ {prod['price']:,.2f}, usado {prod['usage_count']} vezes")
        
        context_parts.append("\nInstruções IMPORTANTES:")
        context_parts.append("- Você é um assistente de análise de negócios")
        context_parts.append("- Responda baseado nos dados fornecidos acima")
        context_parts.append("- Se os dados mostram 0 orçamentos, diga isso claramente")
        context_parts.append("- Se houver dados, seja específico nos números")
        context_parts.append("- Formate números em português brasileiro (R$ 1.234,56)")
        context_parts.append("- Seja analítico e dê insights sobre os dados")
        
        if intent['analysis_type'] == 'prediction':
            context_parts.append("- O usuário quer uma predição/previsão. Use os dados históricos para fazer projeções realistas")
        elif intent['analysis_type'] == 'forecast':
            context_parts.append("- O usuário quer uma previsão. Analise tendências nos dados históricos")
        elif intent['analysis_type'] == 'trend':
            context_parts.append("- O usuário quer análise de tendências. Compare períodos e identifique padrões")
        
        final_context = "\n".join(context_parts)
        logger.info(f"Contexto final construído com {len(context_parts)} seções")
        logger.debug(f"Contexto completo:\n{final_context}")
        
        return final_context
