from pydantic import BaseModel
from typing import Dict, Any

class DocumentResponse(BaseModel):
    status: str
    extracted_text: str
    parsed_data: Dict[str, Any]


