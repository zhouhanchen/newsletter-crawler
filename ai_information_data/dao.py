from utils.ai_consumer_utils import *
from loguru import logger as log


def get_todo_urls(source: int):
    return todo_urls(source)


def update_status(data_id):
    complete(data_id)


def get_failed_urls(deep: int, source: int):
    return failed_urls(deep, source)


def get_monitor_site():
    return monitor_site_list()


def update_site(db_id, latest_url):
    return update_site_db(db_id, latest_url)


def save_scraped_data(data, url, deep: 0, source, pid, path, ext):
    req = AiInformationDataReq()
    req.deep = deep
    req.source = source
    req.pid = pid
    req.path = path
    temp_data = data.get('data', None)
    if data.get('success'):
        metadata = temp_data.get('metadata')
        if ext is not None:
            metadata.update(json.loads(ext))
        req.metadata = json.dumps(metadata, ensure_ascii=False)
        req.title = metadata.get('title')
        req.sourceUrl = metadata.get('sourceURL')
        req.lang = metadata.get('language')
        req.markdown = temp_data['markdown']
        req.status = 'success'
    else:
        log.warning('scrape is failed, resp: {}'.format(data))
        if 'metadata' in data:
            metadata = temp_data['metadata']
            req.metadata = json.dumps(metadata, ensure_ascii=False)
            if 'statusCode' in metadata:
                req.status = metadata['statusCode']
            else:
                req.status = 'failed'
        else:
            req.status = 'failed'
            req.sourceUrl = url
    return save(req)
