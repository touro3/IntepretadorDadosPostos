from fastapi import FastAPI
from app.api.v1.endpoints.chat import router as chat_router

app = FastAPI(title="Chatbot API", version="1.0")

# Registrar rotas
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
