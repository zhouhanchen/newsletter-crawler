from apscheduler.schedulers.background import BackgroundScheduler
from job.tag_job import tag_job
from job.retry_job import retry_failed_job
from loguru import logger as log


def init_job():
    scheduler = BackgroundScheduler()
    # 一小时执行一次job函数
    log.info('register retry_failed_job interval is 3600 seconds')
    scheduler.add_job(retry_failed_job, 'interval', seconds=3600)
    log.info('register tag_job, interval is 780 seconds')
    scheduler.add_job(tag_job, 'interval', seconds=780)
    scheduler.start()
