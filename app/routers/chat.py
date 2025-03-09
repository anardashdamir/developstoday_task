from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service
from typing import List

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Chat endpoint for the cocktail advisor.
    
    Args:
        request: The chat request containing conversation history
        
    Returns:
        Chat response with assistant's message and relevant sources
    """
    # Get the last user message
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user message found in the request")
    
    last_user_message = user_messages[-1].content
    

    response_text, sources = await rag_service.process_query(request.user_id, last_user_message)
    
    # Format the response
    return ChatResponse(
        message=ChatMessage(role="assistant", content=response_text),
        sources=sources
    )


@router.get("/chat/history/{user_id}", response_model=List[ChatMessage])
async def get_chat_history(user_id: str):
    """
    Get chat history for a specific user.
    
    In a production app, you'd implement persistent storage for chat history.
    For this example, we'll return an empty list.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        List of chat messages in the conversation history
    """

    return []