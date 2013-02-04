import sys
import unittest

from gameinterface import ConVarRef

import converters
from units.stalker import CreateStalkerTestSuite

py_disable_protect_path = ConVarRef('py_disable_protect_path')

def RunTests():
    sys.argv = ['hl2wars']
    
    py_disable_protect_path.SetValue(True)
    
    print('Testing converters...')
    suite = converters.CreateConverterTestSuite()
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = CreateStalkerTestSuite()
    unittest.TextTestRunner(verbosity=2).run(suite)
    
    py_disable_protect_path.SetValue(False)