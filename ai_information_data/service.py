import ai_information_data.dao as aid_dao
from utils.fire_crawl_utils import scrape
from loguru import logger as log
import utils.ai_consumer_utils as ai_sdk


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
        retry(0, one_site['id'])
