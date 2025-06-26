from sqlalchemy import Column, String, DateTime, func
from app.database import MainBase

class Session(MainBase):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key = True, index = True)
    user_id = Column(String, index = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String)