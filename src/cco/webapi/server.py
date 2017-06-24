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

from logging import getLogger
from json import dumps, loads
from zope.app.container.traversal import ItemTraverser
from zope import component
from zope.traversing.api import getName

from loops.browser.concept import ConceptView
from loops.browser.node import NodeView
from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.setup import addAndConfigureObject


# TODO: provide lower-level (RDF-like?) API for accessing the concept map
# in a simple and generic way. 
# next steps: RDF-like API for resources and tracks


class ApiHandler(NodeView):

    def __call__(self, *args, **kw):
        self.request.response.setHeader('content-type', 'application/json')
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            return targetView()
        target = self.context.target
        if target is not None:
            targetView = self.getContainerView(target)
            return targetView()
        # TODO: check for request.method?
        if self.request.method == 'POST':
            # error
            return 'Not allowed on node'
        return dumps(self.getData())

    def getData(self):
        return [dict(name=getName(n)) for n in self.context.values()]

    def get(self, name):
        #print '*** NodeView: traversing', name
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            cv = self.getContainerView(targetView.context)
            if cv is None:
                targetView = None
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
        return component.getMultiAdapter(
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

class TargetBase(ConceptView):

    # TODO: use schema for conversion of field data
    #       (1) marshal / toJson
    #       (2) unmarshal / fromJson

    def __call__(self, *args, **kw):
        # TODO: check for request.method
        if self.request.method == 'POST':
            return self.create()
        if self.request.method == 'PUT':
            return self.update()
        return dumps(self.getData())

    def create(self):
        # error
        return 'Not allowed'

    def update(self):
        data = self.getInputData()
        if not data:
            # error
            return 'missing data'
        for k, v in data.items():
            setattr(self.adapted, k, v)
        return 'Done'

    def getInputData(self):
        return self.getPostData()

    def getPostData(self):
        instream = self.request._body_instream
        if instream is not None:
            json = instream.read()
            if json:
                return loads(json)
        return None


class TargetHandler(TargetBase):

    def getData(self):
        obj = self.context
        # TODO: use self.adapted and typeInterface to get all properties
        return dict(name=getName(obj), title=obj.title)


class ContainerHandler(TargetBase):

    def getData(self):
        # TODO: check for real listing method and parameters
        #       (or produce list in the caller and use it directly as context)
        lst = self.context.getChildren()
        return [dict(name=getName(obj), title=obj.title) for obj in lst]

    def getView(self, name):
        #print '*** ContainerHandler: traversing', name
        # TODO: check for special attributes
        # TODO: retrieve object from list of children
        #obj = self.
        obj = self.getObject(name)
        if obj is None:
            return None
        view = component.getMultiAdapter(
                (adapted(obj), self.request), name='api_target')
        return view

    def createObject(self, tp):
        data = self.getPostData()
        if not data:
            # error
            return 'missing data'
        #print '***', data
        cname = tp.conceptManager or 'concepts'
        container = self.loopsRoot[cname]
        prefix = tp.namePrefix or ''
        obj = addAndConfigureObject(container, Concept, prefix + data['name'], 
                title=data.get('title') or '',
                conceptType=baseObject(tp))
        return adapted(obj)


class TypeHandler(ContainerHandler):

    def getData(self):
        lst = self.context.getChildren([self.typePredicate])
        return [dict(name=getName(obj), title=obj.title) for obj in lst]

    def getObject(self, name):
        tp = self.adapted
        cname = tp.conceptManager or 'concepts'
        prefix = tp.namePrefix or ''
        return self.loopsRoot[cname].get(prefix + name)

    def create(self):
        obj = self.createObject(self.adapted)
        return 'Done'
