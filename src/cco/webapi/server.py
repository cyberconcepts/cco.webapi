#
#  Copyright (c) 2017 Helmut Merz helmutm@cy55.de
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
View-like implementations for the REST API.
"""

import logging
from json import dumps, loads
from zope.app.container.traversal import ItemTraverser
from zope import component
from zope.traversing.api import getName

from loops.browser.concept import ConceptView
from loops.browser.node import NodeView
from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.setup import addAndConfigureObject

# provide lower-level (RDF-like?) API for accessing the concept map
# in a simple and generic way. 
# next steps: RDF-like API for resources and tracks


logger = logging.getLogger('cco.webapi.server')
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


class ApiCommon(object):
    """ Common routines for logging, error handling, etc
    """

    # HTTP Status: see https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

    logger = logger

    def logInfo(self, message=None):
        self.logger.info(message)

    def logDebug(self, message=None):
        self.logger.debug(message)

    def success(self, message='Done', **kw):
        kw.update(dict(message=message))
        self.logger.debug(message)
        return dumps(kw)

    def error(self, message, status=500):
        self.logger.error(message)
        self.request.response.setStatus(status, message)
        return dumps(dict(message=message, status=status))


class ApiHandler(ApiCommon, NodeView):

    def __call__(self, *args, **kw):
        self.logDebug('Request Env: ' + str(self.request._environ))
        self.request.response.setHeader('content-type', 'application/json')
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            return targetView()
        target = self.context.target
        if target is not None:
            targetView = self.getContainerView(target)
            return targetView()
        # TODO: check for request.method?
        if self.request.method in ('PUT', 'POST'):
            return self.error('Method not allowed', 405)
        return dumps(self.getData())

    PUT = __call__

    def getData(self):
        return [dict(name=getName(n)) for n in self.context.values()]

    def get(self, name):
        #self.logInfo('*** NodeView: traversing ' + name)
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            cv = self.getContainerView(targetView.adapted)
            if cv is None:
                targetView = targetView.getView(name)
            else:
                targetView = cv.getView(name)
        else:
            target = self.context.target
            if target is None:
                return None
            cv = self.getContainerView(target)
            targetView = cv.getView(name)
        if targetView is None:
            return None
        self.viewAnnotations['targetView'] = targetView
        return self.context

    def getContainerView(self, target):
        viewName = self.context.viewName or 'api_container'
        return component.queryMultiAdapter(
                    (adapted(target), self.request), name=viewName)


class ApiTraverser(ItemTraverser):

    def publishTraverse(self, request, name):
        if self.context.get(name) is None:
            obj = ApiHandler(self.context, request).get(name)
            if obj is not None:
                return obj
        return self.defaultTraverse(request, name)

    def defaultTraverse(self, request, name):
        return super(ApiTraverser, self).publishTraverse(request, name)


# target / concept views

class TargetBase(ApiCommon, ConceptView):

    # TODO: use schema for conversion of field data
    #       (1) marshal / toJson
    #       (2) unmarshal / fromJson

    routes = {}

    def __call__(self, *args, **kw):
        if self.request.method == 'POST':
            return self.create()
        if self.request.method == 'PUT':
            return self.update()
        return dumps(self.getData())

    def getName(self, obj):
        obj = baseObject(obj)
        name = getName(obj)
        prefix = adapted(obj.getType()).namePrefix
        if prefix and name.startswith(prefix):
            name = name[len(prefix):]
        return name

    def create(self):
        # error
        return self.error('Not allowed', 405)

    def update(self):
        data = self.getInputData()
        if not data:
            return self.error('Missing data')
        for k, v in data.items():
            setattr(self.adapted, k, v)
        return self.success()

    def getInputData(self):
        data = self.getPostData()
        self.logInfo('Input Data: ' + repr(data))
        return data

    def getPostData(self):
        stream = self.request.bodyStream
        if stream is not None:
            json = stream.read(None)
            self.logInfo('POST Data: ' + repr(json))
            if json:
                return loads(json)
        return None


class TargetHandler(TargetBase):

    def getView(self, name):
        cname = self.routes.get(name)
        if cname is not None:
            name = cname
        view = component.getMultiAdapter(
                (self.adapted, self.request), name=name)
        return view

    def getData(self):
        obj = self.context
        # TODO: use self.adapted and typeInterface to get all properties
        return dict(name=self.getName(obj), title=obj.title)


class ContainerHandler(TargetBase):

    def getData(self):
        # TODO: check for real listing method and parameters
        #       (or produce list in the caller and use it directly as context)
        lst = self.context.getChildren()
        return [dict(name=self.getName(obj), title=obj.title) for obj in lst]

    def getView(self, name):
        #print '*** ContainerHandler: traversing', name, self
        # TODO: check for special attributes
        # TODO: retrieve object from list of children
        obj = self.getObject(name)
        if obj is None:
            return None
        view = component.getMultiAdapter(
                (adapted(obj), self.request), name='api_target')
        return view

    def getObject(self, name):
        self.error('getObject: To be implemented by subclass')
        return None

    def createObject(self, tp):
        data = self.getInputData()
        if not data:
            self.error('Missing data')
            return None
        cname = tp.conceptManager or 'concepts'
        container = self.loopsRoot[cname]
        prefix = tp.namePrefix or ''
        name = data.get('name')
        if name is None:
            name = self.generateName(data)
        obj = addAndConfigureObject(container, Concept, prefix + name, 
                title=data.get('title') or '',
                conceptType=baseObject(tp))
        return adapted(obj)


class TypeHandler(ContainerHandler):

    def getData(self):
        lst = self.context.getChildren([self.typePredicate])
        return [dict(name=self.getName(obj), title=obj.title) for obj in lst]

    def getObject(self, name):
        # TODO: use catalog query
        tp = self.adapted
        cname = tp.conceptManager or 'concepts'
        prefix = tp.namePrefix or ''
        return self.loopsRoot[cname].get(prefix + name)

    def create(self):
        obj = self.createObject(self.adapted)
        return self.success()
