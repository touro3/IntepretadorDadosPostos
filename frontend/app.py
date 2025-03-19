import streamlit as st
import time

# Configuração da interface
st.set_page_config(page_title="Chatbot GPT-4o", page_icon="💬")

st.title("🤖 Chatbot com GPT-4o")
st.write("Digite sua pergunta abaixo e o chatbot responderá.")

# Campo de entrada do usuário
question = st.text_input("Pergunta:", placeholder="Digite sua dúvida aqui...")

# Botão de envio
if st.button("Enviar"):
    if question:
        st.success("Resposta do Chatbot:")
        
        # Aqui, futuramente, será feita a chamada para a API
        resposta = "Resposta gerada pelo chatbot será exibida aqui quando a API estiver integrada."
        
        # Simula o streaming da resposta
        response_container = st.empty()
        response_text = ""
        
        for palavra in resposta.split():
            response_text += palavra + " "
            response_container.markdown(response_text)  # Atualiza o texto dinamicamente
            time.sleep(0.07)  # Pequeno delay para efeito de digitação
