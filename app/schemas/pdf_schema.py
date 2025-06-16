from pydantic import BaseModel
from typing import Literal

class BudgetGenerationRequest(BaseModel):
    customer_id: str
    user_id: str
    description: str
    output_format: Literal['pdf', 'docx'] = 'pdf'