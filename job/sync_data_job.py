from ai_information_data.service import pull_today_data
from loguru import logger as log


async def sync_data_job():
    log.info('开始拉取今天的数据')
    await pull_today_data()
    log.info('今天的数据拉取完成')
