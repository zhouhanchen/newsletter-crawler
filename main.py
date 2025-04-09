from fastapi import FastAPI
from ai_information_data.api import api_aid
from tortoise.contrib.fastapi import register_tortoise
from settings.settings import TORTOISE_ORM

app = FastAPI()


app.include_router(api_aid, prefix='/aid', tags=['information_data'])

register_tortoise(app, config=TORTOISE_ORM)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3009)

