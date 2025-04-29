import time

import datetime
import ai_information_data.dao as dao
import ai_information_data.service as service
import utils.redis_utils as redis
from constants import saas_ai_url, saas_ai_headers
import requests
from db.models import TjPushLog
from utils.snowflake_util import get_snowflake_id
from loguru import logger as log


async def check_todo():
    log.info('check_todo_and_push start')
    now = datetime.datetime.now()
    # 获取年、月、日
    year = now.year
    month = now.month
    day = now.day
    today_data = await dao.today_has_data(year, month, day)
    if today_data is None or len(today_data) == 0:
        log.info('今日没有数据')
        return
    undo_list = await dao.get_filtered_data(year, month, day)
    undo_num = len(undo_list)
    log.info('check_todo_and_push undo num is {}'.format(undo_num))

    check_todo_redis = redis.get_value('check_todo')
    if check_todo_redis is not None:
        log.warning('当前有任务在进行')
        return
    redis.set_value('check_todo', '1')
    await service.fire_crawl_url(undo_list)

    push_log = await dao.get_today_push_log()

    if push_log is not None and push_log.status == 1:
        log.info('今日已成功推送，不再进行推送')
        return

    data = {
        'source': -1
    }
    # 先检查今天是否已经打标签完成
    response = requests.post(saas_ai_url + '/ai/information/count_untag_num_today/', headers=saas_ai_headers, json=data)
    response.raise_for_status()
    result_json = response.json()
    if result_json is None or result_json['code'] != 0:
        log.warning(f'请求失败，返回结果: {result_json}')
        return
    log.info('response is {}'.format(result_json))
    num = int(result_json['data'])

    if num > 0:
        log.info('今日数据打标未完成，num is {}'.format(num))
        return

    log.info('开始推送 cos')
    # 开始推送 cos
    response = requests.post(saas_ai_url + '/ai/information/push_history_tj/', headers=saas_ai_headers, json=data)
    response.raise_for_status()
    result_json = response.json()
    log.success('resp is {}'.format(result_json))
    push_status = 0
    if result_json is None or result_json['code'] != 0:
        log.warning(f'请求失败，返回结果: {result_json}')
    else:
        push_status = 1

    now = int(time.time())
    if push_log is None:
        await TjPushLog.create(id=get_snowflake_id(), status=push_status, create_time=now, push_time=now)
    else:
        push_log.push_time = now
        push_log.status = push_status
        await push_log.save()
    redis.del_value('check_todo')



