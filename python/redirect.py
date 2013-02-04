""" 
Redirect sys.stdout and sys.stderr to the builtin methods Msg and PrintWarning.
These methods will print the output in the console. 
Don't add any other imports here. Don't break this. This will likely be merged into python itself later.
"""

import sys
import __builtin__

#from srcbase import Color

interpreterwindow = None

# This object will replace sys.stdout and redirect to Msg()
class StdoutToMsg:
    def __init__(self):
        return
    def write(self, string):
        __builtin__.Msg(string)
        #if interpreterwindow != None:
        #    interpreterwindow.history.InsertColorChange( Color( 255, 255, 255, 255 ) )
        #    interpreterwindow.history.InsertString(string)
    def flush(self):
        pass
    def fileno(self):
        return 0
        
# This object will replace sys.stderr and redirect to Warning()
class StderrToWarning:
    def __init__(self):
        return
    def write(self, string):
        __builtin__.PrintWarning(string)
        #if interpreterwindow != None:
        #    interpreterwindow.history.InsertColorChange( Color( 255, 0, 0, 255 ) )
        #    interpreterwindow.history.InsertString(string)
    def flush(self):
        pass
        
# Redirect print
sys.stdout = StdoutToMsg()       
sys.stderr = StderrToWarning()