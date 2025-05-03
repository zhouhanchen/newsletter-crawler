import json

import ai_information_data.dao as aid_dao
from utils.fire_crawl_utils import scrape
from loguru import logger as log
import utils.ai_consumer_utils as ai_sdk
import utils.redis_utils as redis
from tortoise import Tortoise
import datetime
from sql.todo_data_sql import insert_sql, update_sql_1, update_sql_2
import requests
import time
from db.models import TjPushLog
from constants import saas_ai_url, saas_ai_headers
from utils.snowflake_util import get_snowflake_id


def todo_urls(source: int):
    urls = aid_dao.todo_urls(source)
    if urls is None:
        log.info('no urls')
        return None

    log.info('todo_urls size is {}'.format(len(urls)))

    for i, item in enumerate(urls):
        log.info('todo_url: 当前进度{}/{}'.format(i, len(urls)))
        try:
            scrape_resp = scrape(item['url'])
            aid_dao.save_scraped_data(scrape_resp, item['url'], 0, item['source'], None, None, item['ext'])
            if scrape_resp.get('success'):
                data = scrape_resp.get('data')
                metadata = data.get('metadata')
                if metadata is not None and metadata.get('statusCode') and metadata.get('statusCode') == 200:
                    aid_dao.complete(item['id'])
        except Exception as e:
            log.warning('爬取失败: {}'.format(e))
            aid_dao.save_scraped_data({}, item['url'], 0, source,
                                      None, None, item['ext'])


def retry(deep: int, source: int):
    failed_data = aid_dao.get_failed_urls(deep, source)
    log.info('failed_urls size is {}'.format(len(failed_data)))

    ext = None
    for item in aid_dao.get_monitor_site():
        if item['id'] == source:
            ext = item['ext']
            break

    for i, item in enumerate(failed_data):
        log.info('failed_url: {}/{}'.format(i, len(failed_data)))
        try:
            scrape_resp = scrape(item['sourceUrl'])
            aid_dao.save_scraped_data(scrape_resp, item['sourceUrl'], item['deep'], item['source'], item['pid'],
                                      item['path'], ext)
        except Exception as e:
            log.warning('爬取失败: {}'.format(e))
            aid_dao.save_scraped_data({}, item['sourceUrl'], int(item['deep']), item['source'],
                                      item['id'], item['path'], ext)

    log.info('finish retry')


def deep(req):
    ext = None
    for item in aid_dao.get_monitor_site():
        if item['id'] == req['source']:
            ext = item['ext']
            break
    # 根据条件获取要爬取的urls
    data_array = ai_sdk.deep_urls(req)
    log.info('data_array size is {}'.format(len(data_array)))
    for i, item in enumerate(data_array):
        item_urls = item['urls']
        log.info('deep_url: {}/{}, item_urls: {}'.format(i, len(data_array), len(item_urls)))
        if len(item_urls) == 0:
            log.info('没有要爬取的url')
            continue

        for j, url in enumerate(item_urls):
            log.info('deep_url: {}/{}, url: {}'.format(j, len(item_urls), url))
            try:
                scrape_resp = scrape(url)
                aid_dao.save_scraped_data(scrape_resp, url, int(item['deep'] + 1), item['source'],
                                          item['id'], item['path'], ext)
            except Exception as e:
                log.warning('爬取失败: {}'.format(e))
                aid_dao.save_scraped_data({}, url, int(item['deep'] + 1), item['source'],
                                          item['id'], item['path'], ext)

    log.info('finish deep')


def job_retry():
    # sites = aid_dao.get_monitor_site()
    # for one_site in sites:
    retry(0, -1)


async def todo_clean_data(req):
    un_todo_url = await aid_dao.get_un_todo_urls()
    # un_todo_url = await aid_dao.get_filtered_data(2025, 4, 23)
    await fire_crawl_url(un_todo_url)


async def fire_crawl_url(todo_url_list):
    log.info('un_todo_url size is {}'.format(len(todo_url_list)))
    redis.set_value('un_todo_url', len(todo_url_list))
    for i, item in enumerate(todo_url_list):
        log.info('un_todo_url: 当前进度{}/{}'.format(i + 1, len(todo_url_list)))
        ext = {
            'region': item.region,
            'countryOrAreas': item.country,
            'subjectType': item.subject_type,
            'orgType': item.organization_type,
            'notificationAgency': item.notification_agency,
            'articleClass': item.article_category,
            'identifySource': item.identification_source,
            'siteLang': item.lang,
            'regionalScope': item.regional_scope
        }
        try:
            todo_url = item.url if item.attachment is None else item.attachment
            scrape_resp = scrape(todo_url)
            if item.publish_time is not None:
                scrape_resp['publishTime'] = item.publish_time.strftime('%Y-%m-%d %H:%M:%S')
            scrape_resp['tempTitle'] = item.title
            scrape_resp['tempLang'] = item.lang_site
            scrape_resp['data']['metadata']['sourceURL'] = item.url
            aid_dao.save_scraped_data(scrape_resp, item.url, 0, -1, None, None, json.dumps(ext, ensure_ascii=False))
            await aid_dao.complete_un_todo_url(item.id)
        except Exception as e:
            log.warning('爬取失败: {}'.format(e))
            await aid_dao.mark_exception_status(item.id, item.retry_num + 1)

        redis.set_value('un_todo_url', len(todo_url_list) - (i + 1))

    return None


async def pull_today_data():
    conn = Tortoise.get_connection('default')

    log.info('execute insert_sql')
    await conn.execute_script(insert_sql)

    log.info('execute update_sql_1')
    await conn.execute_script(update_sql_1)

    log.info('execute update_sql_2')
    await conn.execute_script(update_sql_2)

    return None


async def execute_fire_crawl_job():
    now = datetime.datetime.now()

    # 获取年、月、日
    year = now.year
    month = now.month
    day = now.day
    # 执行未完成的
    un_todo_url = await aid_dao.get_filtered_data(year, month, day)
    await fire_crawl_url(un_todo_url)


async def check_todo():
    log.info('check_todo_and_push start')
    now = datetime.datetime.now()
    # 获取年、月、日
    year = now.year
    month = now.month
    day = now.day
    today_data = await aid_dao.today_has_data(year, month, day)
    if today_data is None or len(today_data) == 0:
        log.info('今日没有数据')
        return
    undo_list = await aid_dao.get_filtered_data(year, month, day)
    undo_num = len(undo_list)
    log.info('check_todo_and_push undo num is {}'.format(undo_num))

    check_todo_redis = redis.get_value('check_todo')
    if check_todo_redis is not None:
        log.warning('当前有任务在进行')
        return
    redis.set_value('check_todo', '1')
    await fire_crawl_url(undo_list)

    push_log = await aid_dao.get_today_push_log()

    if push_log is not None and push_log.status == 1:
        log.info('今日已成功推送，不再进行推送')
        redis.del_value('check_todo')
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
        redis.del_value('check_todo')
        return
    log.info('response is {}'.format(result_json))
    num = int(result_json['data'])

    if num > 0:
        log.info('今日数据打标未完成，num is {}'.format(num))
        redis.del_value('check_todo')
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
