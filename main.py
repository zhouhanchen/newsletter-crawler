from fastapi import FastAPI
from ai_information_data.api import api_aid
from tortoise.contrib.fastapi import register_tortoise
from settings.settings import TORTOISE_ORM
from loguru import logger as log
from utils import redis_utils
from job import retry_job

app = FastAPI()

log.info("Starting FastAPI application...")

# log.info('flush db...')
#
# redis_utils.flush_db()


app.include_router(api_aid, prefix='/aid', tags=['information_data'])

register_tortoise(app, config=TORTOISE_ORM)


@app.on_event("startup")
async def startup_event():
    log.info("Starting up init job...")
    retry_job.init_job()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3009)

