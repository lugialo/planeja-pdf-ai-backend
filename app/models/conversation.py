from sqlalchemy import Column, String, DateTime, ForeignKey, func
from database import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id'), index=True)
    prompt = Column(String)
    response = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())