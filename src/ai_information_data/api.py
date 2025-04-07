from fastapi import APIRouter


api_aid = APIRouter()


@api_aid.get("/test")
async def test():
    return {"message": "Hello World"}
