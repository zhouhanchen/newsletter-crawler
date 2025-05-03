from loguru import logger as log
import requests
from constants import hongkong_newsletter_host


def sync_data_job():
    log.info('🤔开始拉取今天的数据')
    resp = requests.get(f'{hongkong_newsletter_host}/aid/pull_today_data')
    if resp.status_code != 200:
        log.warning('❌请求失败，返回状态码: {}'.format(resp.status_code))
        return
    log.info('今天的数据拉取完成 ✅')
