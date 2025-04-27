from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger as log
from utils import redis_utils as redis
from ai_information_data.service import job_retry
import requests
import time

# 定义请求的 URL
saas_ai_url = 'https://devlawai.lawtrust.cn'

# 定义请求头
saas_ai_headers = {
    'lawyer-token': 'ZU4weWpzU1huV0NnekxiekZrQmU4OUpJOWNCbmwvU0xaR3NB',
    'Content-Type': 'application/json'
}


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


def tag_job():
    old_num = redis.get_value('tag_num')
    log.info('old_num is: {}'.format(old_num))

    log.info('开始执行count')
    count_req_retry_count = 0
    count = count_request()
    while count is None and count_req_retry_count < 10:
        log.warning(f'count_request失败，重试次数: {count_req_retry_count}')
        time.sleep(1)
        count = count_request()
        count_req_retry_count += 1
    if count is None:
        log.error('count_request重试失败，无法获取标签数量')
        return
    log.info('count is {}'.format(count))
    redis.set_value('tag_num', count)
    if old_num is not None and int(old_num) != int(count):
        log.info('打标进行中，不进行重试')
        return

    log.info('打标可能停止，开始执行job')
    tag_req_retry_count = 0
    tag = tag_request()
    while not tag and tag_req_retry_count < 10:
        log.warning(f'tag_request失败，重试次数: {tag_req_retry_count}')
        time.sleep(1)
        tag = tag_request()
        tag_req_retry_count += 1
    if not tag:
        log.error('tag_request重试失败，无法执行打标')
        return


def count_request():
    try:
        # 发送 GET 请求
        response = requests.get(saas_ai_url + '/ai/information/count_tag_num/', headers=saas_ai_headers)
        # 检查响应状态码，如果不是 200 则抛出异常
        response.raise_for_status()
        result_json = response.json()
        if result_json is None or result_json['code'] != 0:
            log.warning(f'请求失败，返回结果: {result_json}')
            return None
        return result_json['data']
    except requests.exceptions.HTTPError as http_err:
        log.warning(f'HTTP 错误发生: {http_err}')
    except requests.exceptions.RequestException as req_err:
        log.warning(f'请求错误发生: {req_err}')
    return None


def tag_request():
    try:
        data = {
            "source": -1,
            "limit": 15
        }
        response = requests.post(saas_ai_url + '/ai/information/run_tag/', headers=saas_ai_headers, json=data)
        response.raise_for_status()
        result_json = response.json()
        if result_json is None or result_json['code'] != 0:
            log.warning(f'请求失败，返回结果: {result_json}')
            return False
        return True
    except requests.exceptions.HTTPError as http_err:
        log.warning(f"HTTP 错误发生: {http_err}")
    except requests.exceptions.RequestException as req_err:
        log.warning(f"请求错误发生: {req_err}")
    return True


def init_job():
    scheduler = BackgroundScheduler()
    # 一小时执行一次job函数
    # scheduler.add_job(job, 'interval', seconds=3600)
    scheduler.add_job(tag_job, 'interval', seconds=600)
    scheduler.start()