from ai_information_data.service import pull_today_data
from loguru import logger as log
from ai_information_data import dao


async def sync_data_job():
    log.info('开始执行 sync_data_job')
    push_log = await dao.get_today_push_log()

    if push_log is not None and push_log.status == 1:
        log.info('今日已成功推送，不再进行数据拉取')
        return
    log.info('开始拉取今天的数据')
    await pull_today_data()
    log.info('今天的数据拉取完成')
