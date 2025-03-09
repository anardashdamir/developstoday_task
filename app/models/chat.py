from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: Optional[str] = "default_user"  # To track user sessions/preferences


class ChatResponse(BaseModel):
    message: ChatMessage
    sources: Optional[List[Dict[str, Any]]] = None  # For providing source cocktail info


class UserMemory(BaseModel):
    user_id: str
    favorite_ingredients: List[str] = []
    favorite_cocktails: List[str] = []
    timestamp: Optional[str] = None