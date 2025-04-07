from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from src.ai_information_data.services import monitor_service


class TodoUrlReq(BaseModel):
    source: int
    status: int


api_aid = APIRouter()


@api_aid.post("/test")
async def test(req: TodoUrlReq):
    logger.info('req is: {}'.format(req))
    await monitor_service()
    return {"message": "Hello World"}
