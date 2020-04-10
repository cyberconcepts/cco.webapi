#
#
#

"""
API node interfaces.
"""

from zope.app.container.constraints import contains, containers
from zope.interface import Interface
from zope import schema

from loops.interfaces import INodeSchema, INode, IViewManager


class IApiBase(INodeSchema):

    pass


class IApiNode(IApiBase, INode):

    contains(IApiBase)


class IApiNodeContained(Interface):

    containers(IApiNode, IViewManager)

