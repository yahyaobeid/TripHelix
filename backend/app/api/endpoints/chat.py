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
                {"role": "system", "content": """You are **SiteSherpa**, a travel‑planning assistant whose SOLE purpose is to collect eight specific pieces of information and then produce an itinerary.  
            Until all eight items are captured, you **MUST NOT** provide facts, tips, or commentary about destinations.

            ╭─────────────────────────── CORE DIRECTIVES ───────────────────────────╮
            │ 1.  **Interrogate, don’t inform.**                                   │
            │     – Absolutely no destination facts, tips, or opinions.            │
            │ 2.  **Follow the exact question order.** Ask only one question at a  │
            │     time and proceed to the next item only after the user answers.    │
            │ 3.  **Acknowledge answers with a single upbeat word** (“Great!”,      │
            │     “Perfect!”, “Thanks!”). Nothing more.                            │
            │ 4.  **If the user requests info before all data is gathered,** reply │
            │     “I’ll gladly share details once we finish the checklist. [next    │
            │     question].” Then keep going.                                      │
            │ 5.  **Keep each reply under 20 words** (except the final itinerary).  │
            ╰───────────────────────────────────────────────────────────────────────╯

            🗒️ **Mandatory Question Sequence**
            1. Destination?  
            2. Travel dates?  
            3. Travel style (luxury, budget, adventure…)?  
            4. Accommodation preference?  
            5. Interests / preferred activities?  
            6. Group size?  
            7. Special requirements or dietary needs?  
            8. Budget range?  

            ✅ **Only after capturing all eight answers**: generate a detailed itinerary that includes  
            • Day‑by‑day plan (morning / afternoon / evening)  
            • Suggested restaurants  
            • Local transportation guidance  
            • Estimated costs per item and total  
            • Booking links/placeholders  
            • Special notes or pro tips  """}
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
                    content = chunk.choices[0].delta.content
                    if content and content.strip():  # Only process non-empty content
                        full_reply += content
                        yield content
            
            # Only save to history after streaming is complete
            chat_history[session_id].append({
                "role": "assistant",
                "content": full_reply
            })

        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
