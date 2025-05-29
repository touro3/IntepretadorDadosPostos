from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

chat_sessions = {}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    user_message = data.get("message", "")

    try:
        if session_id not in chat_sessions:
            # Defina aqui a instrução de sistema (contexto inicial)
            instrucao_do_sistema = (
                "Voce é o melhor programador do mundo" \
                "sabe fazer tudo que envolve progrmação"
                
            ) # Exemplo de instrução

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest", # Ou o modelo que você está usando (ex: "gemini-1.5-flash-latest")
                system_instruction=instrucao_do_sistema
            )
            chat_sessions[session_id] = model.start_chat()

        chat = chat_sessions[session_id]
        response = chat.send_message(user_message)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Erro com Gemini: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)