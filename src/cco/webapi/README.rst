
cco.webapi - cyberconcepts.org: Web API = REST + JSON
=====================================================

Let's first do some common imports and initializations.

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.api import getName

  >>> from logging import getLogger
  >>> log = getLogger('cco.webapi')

  >>> from cco.webapi.node import ApiNode
  >>> from cco.webapi.tests import callPath, traverse

  >>> from loops.setup import addAndConfigureObject, addObject
  >>> from loops.concept import Concept

  >>> concepts = loopsRoot['concepts']
  >>> type_type = concepts['type']
  >>> type_topic = addAndConfigureObject(concepts, Concept, 'topic',
  ...     conceptType=type_type)
  >>> type_task = addAndConfigureObject(concepts, Concept, 'task',
  ...     conceptType=type_type)
  >>> home = loopsRoot['views']['home']

We now create the first basic objects.

  >>> apiRoot = addAndConfigureObject(home, ApiNode, 'webapi')
  >>> node_topics = addAndConfigureObject(apiRoot, ApiNode, 'topics')

Querying the database with the GET method
-----------------------------------------

We start with calling the API view of the top-level (root) API node.

  >>> from cco.webapi.server import ApiHandler
  >>> handler = ApiHandler(apiRoot, TestRequest())
  >>> handler()
  '[{"name": "topics"}]'

The tests module contains a shortcout for traversing a path and calling
the corresponding view.

  >>> callPath(apiRoot)
  '[{"name": "topics"}]'

What happens upon traversing a node?

  >>> callPath(apiRoot, 'topics')
  '[]'

When a node does not exist we get a 'NotFound' exception.

  >>> callPath(apiRoot, 'topics/loops')
  Traceback (most recent call last):
  ...
  NotFound: ... name: 'loops'

Maybe we should assign a target: we use the topic type as target 
and create a 'loops' topic.

  >>> node_topics.target = type_topic
  >>> topic_loops = addAndConfigureObject(concepts, Concept, 'loops',
  ...     conceptType=type_topic)

We now get a list of the target object's children.

  >>> callPath(apiRoot, 'topics')
  '[{"name": "loops", "title": ""}]'

We can also directly access the target's children using their name.

  >>> callPath(apiRoot, 'topics/loops')
  '{"name": "loops", "title": ""}'

We can also use the type hierarchy as starting point of our 
journey.

  >>> node_types = addAndConfigureObject(apiRoot, ApiNode, 'types')
  >>> node_types.target = type_type

  >>> callPath(apiRoot, 'types')
  '[{"name": "topic", "title": ""}, ... {"name": "type", "title": "Type"}]'

  >>> callPath(apiRoot, 'types/topic')
  '[{"name": "loops", "title": ""}]'

  >>> callPath(apiRoot, 'types/topic/loops')
  '{"name": "loops", "title": ""}'

Next steps
- return properties of target object as given by interface/schema
- traverse special attributes/methods (e.g. _children) of target topic

Creating new objects with POST
------------------------------

  >>> input = '{"name": "rdf", "title": "RDF"}'
  >>> callPath(apiRoot, 'types/topic', 'POST', input=input)
  'Done'

  >>> callPath(apiRoot, 'types/topic')
  '[{"name": "loops", "title": ""}, {"name": "rdf", "title": "RDF"}]'

  >>> callPath(apiRoot, 'types/topic/rdf')
  '{"name": "rdf", "title": "RDF"}'

  >>> input = '{"name": "task0001", "title": "Document loops WebAPI"}'
  >>> callPath(apiRoot, 'types/task', 'POST', input=input)
  'Done'

  >>> callPath(apiRoot, 'types/task')
  '[{"name": "task0001", "title": "Document loops WebAPI"}]'

Updating objects with PUT
-------------------------

  >>> input = '{"title": "loops"}'
  >>> callPath(apiRoot, 'topics/loops', 'PUT', input=input)
  'Done'

  >>> callPath(apiRoot, 'topics')
  '[{"name": "loops", "title": "loops"}, {"name": "rdf", "title": "RDF"}]'

  >>> callPath(apiRoot, 'topics/loops')
  '{"name": "loops", "title": "loops"}'

Create relationships (links) between objects - assign a child.
