from unittest import TestSuite, TestCase
import random

from _srctests import SrcPyTest_EntityArg

from entities import CBaseEntity, PyHandle, EntityFactory, CreateEntityByName, DispatchSpawn
from utils import UTIL_RemoveImmediate

# A test python entity we can use.
class TestPythonEnt(CBaseEntity):
    pass
sometest = EntityFactory("testpythonent", TestPythonEnt)     
    
# Add all tests
def CreateConverterTestSuite():
    suite = TestSuite()
    suite.addTest(EntityConverterTestCase('test_nonearg'))
    suite.addTest(EntityConverterTestCase('test_validpythonentity'))
    suite.addTest(EntityConverterTestCase('test_removedpythonentity'))
    suite.addTest(EntityConverterTestCase('test_nonehandlearg'))
    suite.addTest(EntityConverterTestCase('test_validpythonhandle'))
    suite.addTest(EntityConverterTestCase('test_removedpythonhandle'))
    return suite

class EntityConverterTestCase(TestCase):
    """ Test functions related to entity converting """
    def setUp(self):
        pass

    def test_nonearg(self):
        SrcPyTest_EntityArg(None)
        
    def test_validpythonentity(self):
        arg = CreateEntityByName('testpythonent').Get()
        self.assertTrue( type(arg) == TestPythonEnt )
        DispatchSpawn(arg)
        SrcPyTest_EntityArg(arg)
        UTIL_RemoveImmediate(arg)
        
    def test_removedpythonentity(self):
        arg = CreateEntityByName('testpythonent').Get()
        self.assertTrue( type(arg) == TestPythonEnt )
        DispatchSpawn(arg)
        UTIL_RemoveImmediate(arg)
        SrcPyTest_EntityArg(arg)
        
    def test_nonehandlearg(self):
        SrcPyTest_EntityArg(PyHandle(None))
        
    def test_validpythonhandle(self):
        arg = CreateEntityByName('testpythonent')
        self.assertTrue( type(arg) == PyHandle )
        DispatchSpawn(arg)
        SrcPyTest_EntityArg(arg)
        UTIL_RemoveImmediate(arg)
        
    def test_removedpythonhandle(self):
        arg = CreateEntityByName('testpythonent')
        self.assertTrue( type(arg) == PyHandle )
        DispatchSpawn(arg)
        UTIL_RemoveImmediate(arg)
        SrcPyTest_EntityArg(arg)
                