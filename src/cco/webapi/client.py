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

logger = getLogger('cco.webapi.client')


def postJson(url, data, cred):
    resp = requests.post(url, json=data, auth=cred, timeout=10)
    print '*** reponse', resp.text
    print '*** status', resp.status_code
    return resp.json(), dict(state='success')


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
    print '*** notify', url, data, cred
    postJson(url, data, cred)


hook.processor_hooks['notifier'] = notify
