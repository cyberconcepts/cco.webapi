
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
  INFO: Input Data: {u'name': u'rdf', u'title': u'RDF'}
  '{"info": "Done"}'
  
  >>> callPath(apiRoot, 'types/topic')
  '[{"name": "loops", "title": ""}, {"name": "rdf", "title": "RDF"}]'

  >>> callPath(apiRoot, 'types/topic/rdf')
  '{"name": "rdf", "title": "RDF"}'

  >>> input = '{"name": "task0001", "title": "Document loops WebAPI"}'
  >>> callPath(apiRoot, 'types/task', 'POST', input=input)
  INFO: Input Data: {u'name': u'task0001', u'title': u'Document loops WebAPI'}
  '{"info": "Done"}'

  >>> callPath(apiRoot, 'types/task')
  '[{"name": "task0001", "title": "Document loops WebAPI"}]'

Updating objects with PUT
-------------------------

  >>> input = '{"title": "loops"}'
  >>> callPath(apiRoot, 'topics/loops', 'PUT', input=input)
  INFO: Input Data: {u'title': u'loops'}
  '{"info": "Done"}'

  >>> callPath(apiRoot, 'topics')
  '[{"name": "loops", "title": "loops"}, {"name": "rdf", "title": "RDF"}]'

  >>> callPath(apiRoot, 'topics/loops')
  '{"name": "loops", "title": "loops"}'

Let's just see what happens if we do not supply input data.

  >>> callPath(apiRoot, 'topics/loops', 'PUT', input='{}')
  INFO: Input Data: {}
  ERROR: Missing data
  '{"status": 500, "message": "Missing data"}'

Create relationships (links) between objects - assign a child.

... TODO ...

Client module
=============

  >>> from cco.webapi.client import postMessage

  >>> postMessage('test://localhost:8123/webapi', 
  ...       'demo', 'query', 'topics', 'rdf')
  request: POST test://localhost:8123/webapi/demo/query/topics/rdf
  None
  auth: None
  '{"state": "success"}'

Asynchronous processing of integrator messages
==============================================

query action
------------

  >>> node_domain = addAndConfigureObject(apiRoot, ApiNode, 'demo')
  >>> node_query = addAndConfigureObject(node_domain, ApiNode, 'query')
  >>> node_query.target = type_type
  >>> node_query.viewName = 'api_integrator_query'

  >>> callPath(apiRoot, 'demo/query/topic')
  request: POST test://localhost:8123/webapi/demo/list/topic
  {"title": "loops", "_item": "loops"}
  {"title": "RDF", "_item": "rdf"}
  auth: None
  '"{\\"state\\": \\"success\\"}"'

  >>> callPath(apiRoot, 'demo/query/topic/loops')
  request: POST test://localhost:8123/webapi/demo/data/topic/loops
  {"title": "loops"}
  auth: None
  '"{\\"state\\": \\"success\\"}"'

data action
-----------

  >>> node_data = addAndConfigureObject(node_domain, ApiNode, 'data')
  >>> node_data.target = type_type

  >>> input = '{"name": "typescript", "title": "Typescript"}'
  >>> callPath(apiRoot, 'demo/data/topic', 'POST', input=input)
  INFO: Input Data: {u'name': u'typescript', u'title': u'Typescript'}
  '{"info": "Done"}'

  >>> input = '{"title": "TypeScript"}'
  >>> callPath(apiRoot, 'demo/data/topic/typescript', 'POST', input=input)
  INFO: Input Data: {u'title': u'TypeScript'}
  '{"info": "Done"}'

  >>> input = '{"title": "TypeScript"}'
  >>> callPath(apiRoot, 'demo/data/topic/typescript', 'POST', input=input)
  INFO: Input Data: {u'title': u'TypeScript'}
  '{"info": "Done"}'

  >>> callPath(apiRoot, 'demo/query/topic')
  request: POST test://localhost:8123/webapi/demo/list/topic
  {"title": "loops", "_item": "loops"}
  {"title": "RDF", "_item": "rdf"}
  {"title": "TypeScript", "_item": "typescript"}
  auth: None
  '"{\\"state\\": \\"success\\"}"'


