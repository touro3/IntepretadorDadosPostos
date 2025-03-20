from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Modelo para requisição de chat"""

    question: str


class ChatResponse(BaseModel):
    """Modelo para resposta do chat"""

    answer: str
