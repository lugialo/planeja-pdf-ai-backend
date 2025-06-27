from pydantic import BaseModel
from datetime import datetime

class PromptRequest(BaseModel):
    session_id: str
    prompt: str

class SessionBase(BaseModel):
    id: str
    title: str
    created_at: datetime
    
class CreateSessionRequest(BaseModel):
    user_id: str
    first_prompt: str

class CreateSessionResponse(BaseModel):
    session_id: str
    title: str
    first_response: str

class ConversationResponse(BaseModel):
    prompt: str
    response: str
    created_at: datetime

class SessionResponse(SessionBase):
    conversations: list[ConversationResponse]