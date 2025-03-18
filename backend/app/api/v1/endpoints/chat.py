from fastapi import APIRouter, HTTPException
from app.core.llm import get_gpt_response  
from app.schemas.chat import ChatRequest, ChatResponse  

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = get_gpt_response(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
