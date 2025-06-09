from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta

from models.external_data import Budget, Product, Category, StatusBudget

def get_sales_trends_data(db: Session, user_id: str, days_to_analyze: int = 30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_analyze)

    # Agrega dados gerais sobre orçamentos aprovados no período definido pelo parâmetro days_to_analyze
    approved_budgets_summary = db.query(
        func.count(Budget.id).label("count"),
        func.sum(Budget.total).label("total_value"),
        func.avg(Budget.total).label("average_value")
    ).filter(
        Budget.userId == user_id,
        Budget.status == StatusBudget.APROVADO.value,
        Budget.createdAt >= start_date,
        Budget.createdAt <= end_date
    ).first()
    
    # Encontra as categorias mais populares em orçamentos aprovados.
    
    top_categories = db.query(
        Category.name,
        func.count(Category.id).label("category_count")
    ).join(
        Budget, Category.budgetId == Budget.id
    ).filter(
        Budget.userId == user_id,
        Budget.status == StatusBudget.APROVADO.value,
        Budget.createdAt >= start_date
    ).group_by(
        Category.name
    ).order_by(
        func.count(Category.id).desc()
    ).limit(5).all()
    
    # Encontra os produtos mais populares
    top_products = db.query(
        Product.name,
        func.count(Product.id).label("product_count")
    ).join(
        Category, Product.categoryId == Category.id
    ).join(
        Budget, Category.budgetId == Budget.id
    ).filter(
        Budget.userId == user_id,
        Budget.status == StatusBudget.APROVADO.value,
        Budget.createdAt >= start_date
    ).group_by(
        Product.name
    ).order_by(
        func.count(Product.id).desc()
    ).limit(5).all()
    
    return {
        "user_id": user_id,
        "period_days": days_to_analyze,
        "summary": {
            "approved_budgets_count": approved_budgets_summary.count or 0,
            "total_sales_value": approved_budgets_summary.total_value or 0,
            "average_budget_value": approved_budgets_summary.average_value or 0
        },
        "top_categories": [{"name": name, "count": count} for name, count in top_categories],
        "top_products": [{"name": name, "count": count} for name, count in top_products]
    }