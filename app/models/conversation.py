from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    prompt = Column(String)
    response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)