from fastapi import APIRouter, Depends


router = APIRouter()


@router.get("/")
async def read_reviews():
    return {"message": "Hello, World!"}

