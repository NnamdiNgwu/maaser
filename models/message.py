from pydantic import BaseModel
from typing import Dict, Any

class Message(BaseModel):
    sender: str
    receiver: str
    action: str
    data: Dict[str, Any]