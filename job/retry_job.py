from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger as log
from utils import redis_utils as redis
from ai_information_data.service import job_retry


def job():
    v = redis.get_value('retry:jobs')
    if v is not None:
        log.warning('当前有未完成的任务')
        return
    redis.set_value('retry:jobs', '1')
    log.info('开始执行job')
    job_retry()
    log.info('job执行完成')
    redis.del_value('retry:jobs')


def init_job():
    scheduler = BlockingScheduler()
    # 一小时执行一次job函数
    scheduler.add_job(job, 'interval', seconds=5)
    scheduler.start()
