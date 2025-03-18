import openai
from app.core.config import settings

def get_gpt_response(question: str) -> str:
    """Envia uma pergunta ao modelo GPT-4o e retorna a resposta."""
    openai.api_key = settings.OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente especializado em fornecer insights para donos de postos de gasolina. "
                        "Suas respostas devem ser diretas, claras e focadas em dados operacionais, ajudando na tomada de decisão. "
                        "Seja objetivo e utilize métricas relevantes sempre que possível. "
                        "Exemplos de tópicos incluem: estoque de combustíveis, preços, concorrência, fluxo de vendas, margens de lucro e tendências de consumo. "
                        "Caso precise de dados específicos, peça as informações necessárias de maneira educada e eficiente."
                    ),
                },
                {"role": "user", "content": question}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Erro na API OpenAI: {str(e)}")
