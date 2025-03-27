from fastapi import APIRouter

router = APIRouter()


@router.post("/chat/", tags=["chat"])
async def chat():
    return {"message": "Hello, World!"}
