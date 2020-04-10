#
#
#

"""
API node implementations.
"""

from zope.interface import implements

from cco.webapi.interfaces import IApiNode, IApiNodeContained
from loops.view import Node


class ApiNode(Node):

    implements(IApiNode, IApiNodeContained)

