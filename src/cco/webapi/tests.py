#! /usr/bin/python

"""
Tests for the 'cco.webapi' package.
"""

import os
import unittest, doctest
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope import component
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

from loops.interfaces import IConceptSchema, ITypeConcept
from loops.setup import importData as baseImportData
from loops.tests.setup import TestSite

from cco.webapi.api import ApiTargetView, ApiContainerView, ApiTypeView
from cco.webapi.api import ApiView, ApiTraverser


def setUp(self):
    site = placefulSetUp(True)
    t = TestSite(site)
    concepts, resources, views = t.setup()
    loopsRoot = site['loops']
    self.globs['loopsRoot'] = loopsRoot
    component.provideAdapter(ApiTargetView, 
        (IConceptSchema, IBrowserRequest), Interface, name='api_target')
    component.provideAdapter(ApiContainerView, 
        (IConceptSchema, IBrowserRequest), Interface, name='api_container')
    component.provideAdapter(ApiTypeView, 
        (ITypeConcept, IBrowserRequest), Interface, name='api_container')


def tearDown(self):
    placefulTearDown()


def traverse(root, request, path):
    obj = root
    for name in path.split('/'):
        trav = ApiTraverser(obj, request)
        obj = trav.publishTraverse(request, name)
    return obj

def callPath(obj, path='', method='GET', params={}):
    request = TestRequest(method=method, form=params)
    if path:
        obj = traverse(obj, request, path)
    view = ApiView(obj, request)
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
