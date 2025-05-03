"""
Chat API endpoints for the TripHelix application.
This module handles the chat functionality, including streaming responses from the AI model.
"""

# Import necessary FastAPI components and utilities
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from openai import OpenAI
from app.core.ai_config import ai_config

# Initialize the router for chat endpoints
router = APIRouter()

# Initialize the OpenAI client with the API key from configuration
client = OpenAI(api_key=ai_config.OPENAI_API_KEY)

# In-memory storage for chat history, organized by session ID
# This is a simple implementation - in production, consider using a database
chat_history: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    """
    Pydantic model for chat request validation.
    
    Attributes:
        message (str): The user's message to be processed by the AI
        session_id (Optional[str]): Unique identifier for the chat session
    """
    message: str
    session_id: Optional[str] = None

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Endpoint for streaming chat responses.
    This endpoint processes user messages and streams the AI's response in real-time.
    
    Args:
        request (ChatRequest): The chat request containing the message and optional session ID
        
    Returns:
        StreamingResponse: A response that streams the AI's response token by token
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Use provided session ID or default to "default_session"
        session_id = request.session_id or "default_session"
        
        # Initialize chat history for new sessions
        if session_id not in chat_history:
            chat_history[session_id] = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ]
        
        # Add user message to chat history
        chat_history[session_id].append({"role": "user", "content": request.message})

        # Create a streaming response from OpenAI
        response_stream = client.chat.completions.create(
            model=ai_config.OPENAI_MODEL,
            messages=chat_history[session_id],
            temperature=ai_config.OPENAI_TEMPERATURE,
            max_tokens=ai_config.OPENAI_MAX_TOKENS,
            stream=True,
        )

        async def event_generator():
            """
            Generator function that yields the AI's response token by token.
            Also accumulates the full response for history.
            
            Yields:
                str: Individual tokens from the AI's response
            """
            full_reply = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    if content and content.strip():  # Only process non-empty content
                        full_reply += content
                        yield content
            
            # Save the complete response to chat history after streaming is done
            chat_history[session_id].append({
                "role": "assistant",
                "content": full_reply
            })

        # Return the streaming response with plain text media type
        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))
