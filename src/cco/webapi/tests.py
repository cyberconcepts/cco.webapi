#! /usr/bin/python

"""
Tests for the 'cco.webapi' package.
"""

import io
import logging
import os
import sys
import unittest, doctest
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope import component
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

from loops.interfaces import IConceptSchema, ITypeConcept
from loops.setup import importData as baseImportData
from loops.tests.setup import TestSite

from cco.webapi.server import ApiHandler, ApiTraverser
from cco.webapi.server import TargetHandler, ContainerHandler, TypeHandler
from cco.webapi.server import IntegratorQuery, IntegratorClassQuery, IntegratorItemQuery

import cco.webapi
cco.webapi.config.integrator['url'] = 'test://localhost:8123/webapi'

class LogHandler(logging.StreamHandler):

    def emit(self, record):
        print('%s: %s' % (record.levelname, record.msg))

logger = logging.getLogger('cco.webapi.server')
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.addHandler(LogHandler())


def setUp(self):
    site = placefulSetUp(True)
    t = TestSite(site)
    concepts, resources, views = t.setup()
    loopsRoot = site['loops']
    self.globs['loopsRoot'] = loopsRoot
    component.provideAdapter(TargetHandler, 
        (IConceptSchema, IBrowserRequest), Interface, name='api_target')
    component.provideAdapter(ContainerHandler, 
        (IConceptSchema, IBrowserRequest), Interface, name='api_container')
    component.provideAdapter(TypeHandler, 
        (ITypeConcept, IBrowserRequest), Interface, name='api_target')
    component.provideAdapter(TypeHandler, 
        (ITypeConcept, IBrowserRequest), Interface, name='api_container')
    component.provideAdapter(IntegratorQuery, 
        (ITypeConcept, IBrowserRequest), Interface, name='api_integrator_query')
    component.provideAdapter(IntegratorClassQuery, 
        (IConceptSchema, IBrowserRequest), Interface, 
        name='api_integrator_class_query')
    component.provideAdapter(IntegratorItemQuery, 
        (IConceptSchema, IBrowserRequest), Interface, 
        name='api_integrator_item_query')


def tearDown(self):
    placefulTearDown()


def traverse(root, request, path):
    obj = root
    for name in path.split('/'):
        trav = ApiTraverser(obj, request)
        obj = trav.publishTraverse(request, name)
    return obj

def callPath(obj, path='', method='GET', params={}, input=''):
    env = dict(REQUEST_METHOD=method)
    request = TestRequest(
                body_instream=io.BytesIO(input), environ=env, form=params)
    if path:
        obj = traverse(obj, request, path)
    view = ApiHandler(obj, request)
    return view()


class Test(unittest.TestCase):
    "Basic tests."

    def testBasicStuff(self):
        pass


def test_suite():
    flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        doctest.DocFileSuite('README.rst', optionflags=flags,
                     setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
