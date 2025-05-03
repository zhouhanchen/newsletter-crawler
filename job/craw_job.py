import requests
from loguru import logger as log
from constants import hongkong_newsletter_host


def check_todo():
    log.info('🤔start execute check_todo job ...')
    resp = requests.get(f'{hongkong_newsletter_host}/aid/test_check_todo')
    if resp.status_code != 200:
        log.warning('❌请求失败，返回状态码: {}'.format(resp.status_code))
        return
    log.info('✅check_todo job executed successfully')
