import ai_information_data.dao as aid_dao
from utils.fire_crawl_utils import scrape
from loguru import logger as log


def todo_urls(source: int):
    urls = aid_dao.todo_urls(source)
    if urls is None:
        log.info('no urls')
        return None

    log.info('todo_urls size is {}'.format(len(urls)))

    for i, item in enumerate(urls):
        log.info('todo_url: 当前进度{}/{}'.format(i, len(urls)))
        scrape_resp = scrape(item['url'])
        aid_dao.save_scraped_data(scrape_resp, item['url'], 0, item['source'], None, None, item['ext'])
        if scrape_resp.get('success'):
            data = scrape_resp.get('data')
            metadata = data.get('metadata')
            if metadata is not None and metadata.get('statusCode') and metadata.get('statusCode') == 200:
                aid_dao.complete(item['id'])


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
        scrape_resp = scrape(item['sourceUrl'])
        aid_dao.save_scraped_data(scrape_resp, item['url'], item['deep'], item['source'], item['pid'], item['path'], ext)