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
View-like implementations for access to the REST API.
"""

from json import dumps
from zope.app.container.traversal import ItemTraverser
from zope.traversing.api import getName

from loops.browser.concept import ConceptView
from loops.browser.node import NodeView
from loops.common import adapted


# TODO: provide lower-level (RDF-like) API for accessing the concept map
#       in a simple and generic way. 
#       next steps: RDF-like API for resources and tracks


class ApiView(NodeView):

    def __call__(self, *args, **kw):
        self.request.response.setHeader('content-type', 'application/json')
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            return targetView()
        # TODO: check for request.method
        return dumps(self.getData())

    def getData(self):
        return [dict(name=getName(n)) for n in self.context.values()]

    def get(self, name):
        print '*** NodeView: traversing', name
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            targetView = targetView.getView(name)
        else:
            tp = adapted(self.context.target)
            if tp is None:
                return None
            cname = tp.conceptManager or 'concepts'
            prefix = tp.namePrefix or ''
            target = self.loopsRoot[cname].get(prefix + name)
            if target is None:
                return None
            # TODO: find target via targetContainer
            # TODO: use self.context.viewName (if present) 
            # and target type (Interface, Adapter) to get target view
            targetView = ApiTargetView(target, self.request)
        self.viewAnnotations['targetView'] = targetView
        return self.context


class ApiTraverser(ItemTraverser):

    def publishTraverse(self, request, name):
        if self.context.get(name) is None:
            obj = ApiView(self.context, request).get(name)
            if obj is not None:
                return obj
        return self.defaultTraverse(request, name)        

    def defaultTraverse(self, request, name):
        return super(ApiTraverser, self).publishTraverse(request, name)


class ApiTargetView(ConceptView):

    def __call__(self, *args, **kw):
        # TODO: check for request.method
        return dumps(self.getData())

    def getData(self):
        obj = self.context
        # TODO: use self.adapted and typeInterface to get all properties
        return dict(name=getName(obj), title=obj.title)

    def getView(self, name):
        print '*** TargetView: traversing', name
        # TODO: check for special attributes
        value = getattr(self.adpated, name, None)
        return ApiTargetView(value, self.request)


class ApiContainerView(ConceptView):

    def __call__(self, *args, **kw):
        # TODO: check for request.method
        return dumps(self.getData())

    def getData(self):
        # TODO: check for real listing method and parameters
        #       (or produce list in the caller and use it directly as context)
        lst = self.context.getChildren()
        return [dict(name=getName(obj), title=obj.title) for obj in lst]
