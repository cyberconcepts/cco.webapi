
cco.webapi - cyberconcepts.org: Web API = REST + JSON
=====================================================

Let's first do some common imports and initializations.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.api import getName

  >>> from logging import getLogger
  >>> log = getLogger('cco.webapi')

  >>> from cco.webapi.node import ApiNode
  >>> from loops.setup import addAndConfigureObject, addObject
  >>> from loops.concept import Concept

  >>> concepts = loopsRoot['concepts']
  >>> type_type = concepts['type']
  >>> type_topic = addAndConfigureObject(concepts, Concept, 'topic',
  ...     conceptType=type_type)
  >>> home = loopsRoot['views']['home']

  >>> req = TestRequest()

We now create the first basic objects

  >>> apiRoot = addAndConfigureObject(home, ApiNode, 'webapi')
  >>> node_topics = addAndConfigureObject(apiRoot, ApiNode, 'topics')

We start with calling the API view of the top-level (root) API node.

  >>> from cco.webapi.api import ApiView
  >>> apiView = ApiView(apiRoot, req)
  >>> apiView()
  '[{"name": "topics"}]'

What happens upon traversing a node?

  >>> from cco.webapi.api import ApiTraverser
  >>> apiTrav = ApiTraverser(apiRoot, req)
  >>> obj = apiTrav.publishTraverse(TestRequest(), 'topics')
  >>> obj is node_topics
  True

  >>> apiTrav = ApiTraverser(node_topics, req)
  >>> obj = apiTrav.publishTraverse(TestRequest(), 'loops')
  *** traversing target loops
  >>> obj is None
  True

Maybe we should assign a target: we use the topic type and
create a 'loops' topic.

  >>> node_topics.target = type_topic
  >>> topic_loops = addAndConfigureObject(concepts, Concept, 'loops',
  ...     conceptType=type_topic)

  >>> obj = apiTrav.publishTraverse(req, 'loops')
  *** traversing target loops
  >>> obj is node_topics
  True

The traversed object is remembered in the request so that the 
view can deliver the correct data.

  >>> apiView = ApiView(node_topics, req)
  >>> apiView()
  '{"name": "loops", "title": ""}'

