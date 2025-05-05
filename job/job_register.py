from apscheduler.schedulers.background import BackgroundScheduler
from job.tag_job import tag_job
from job.retry_job import retry_failed_job
from loguru import logger as log
from job.craw_job import check_todo
from job.sync_data_job import sync_data_job


def init_job():
    scheduler = BackgroundScheduler()
    # 一小时执行一次job函数
    # log.info('register retry_failed_job interval is 1 hours')
    # scheduler.add_job(retry_failed_job, 'interval', seconds=3600, max_instances=10)
    log.info('register tag_job, interval is 13 minutes')
    scheduler.add_job(tag_job, 'interval', seconds=780)
    log.info('register check_todo, interval is 1 hours')
    scheduler.add_job(check_todo, 'interval', seconds=3600)
    log.info('register sync_data_job, interval is 10 minutes')
    scheduler.add_job(sync_data_job, 'interval', seconds=600)
    scheduler.start()
