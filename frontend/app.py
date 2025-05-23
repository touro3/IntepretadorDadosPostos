from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai

load_dotenv()
app = Flask(__name__)

# Define a chave da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente útil e simpático."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Erro ao conectar com a OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
