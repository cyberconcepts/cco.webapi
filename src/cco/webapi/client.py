#
#  Copyright (c) 2018 Helmut Merz helmutm@cy55.de
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Functions for accessing external services via a REST-JSON API.
"""

import json
import requests


def sendJson(url, data, cred, method='POST'):
    try:
        resp = requests.request(method, url, json=data, auth=cred, timeout=10)
    except requests.exceptions.Timeout:
        return {}, dict(state='retry')
    # Todo: check resp.status_code
    return resp.json(), dict(state='success')

