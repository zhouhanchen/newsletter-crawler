from src.settings.models import TodoUrl, AiInformationData


async def get_todo_urls(source: int):
    return await TodoUrl.filter(status=0, source=source).all()
