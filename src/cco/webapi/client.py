#
# cco.webapi.client
#

"""
Functions for providieng external services with object data 
via a REST-JSON API.
"""

import json
from logging import getLogger
import requests

from cco.processor import hook
from cco.webapi import testing

logger = getLogger('cco.webapi.client')


def sendJson(url, payload, cred, method):
    if url.startswith('test:'):
        resp = testing.request(method, url, json=payload, auth=cred)
    else:
        resp = requests.request(
                method, url, json=payload, auth=cred, timeout=10)
    logger.info('sendJson: %s %s -> %s %s.' % (
        method, url, resp.status_code, resp.text))
    # TODO: check resp.status_code
    #return resp.json(), dict(state='success')
    return resp.content


def postJson(url, payload, cred):
    return sendJson(url, payload, cred, 'POST')


def postMessage(baseUrl, domain='system', action='data', class_='', item='',
        payload=None, cred=None):
    url = '/'.join(p for p in (baseUrl, domain, action, class_, item) if p)
    return postJson(url, payload, cred)
    

def notify(obj, data):
    name = 'notifier'
    config = obj._hook_config.get(name)
    if config is None:
        logger.warn('config missing: %s' % 
            dict(hook=name, obj=obj))
        return
    baseUrl = config.get('url', 'http://localhost:8123')
    cred = config.get('_credentials', ('dummy', 'dummy')) 
    url = '/'.join((baseUrl, obj._hook_message_base, obj.identifier))
    logger.info('notify: %s - %s - %s.' % (url, data, cred))
    postJson(url, data, cred)


hook.processor_hooks['notifier'] = notify
