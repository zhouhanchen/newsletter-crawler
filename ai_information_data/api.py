from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from ai_information_data.monitor_services import monitor_service
import ai_information_data.service as service
from utils import redis_utils as redis


class TodoUrlReq(BaseModel):
    source: int
    status: int


api_aid = APIRouter()


@api_aid.get("/hello")
async def hello():
    return {"message": "Hello World"}


@api_aid.post("/test")
async def test(req: TodoUrlReq):
    logger.info('req is: {}'.format(req))
    await monitor_service()
    return {"message": "Hello World"}


@api_aid.post("/todo_urls")
async def todo_urls(req: TodoUrlReq):
    v = redis.get_value('todo_urls')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('todo_urls', '1')
    logger.info('req is: {}'.format(req))
    service.todo_urls(req.source)
    redis.del_value('todo_urls')
    return {"message": "success"}


@api_aid.post("/retry")
async def retry(req: dict):
    v = redis.get_value('retry')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('retry', '1')
    logger.info('req is: {}'.format(req))
    service.retry(req['deep'], req['source'])
    redis.del_value('retry')
    return {"message": "success"}


@api_aid.post("/deep")
async def deep(req: dict):
    v = redis.get_value('deep')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('deep', '1')
    logger.info('req is: {}'.format(req))
    service.deep(req)
    redis.del_value('deep')
    return {"message": "success"}

