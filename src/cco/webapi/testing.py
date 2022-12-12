#
# cco.webapi.testing
#

"""
Mock classes and functions for testing.
"""

class Response(object):

    def __init__(self, status, content, text):
        self.status_code = status
        self.content = content
        self.text = text


def request(method, url, json, auth):
    print('request: %s, %s, %s, %s' % (method, url, json, auth))
    result = '{"state": "success"}'
    return Response(200, result, result)

