import streamlit as st
import requests

# Configuração da URL do backend
API_URL = "http://localhost:8000/api/v1/chat"

# Configuração da interface
st.set_page_config(page_title="Chatbot GPT-4o", page_icon="💬")

# Estilização da interface
st.title("🤖 Chatbot com GPT-4o")
st.write("Digite sua pergunta abaixo e o chatbot responderá.")

# Campo de entrada do usuário
question = st.text_input("Pergunta:", placeholder="Digite sua dúvida aqui...")

# Botão de envio
if st.button("Enviar"):
    if question:
        # Faz a requisição para o backend FastAPI
        response = requests.post(API_URL, json={"question": question})
        
        # Exibe a resposta do chatbot
        if response.status_code == 200:
            st.success("Resposta do Chatbot:")
            st.write(response.json()["answer"])
        else:
            st.error("Erro ao conectar com a API.")
