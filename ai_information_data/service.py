import json

import ai_information_data.dao as aid_dao
from utils.fire_crawl_utils import scrape
from loguru import logger as log
import utils.ai_consumer_utils as ai_sdk
import utils.redis_utils as redis
from tortoise import Tortoise, run_async


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
    sites = aid_dao.get_monitor_site()
    for one_site in sites:
        retry(None, one_site['id'])


async def todo_clean_data(req):
    un_todo_url = await aid_dao.get_un_todo_urls()
    log.info('un_todo_url size is {}'.format(len(un_todo_url)))
    redis.set_value('un_todo_url', len(un_todo_url))
    for i, item in enumerate(un_todo_url):
        log.info('un_todo_url: 当前进度{}/{}'.format(i + 1, len(un_todo_url)))
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

        redis.set_value('un_todo_url', len(un_todo_url) - (i + 1))

    return None


async def pull_today_data():
    conn = Tortoise.get_connection('default')

    insert_sql = ('insert ignore into todo_clean_data(id, task_id, title, url, publish_time, create_time, update_time) '
                  'select id, task_id, title, url, publish_time, create_time, update_time from crawler_ai_news_detail')
    insert_result = await conn.execute_script(insert_sql)
    log.info('insert_result is {}'.format(insert_result))

    update_sql_1 = ('update todo_clean_data t1 join crawler_ai_news_task_config t2 '
                    'on t1.task_id = t2.id set t1.website_info_id = t2.website_info_id')
    await conn.execute_script(update_sql_1)

    update_sql_2 = ('update todo_clean_data t1 join crawler_website_info t2 '
                    'on t1.website_info_id = t2.id '
                    'set t1.region  = t2.region,'
                    't1.country = t2.country,'
                    't1.subject_type = t2.subject_type,'
                    't1.organization_type = t2.organization_type,'
                    't1.notification_agency = t2.notification_agency,'
                    't1.article_category = t2.article_category,'
                    't1.regional_scope = t2.regional_scope,'
                    't1.identification_source = t2.identification_source,'
                    't1.website_info_id = t2.id,'
                    't1.lang_site = t2.language_locale,'
                    't1.lang = t2.language')
    await conn.execute_script(update_sql_2)

    return None
