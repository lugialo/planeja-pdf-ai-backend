from pydantic import BaseModel, ConfigDict
from typing import Optional

class CustomerResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    

    model_config = ConfigDict(from_attributes=True)