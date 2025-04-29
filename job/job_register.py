from apscheduler.schedulers.background import BackgroundScheduler
from job.tag_job import tag_job
from job.retry_job import retry_failed_job
from loguru import logger as log
from job.craw_job import check_todo
from job.sync_data_job import sync_data_job
import asyncio


async def run_async_job(func):
    await func()


def scheduler_wrapper(func):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(run_async_job(func))
    else:
        loop.run_until_complete(run_async_job(func))


def init_job():
    scheduler = BackgroundScheduler()
    # 一小时执行一次job函数
    log.info('register retry_failed_job interval is 3600 seconds')
    scheduler.add_job(retry_failed_job, 'interval', seconds=3600)
    log.info('register tag_job, interval is 780 seconds')
    scheduler.add_job(tag_job, 'interval', seconds=780)
    log.info('register retry_failed_job, interval is 1 hours')
    scheduler.add_job(lambda: scheduler_wrapper(check_todo), 'interval', seconds=3600)
    log.info('register retry_failed_job, interval is 1 hours')
    scheduler.add_job(lambda: scheduler_wrapper(sync_data_job), 'interval', seconds=600)
    scheduler.start()
