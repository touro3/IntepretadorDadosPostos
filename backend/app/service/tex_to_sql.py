from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from dags.etl_s3_to_postgres import engine
from service.azure_openai import llm
from llama_index.core import SQLDatabase, Settings
from llama_index.core.prompts import PromptTemplate
from jinja2 import Environment, FileSystemLoader
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.embed_model = OpenAIEmbedding()


def consulta_com_sql_e_resposta(pergunta: str):
    env = Environment(loader=FileSystemLoader("prompts"))

    # 1) Renderiza apenas o txt2sql (que já precisa do `pergunta`)
    rendered_txt2sql = env.get_template("txt2sql.j2").render(pergunta=pergunta)
    prompt_sql = PromptTemplate(rendered_txt2sql)

    # Template como PromptTemplate
    prompt_resposta_template = PromptTemplate(
        """
        Você está respondendo a um dono de posto de combustíveis.
        Responda em português claro e direto à pergunta:
        {query_str}
        Com base na seguinte consulta SQL:
        {sql_query}
        E nos resultados abaixo:
        {context_str}
        """,
        prompt_type="sql_response_synthesis_v2",
    )

    # 3) Conecta no banco
    db = SQLDatabase(engine, include_tables=["postos"])

    # 4) Gera a consulta SQL (texto bruto)
    retriever = NLSQLRetriever(
        sql_database=db,
        text_to_sql_prompt=prompt_sql,
        tables=["postos"],
        llm=llm,
        return_raw=True,
    )
    sql_results = retriever.retrieve(pergunta)
    sql_query = sql_results[0].text.strip() if sql_results else ""

    # 5) Cria o engine com response_synthesis_prompt como string
    query_engine = NLSQLTableQueryEngine(
        sql_database=db,
        tables=["postos"],
        llm=llm,
        response_synthesis_prompt=prompt_resposta_template,  # Passa a string template
    )

    # 6) Executa a pergunta
    response = query_engine.query(pergunta)

    return {
        "pergunta": pergunta,
        "sql_query": sql_query,
        "sql_results": [r.text.strip() for r in sql_results],
        "resposta_natural": str(response),
    }


if __name__ == "__main__":
    pergunta = "Qual foi a média de preço?"
    resultado = consulta_com_sql_e_resposta(pergunta)
    print(f"💬 Resposta Natural: {resultado['resposta_natural']}")
