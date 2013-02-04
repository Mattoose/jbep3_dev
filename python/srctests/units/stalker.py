from unittest import TestSuite, TestCase
from core.units import CreateUnit
from vmath import vec3_origin

import sys

def CreateStalkerTestSuite():
    suite = TestSuite()
    suite.addTest(StalkerTestCase('test_spawn'))
    return suite

class StalkerTestCase(TestCase):
    def setUp(self):
        pass
        
    def test_spawn(self):
        # Clear last_traceback
        try: del sys.last_traceback
        except: pass
        
        unit = CreateUnit('unit_stalker', vec3_origin)
        
        self.assertIsNotNone(unit)
        self.assertRaises(AttributeError, lambda: sys.last_traceback)
        