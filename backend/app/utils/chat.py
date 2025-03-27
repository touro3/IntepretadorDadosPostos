from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core import SQLDatabase
from sqlalchemy import create_engine, inspect
from llama_index.core import Settings
from app.service.azure_openai import llm, embedding
from app.config.properties import POSTGRES_URI
from llama_index.core import PromptTemplate

Settings.llm = llm
Settings.embed_model = embedding

engine = create_engine(POSTGRES_URI)

template = PromptTemplate(
    """
Você é um executor de SQL do PostgreSQL. Sua tarefa é gerar um SQL válido e retornar o resultado da consulta de execução que responde à seguinte pergunta usando o esquema de banco de dados fornecido, depois executar essa consulta no banco de dados e retornar somente o resultado da consulta.
Insira aspas duplas ao redor dos nomes das colunas e das tabelas.
{schema}

Pergunta do usuário:
{query_str}
"""
)

inspector = inspect(engine)
columns = inspector.get_columns("gasprices")
schema_info = "Table 'titanic':\n"
for col in columns:
    schema_info += f" - {col['name']} ({col['type']})\n"

sql_database = SQLDatabase(engine=engine, include_tables=["gasprices"])

final_template = template.partial_format(schema=schema_info)

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["gasprices"],
    llm=llm,
    text_to_sql_prompt=final_template,
    verbose=True,
)

response = query_engine.query(
    "Quanto foi o preco mais alto de gasolina de cada estado?"
)

print(response)
