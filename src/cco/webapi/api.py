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
NodeView implementations for access to the REST API.
"""

from zope.app.container.traversal import ItemTraverser

from loops.browser.node import NodeView


class ApiView(NodeView):

    def __call__(self, *args, **kw):
        print '*** API View'
        return 'API View'

    def get(self, name):
        print '*** traversing', name
        # use self.context.viewName to get real view
        # use this view + name to get target and targetView
        # put targetView in request annotations
        return self.context


class ApiTraverser(ItemTraverser):

    def publishTraverse(self, request, name):
        if self.context.get(name) is None:
            # if targetView present: return.targetView.get(name)
            return ApiView(self.context, request).get(name)
        return self.defaultTraverse(request, name)        

    def defaultTraverse(self, request, name):
        return super(ApiTraverser, self).publishTraverse(request, name)

