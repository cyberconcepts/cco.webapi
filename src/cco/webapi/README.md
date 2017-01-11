
cco.webapi - cyberconcepts.org: Web API = REST + JSON
=====================================================

  >>> from zope.publisher.browser import TestRequest
  >>> from logging import getLogger
  >>> log = getLogger('cco.webapi')

  >>> from cco.webapi.node import ApiNode
  >>> from loops.setup import addAndConfigureObject, addObject
  >>> from loops.concept import Concept

  >>> concepts = loopsRoot['concepts']
  >>> home = loopsRoot['views']['home']
  >>> addAndConfigureObject(home, ApiNode, 'webapi')
  <cco.webapi.node.ApiNode object...>

  >>> from cco.webapi.api import ApiView
  >>> apiRoot = home['webapi']
  >>> apiView = ApiView(apiRoot, TestRequest())

