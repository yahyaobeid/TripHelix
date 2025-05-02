from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from openai import OpenAI
from app.core.ai_config import ai_config

router = APIRouter()
client = OpenAI(api_key=ai_config.OPENAI_API_KEY)

chat_history: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        session_id = request.session_id or "default_session"
        if session_id not in chat_history:
            chat_history[session_id] = [
                {"role": "system", "content": "You are a helpful AI assistant."}
            ]
        chat_history[session_id].append({"role": "user", "content": request.message})

        response_stream = client.chat.completions.create(
            model=ai_config.OPENAI_MODEL,
            messages=chat_history[session_id],
            temperature=ai_config.OPENAI_TEMPERATURE,
            max_tokens=ai_config.OPENAI_MAX_TOKENS,
            stream=True,
        )

        async def event_generator():
            full_reply = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    for chunk in response_stream:
                        # content = chunk.choices[0].delta.content
                        # if not content:
                            # continue
                        full_reply += chunk.choices[0].delta.content or ''
                        yield chunk.choices[0].delta.content or ''
            
            # Only save to history after streaming is complete
            chat_history[session_id].append({
                "role": "assistant",
                "content": full_reply
            })

        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
