from pydantic import BaseModel


class RespostaBot(BaseModel):
    resposta: str


class PerguntaBot(BaseModel):
    pergunta: str


class ETLResponse(BaseModel):
    status: str = "Realizado"
