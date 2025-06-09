from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from models.external_data import ExternalUser

from models.external_data import ExternalBudget, ExternalProduct, ExternalCategory, BudgetStatusEnum

def get_sales_trends_data(db: Session, user_id: str, days_to_analyze: int = 30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_analyze)

    # Agrega dados gerais sobre orçamentos aprovados no período definido pelo parâmetro days_to_analyze
    approved_budgets_summary = db.query(
        func.count(ExternalBudget.id).label("count"),
        func.sum(ExternalBudget.total).label("total_value"),
        func.avg(ExternalBudget.total).label("average_value")
    ).filter(
        ExternalBudget.userId == user_id,
        ExternalBudget.status == BudgetStatusEnum.Aceito.value,
        ExternalBudget.createdAt >= start_date,
        ExternalBudget.createdAt <= end_date
    ).first()
    
    # Encontra as categorias mais populares em orçamentos aprovados.
    
    top_categories = db.query(
        ExternalCategory.name,
        func.count(ExternalCategory.id).label("category_count")
    ).join(
        ExternalBudget, ExternalCategory.budgetId == ExternalBudget.id
    ).filter(
        ExternalBudget.userId == user_id,
        ExternalBudget.status == BudgetStatusEnum.Aceito.value,
        ExternalBudget.createdAt >= start_date
    ).group_by(
        ExternalCategory.name
    ).order_by(
        func.count(ExternalCategory.id).desc()
    ).limit(5).all()
    
    # Encontra os produtos mais populares
    top_products = db.query(
        ExternalProduct.name,
        func.count(ExternalProduct.id).label("product_count")
    ).join(
        ExternalCategory, ExternalProduct.categoryId == ExternalCategory.id
    ).join(
        ExternalBudget, ExternalCategory.budgetId == ExternalBudget.id
    ).filter(
        ExternalBudget.userId == user_id,
        ExternalBudget.status == BudgetStatusEnum.Aceito.value,
        ExternalBudget.createdAt >= start_date
    ).group_by(
        ExternalProduct.name
    ).order_by(
        func.count(ExternalProduct.id).desc()
    ).limit(5).all()

    user_name = db.query(ExternalUser.name).filter(ExternalUser.id == user_id).scalar()
    
    return {
        "user_id": user_id,
        "user_name": user_name,
        "period_days": days_to_analyze,
        "summary": {
            "approved_budgets_count": approved_budgets_summary.count or 0,
            "total_sales_value": approved_budgets_summary.total_value or 0,
            "average_budget_value": approved_budgets_summary.average_value or 0
        },
        "top_categories": [{"name": name, "count": count} for name, count in top_categories],
        "top_products": [{"name": name, "count": count} for name, count in top_products]
    }