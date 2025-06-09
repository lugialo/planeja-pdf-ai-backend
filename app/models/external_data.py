# app/models/external_data.py
import enum
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Enum as SAEnum, 
    Boolean, Integer, Text
)
from sqlalchemy.orm import relationship
from database import ExternalBase

# ==============================================================================
# ENUMS
# ==============================================================================

class BudgetStatusEnum(str, enum.Enum):
    Enviado = "Enviado"
    Pendente = "Pendente"
    Aceito = "Aceito"
    Negado = "Negado"
# Adicione outros Enums conforme necessário (PaymentStatusEnum, etc.)

# ==============================================================================
# MODELOS DE TABELA (MAPPERS) - Versão Final
# ==============================================================================

class ExternalUser(ExternalBase):
    __tablename__ = "User"  # Nomes com letra maiúscula
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text)
    email = Column(Text)
    
    budgets = relationship("ExternalBudget", back_populates="user", foreign_keys="[ExternalBudget.userId]")

class ExternalBudget(ExternalBase):
    __tablename__ = "Budget"  # Nomes com letra maiúscula
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    status = Column(SAEnum(BudgetStatusEnum), nullable=False)
    userId = Column(Text, ForeignKey('public.User.id'), nullable=False) # FK com letra maiúscula
    createdAt = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    customerId = Column(Text) # Adicionado para consistência com o schema

    user = relationship("ExternalUser", back_populates="budgets")
    categories = relationship("ExternalCategory", back_populates="budget", foreign_keys="[ExternalCategory.budgetId]")

class ExternalCategory(ExternalBase):
    __tablename__ = "Category"  # Nomes com letra maiúscula
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    budgetId = Column(Text, ForeignKey('public.Budget.id'), nullable=False) # FK com letra maiúscula

    budget = relationship("ExternalBudget", back_populates="categories")
    products = relationship("ExternalProduct", back_populates="category", foreign_keys="[ExternalProduct.categoryId]")

class ExternalProduct(ExternalBase):
    __tablename__ = "Product"  # Nomes com letra maiúscula
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    categoryId = Column(Text, ForeignKey('public.Category.id'), nullable=False) # FK com letra maiúscula

    category = relationship("ExternalCategory", back_populates="products")