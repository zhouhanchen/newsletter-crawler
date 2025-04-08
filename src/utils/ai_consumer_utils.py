import json

import requests
from src.ai_information_data.models import AiInformationDataReq
from loguru import logger as log

base_url = 'https://testai.ilaw.law/consumer-gateway/consumer-ai-server'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzeXN0ZW1JZCI6IkNPTlNVTUVSX0FJIiwicGhvbmUiOiIxNTUyMzMxMjgzMSIsImV4cCI6MTc0NDcyNDQ0NCwidXNlcklkIjoiMTg4OTUxMzg0NzUwOTcwMDYxMCJ9.kBAEikwpzbH0eQH91AwihOJR9iVSdHydfSlvV3Qo0O4'

def get_data(response, api):
    if response.status_code == 200:
        if response.json()['code'] == 0:
            log.success(f'{api} is request success')
            return response.json()['data']
        else:
            log.error(f'failed, error: {response.json()}')
    else:
        log.error('request failed, status code: {}'.format(response.status_code))
    return None

def save(data: AiInformationDataReq):
    api = '/api/v1/crawl/data/save'
    resp = requests.post(base_url + api, headers={
        'content-type': 'application/json',
        'token': token
    },data=data.to_json_str())

    return get_data(resp, api)

def todo_urls(source: int):
    api = '/api/v1/todoUrl/get'
    resp = requests.post(base_url + api, headers={
        'content-type': 'application/json',
        'token': token
    }, data=json.dumps({'source': source, 'status': 0}, ensure_ascii=False))

    return get_data(resp, api)

def complete(data_id):
    api = '/api/v1/todoUrl/complete/' + str(data_id)
    resp = requests.post(base_url + api, headers={
        'content-type': 'application/json',
        'token': token
    }, data=json.dumps({}))

    get_data(resp, api)


def failed_urls(deep:int, source: int):
    api = '/api/v1/crawl/data/get'
    resp = requests.post(base_url + api, headers={
        'content-type': 'application/json',
        'token': token
    }, data=json.dumps({'deep': deep, 'source': source, 'failed': True}, ensure_ascii=False))

    return get_data(resp, api)


def monitor_site_list():
    api = '/api/v1/monitorSite/list'
    resp = requests.get(base_url + api, headers={
        'token': token,
    })
    return get_data(resp, api)

def update_site_db(db_id, latest_url):
    pass