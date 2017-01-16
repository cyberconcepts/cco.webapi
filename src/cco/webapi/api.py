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


class ApiView(NodeView):

    def __call__(self, *args, **kw):
        self.request.response.setHeader('content-type', 'application/json')
        targetView = self.viewAnnotations.get('targetView')
        if targetView is not None:
            return targetView()
        result = [dict(name=getName(n)) for n in self.context.values()]
        return dumps(result)

    def get(self, name):
        print '*** traversing target', name
        targetContainer = self.context.target
        if targetContainer is None:
            # raise AttributeError? / NotFound
            return None
        target = self.conceptManager.get(name)
        if target is None:
            return None
        self.viewAnnotations['target'] = target
        # TODO: find target via targetContainer
        # TODO: use self.context.viewName (if present) 
        # and target type (Interface, Adapter) to get target view
        self.viewAnnotations['targetView'] = ApiTargetView(target, self.request)
        return self.context


class ApiTraverser(ItemTraverser):

    def publishTraverse(self, request, name):
        if self.context.get(name) is None:
            # if targetView present: return.targetView.get(name)
            return ApiView(self.context, request).get(name)
        return self.defaultTraverse(request, name)        

    def defaultTraverse(self, request, name):
        return super(ApiTraverser, self).publishTraverse(request, name)


class ApiTargetView(ConceptView):

    def __call__(self, *args, **kw):
        obj = self.context
        result = dict(name=getName(obj), title=obj.title)
        return dumps(result)

