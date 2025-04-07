from src.settings.models import TodoUrl, AiInformationData, MonitorSite
from datetime import datetime


async def get_todo_urls(source: int):
    return await TodoUrl.filter(status=0, source=source).all()


async def get_all_monitor_sites():
    return await MonitorSite.all()


async def get_monitor_site_by_url(url: str):
    return await MonitorSite.filter(site=url).first()


async def update_monitor_latest_url_by_id(db_id: int, latest_url: str):
    return await MonitorSite.filter(id=db_id).update(latest_url=latest_url, update_time=datetime.now())
