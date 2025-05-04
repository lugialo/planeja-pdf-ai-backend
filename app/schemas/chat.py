from pydantic import BaseModel
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str
    user_id: str
    
class ConversationResponse(BaseModel):
    prompt: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True