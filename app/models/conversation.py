from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.database import MainBase
import uuid

class Conversation(MainBase):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('sessions.id'), index=True)
    prompt = Column(String)
    response = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())