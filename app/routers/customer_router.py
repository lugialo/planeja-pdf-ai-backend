from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_platform_db
from app.models.external_data import ExternalCustomer
from app.schemas.customer_schema import CustomerResponse

router = APIRouter(prefix="/customers", tags=["Clientes"])

@router.get("/", response_model=List[CustomerResponse])
async def get_customers_by_user(
    user_id: str = Query(..., description="ID do usuário para buscar os clientes associados"),
    edb: Session = Depends(get_platform_db)
):
    """
    Retorna uma lista de todos os clientes vinculados a um user_id específico.
    """
    customers = edb.query(ExternalCustomer).filter(ExternalCustomer.userId == user_id).order_by(ExternalCustomer.name).all()
    
    return customers