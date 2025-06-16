# app/models/external_data.py
import enum
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey, Enum as SAEnum, 
    Boolean, Integer, Text
)
from sqlalchemy.orm import relationship
from database import ExternalBase

class BudgetStatusEnum(str, enum.Enum):
    Enviado = "Enviado"
    Pendente = "Pendente"
    Aceito = "Aceito"
    Negado = "Negado"

class PaymentStatusEnum(str, enum.Enum):
    Pending = "Pending"
    Completed = "Completed"
    Failed = "Failed"
    Cancelled = "Cancelled"

class PlanIntervalEnum(str, enum.Enum):
    Monthly = "Monthly"
    Yearly = "Yearly"

class SubscriptionStatusEnum(str, enum.Enum):
    Active = "Active"
    Cancelled = "Cancelled"
    Expired = "Expired"
    Trial = "Trial"


class ExternalUser(ExternalBase):
    __tablename__ = "User"
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text)
    email = Column(Text)
    emailVerified = Column(DateTime)
    image = Column(Text)
    stripeCustomerId = Column(Text)
    stripeSubscriptionId = Column(Text)
    stripeSubscriptionStatus = Column(Text)
    stripePriceId = Column(Text)
    
    budgets = relationship("ExternalBudget", back_populates="user", foreign_keys="[ExternalBudget.userId]")
    customers = relationship("ExternalCustomer", back_populates="user", foreign_keys="[ExternalCustomer.userId]")
    subscriptions = relationship("ExternalSubscription", back_populates="user", foreign_keys="[ExternalSubscription.userId]")
    settings = relationship("ExternalSettings", back_populates="user", foreign_keys="[ExternalSettings.userId]", uselist=False)
    
class ExternalCustomer(ExternalBase):
    __tablename__ = "Customer"
    __table_args__ = {'schema': 'public'}
    
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)
    email = Column(Text)
    birthdate = Column(DateTime)
    userId = Column(Text, ForeignKey('public.User.id'), nullable=False)
    address = Column(Text)
    cnpj = Column(Text)
    cpf = Column(Text)
    
    user = relationship("ExternalUser", back_populates="customers")
    budgets = relationship("ExternalBudget", back_populates="customer", foreign_keys="[ExternalBudget.customerId]")

class ExternalBudget(ExternalBase):
    __tablename__ = "Budget"
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    status = Column(SAEnum(BudgetStatusEnum), nullable=False)
    userId = Column(Text, ForeignKey('public.User.id'), nullable=False)
    customerId = Column(Text, ForeignKey('public.Customer.id'))
    createdAt = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    updatedAt = Column(DateTime, nullable=False)
    shippingDate = Column(DateTime)
    validateDate = Column(DateTime)
    total = Column(Float, nullable=False)

    user = relationship("ExternalUser", back_populates="budgets")
    customer = relationship("ExternalCustomer", back_populates="budgets")
    categories = relationship("ExternalCategory", back_populates="budget", foreign_keys="[ExternalCategory.budgetId]")

class ExternalCategory(ExternalBase):
    __tablename__ = "Category" 
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    budgetId = Column(Text, ForeignKey('public.Budget.id'), nullable=False)

    budget = relationship("ExternalBudget", back_populates="categories")
    products = relationship("ExternalProduct", back_populates="category", foreign_keys="[ExternalProduct.categoryId]")

class ExternalProduct(ExternalBase):
    __tablename__ = "Product"
    __table_args__ = {'schema': 'public'}

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    categoryId = Column(Text, ForeignKey('public.Category.id'), nullable=False)

    category = relationship("ExternalCategory", back_populates="products")
class ExternalSubscription(ExternalBase):
    __tablename__ = "Subscription"
    __table_args__ = {'schema': 'public'}
    
    id = Column(Text, primary_key=True)
    userId = Column(Text, ForeignKey('public.User.id'), nullable=False)
    planId = Column(Text, ForeignKey('public.Plan.id'), nullable=False)
    stripeSubscriptionId = Column(Text)
    status = Column(SAEnum(SubscriptionStatusEnum), nullable=False)
    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime)
    cancelAtPeriodEnd = Column(Boolean, nullable=False, default=False)
    
    user = relationship("ExternalUser", back_populates="subscriptions")
    payments = relationship("ExternalPayment", back_populates="subscription")

class ExternalPayment(ExternalBase):
    __tablename__ = "Payment"
    __table_args__ = {'schema': 'public'}
    
    id = Column(Text, primary_key=True)
    subscriptionId = Column(Text, ForeignKey('public.Subscription.id'), nullable=False)
    amount = Column(Float, nullable=False)
    paymentDate = Column(DateTime, nullable=False)
    status = Column(SAEnum(PaymentStatusEnum), nullable=False)
    stripePaymentId = Column(Text)
    
    subscription = relationship("ExternalSubscription", back_populates="payments")

class ExternalSettings(ExternalBase):
    __tablename__ = "Settings"
    __table_args__ = {'schema': 'public'}
    
    id = Column(Text, primary_key=True)
    userId = Column(Text, ForeignKey('public.User.id'), nullable=False)
    companyName = Column(Text, nullable=False)
    cnpj = Column(Text, nullable=False)
    street = Column(Text, nullable=False)
    number = Column(Integer, nullable=False)
    zipCode = Column(Text, nullable=False)
    state = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    phone = Column(Text, nullable=False)
    responsiblePerson = Column(Text, nullable=False)
    createdAt = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP")
    updatedAt = Column(DateTime, nullable=False)
    logo = Column(Text)
    budgetValidityDays = Column(Integer)
    deliveryTimeDays = Column(Integer)
    observation = Column(Text)
    paymentMethod = Column(Text)
    neighborhood = Column(Text)
    
    user = relationship("ExternalUser", back_populates="settings")