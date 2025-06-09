from sqlalchemy import Column, String, Integer, Enum, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from database import ExternalBase

# Tabela Budget, do banco externo
class Budget(ExternalBase):
    __tablename__ = 'Budget'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    customerId = Column(String, ForeignKey('Customer.id'), nullable=True)
    userId = Column(String, ForeignKey('User.id'), nullable=False)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)
    shippingDate = Column(DateTime, nullable=True)
    validateDate = Column(DateTime, nullable=True)
    total = Column(Float, nullable=False)
    
    categories = relationship("Category", back_populates="budget")
    user = relationship("User", back_populates="budgets")
    
class StatusBudget(enum.Enum):
    PENDENTE = 'Pendente'
    APROVADO = 'Aprovado'
    CONCLUIDO = 'CONCLUIDO'
    CANCELADO = 'CANCELADO'

# Tabela Category, do banco externo
class Category(ExternalBase):
    __tablename__ = 'Category'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    budgetId = Column(String, ForeignKey('Budget.id'), nullable=False)
    
    products = relationship("Product", back_populates="category")
    budget = relationship("Budget", back_populates="categories")

# Tabela Product, do banco externo
class Product(ExternalBase):
    __tablename__ = 'Product'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    budgetId = Column(String, ForeignKey('Budget.id'), nullable=False)
    categoryId = Column(String, ForeignKey('Category.id'), nullable=False)
    
    category = relationship("Category", back_populates="products")

# Tabela Customer, do banco externo
class Customer(ExternalBase):
    __tablename__ = 'Customer'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    birthdate = Column(DateTime, nullable=True)
    userId = Column(String, ForeignKey('User.id'), nullable=False)
    address = Column(String, nullable=False)
    cnpj = Column(String, nullable=True)
    cpf = Column(String, nullable=True)

# Tabela User, do banco externo
class User(ExternalBase):
    __tablename__ = 'User'

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    emailVerified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    stripeCustomerId = Column(String, nullable=True)
    stripeSubscriptionId = Column(String, nullable=True)
    stripeSubscriptionStatus = Column(String, nullable=True)
    stripePriceId = Column(String, nullable=True)
    
    budgets = relationship("Budget", back_populates="user")
