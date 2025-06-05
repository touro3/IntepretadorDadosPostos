from fastapi import FastAPI
from config.models import RespostaBot, PerguntaBot, ETLResponse
from service.tex_to_sql import consulta_com_sql_e_resposta
from dags.etl_s3_to_postgres import postos_etl_flow

app = FastAPI(title="postos", root_path="/alfred/api")


@app.post("/pergunta", response_model=RespostaBot)
def indexacao(pergunta: PerguntaBot):
    resposta = consulta_com_sql_e_resposta(pergunta=pergunta.pergunta)
    return RespostaBot(resposta=resposta["resposta_natural"])


@app.post("/etl", response_model=ETLResponse)
def etl(data: str = "2025-03-24"):
    postos_etl_flow(data=data)
    return ETLResponse(status="Realizado")
