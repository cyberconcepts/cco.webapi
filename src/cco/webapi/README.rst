
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

We now create the first basic objects.

  >>> apiRoot = addAndConfigureObject(home, ApiNode, 'webapi')
  >>> node_topics = addAndConfigureObject(apiRoot, ApiNode, 'topics')

Querying the database with the GET method
-----------------------------------------

We start with calling the API view of the top-level (root) API node.

  >>> from cco.webapi.api import ApiView
  >>> apiView = ApiView(apiRoot, req)
  >>> apiView()
  '[{"name": "topics"}]'

What happens upon traversing a node?

  >>> from cco.webapi.api import ApiTraverser
  >>> apiTrav = ApiTraverser(apiRoot, req)
  >>> obj = apiTrav.publishTraverse(req, 'topics')
  >>> obj is node_topics
  True

  >>> apiView = ApiView(node_topics, req)
  >>> apiView()
  '[]'

  >>> apiTrav = ApiTraverser(node_topics, req)
  >>> obj = apiTrav.publishTraverse(req, 'loops')
  Traceback (most recent call last):
  ...
  NotFound: ... name: 'loops'

Maybe we should assign a target: we use the topic type and
create a 'loops' topic.

  >>> node_topics.target = type_topic
  >>> topic_loops = addAndConfigureObject(concepts, Concept, 'loops',
  ...     conceptType=type_topic)

The view now shows a list of the target object's children.

  >>> apiView = ApiView(node_topics, req)
  >>> apiView()
  '[{"name": "loops", "title": ""}]'

Now we can also traverse the target object. The traverser still returns
the node, but the traversed object is remembered in the request so that 
the view can deliver the correct data.

  >>> obj = apiTrav.publishTraverse(req, 'loops')
  *** NodeView: traversing loops
  *** ContainerView: traversing loops
  >>> obj is node_topics
  True

  >>> apiView = ApiView(node_topics, req)
  >>> apiView()
  '{"name": "loops", "title": ""}'

We can also use the type hierarchy as starting point of our 
journey.

  >>> node_types = addAndConfigureObject(apiRoot, ApiNode, 'types')
  >>> node_types.target = type_type

  >>> req = TestRequest()
  >>> apiTrav = ApiTraverser(apiRoot, req)
  >>> obj = apiTrav.publishTraverse(req, 'types')
  >>> obj is node_types
  True
  >>> apiView = ApiView(node_types, req)
  >>> apiView()
  '[{"name": "topic", "title": ""}, ... {"name": "type", "title": "Type"}]'

  >>> apiTrav = ApiTraverser(node_types, req)
  >>> obj = apiTrav.publishTraverse(req, 'topic')
  *** NodeView: traversing topic
  *** ContainerView: traversing topic
  >>> apiView = ApiView(node_types, req)
  >>> apiView()
  '{"name": "topic", "title": ""}'

Next steps: 
- traverse properties of target 'topic' (?)
- traverse special attributes/methods (children()) of target topic

Creating new objects with POST
------------------------------

Updating objects with PUT
-------------------------

Create relationships (links) between objects - assign a child.
