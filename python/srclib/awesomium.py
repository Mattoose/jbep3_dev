from _awesomium import *
from vgui import CursorCode
 
import weakref
import re
import traceback

from gameinterface import concommand, ConVarRef, engine

class ViewListener(object):
    def OnChangeTitle(self, title): pass
    def OnChangeAddressBar(self, url): pass
    def OnChangeTooltip(self, tooltip): pass
    def OnChangeTargetURL(self, url): pass
    def OnChangeCursor(self, cursor): pass
    def OnChangeFocus(self, focused_type): pass
    def OnShowCreatedWebView(self, opener_url, target_url): pass
    
class LoadListener(object):
    def OnBeginLoadingFrame(self, frame_id, is_main_frame, url, is_error_page): pass
    def OnFailLoadingFrame(self, frame_id, is_main_frame, url, error_code, error_desc): 
        PrintWarning('Failed to load frame (code: %d): %s\n' % (error_code, error_desc))
    def OnFinishLoadingFrame(self, frame_id, is_main_frame, url): pass
    def OnDocumentReady(self, url): pass
    
class ProcessListener(object):
    def OnUnresponsive(self): print '%s unresponsive' % (str(self))
    def OnResponsive(self):  print '%s responsive' % (str(self))
    def OnCrashed(self, status):  print '%s crashed' % (str(self))
    
class DefaultWebView(WebView, ViewListener, LoadListener, ProcessListener):
    def __init__(self, *args, **kwargs):
        self.refself = self
    
        WebView.__init__(self, *args, **kwargs)
        ViewListener.__init__(self)
        LoadListener.__init__(self)
        ProcessListener.__init__(self)
        
        self.SetViewListener(self)
        self.SetLoadListener(self)
        self.SetProcessListener(self)
        
        self.SetPassMouseTruIfAlphaZero(True)
        self.SetZPos(-1000)
 
    def Shutdown(self):
        self.refself = None
        self.Clear()
        
    def OnDocumentReady(self, url):
        self.CreateCallbacks()
        self.SetMouseInputEnabled(True)

    def CreateCallbacks(self):
        self.objpanel = self.CreateGlobalJavascriptObject('panel')
        self.objpanel.SetCustomMethod('close', False)
        self.objpanel.SetCustomMethod('setVisible', False)
        
        self.objinterface = self.CreateGlobalJavascriptObject('interface')
        self.objinterface.SetCustomMethod('clientCommand', False)
        self.objinterface.SetCustomMethod('serverCommand', False)
        self.objinterface.SetCustomMethod('getConVarValue', True)
        
    def OnMethodCall(self, remote_object_id, methodname, args):
        print 'method call %s' % (methodname)
        
        if remote_object_id == self.objpanel.remote_id():
            if methodname == 'close':
                self.Shutdown()
            elif methodname == 'setVisible':
                self.SetVisible(args[0])
        elif remote_object_id == self.objinterface.remote_id():
            if methodname == 'clientCommand':
                engine.ClientCommand(args[0].encode('ascii','ignore'))
            elif methodname == 'serverCommand':
                engine.ServerCommand(args[0].encode('ascii','ignore'))
            elif methodname == 'getConVarValue':
                ref = ConVarRef(args[0].encode('ascii','ignore'))
                return ref.GetString()

    # TODO: Cursors
    cursormap = {
        Cursor.kCursor_Pointer : CursorCode.dc_arrow,
        Cursor.kCursor_Cross : CursorCode.dc_crosshair,
        Cursor.kCursor_Hand : CursorCode.dc_hand,
        Cursor.kCursor_IBeam : CursorCode.dc_ibeam,
        Cursor.kCursor_Wait : CursorCode.dc_hourglass,
        Cursor.kCursor_Help : CursorCode.dc_arrow,
        Cursor.kCursor_EastResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthEastResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthWestResize : CursorCode.dc_arrow,
        Cursor.kCursor_SouthResize : CursorCode.dc_arrow,
        Cursor.kCursor_SouthEastResize : CursorCode.dc_arrow,
        Cursor.kCursor_SouthWestResize : CursorCode.dc_arrow,
        Cursor.kCursor_WestResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthSouthResize : CursorCode.dc_arrow,
        Cursor.kCursor_EastWestResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthEastSouthWestResize : CursorCode.dc_arrow,
        Cursor.kCursor_NorthWestSouthEastResize : CursorCode.dc_arrow,
        Cursor.kCursor_ColumnResize : CursorCode.dc_arrow,
        Cursor.kCursor_RowResize : CursorCode.dc_arrow,
        Cursor.kCursor_MiddlePanning : CursorCode.dc_arrow,
        Cursor.kCursor_EastPanning : CursorCode.dc_arrow,
        Cursor.kCursor_NorthPanning : CursorCode.dc_arrow,
        Cursor.kCursor_NorthEastPanning : CursorCode.dc_arrow,
        Cursor.kCursor_NorthWestPanning : CursorCode.dc_arrow,
        Cursor.kCursor_SouthPanning : CursorCode.dc_arrow,
        Cursor.kCursor_SouthEastPanning : CursorCode.dc_arrow,
        Cursor.kCursor_SouthWestPanning : CursorCode.dc_arrow,
        Cursor.kCursor_WestPanning : CursorCode.dc_arrow,
        Cursor.kCursor_Move : CursorCode.dc_arrow,
        Cursor.kCursor_VerticalText : CursorCode.dc_arrow,
        Cursor.kCursor_Cell : CursorCode.dc_arrow,
        Cursor.kCursor_ContextMenu : CursorCode.dc_arrow,
        Cursor.kCursor_Alias : CursorCode.dc_arrow,
        Cursor.kCursor_Progress : CursorCode.dc_arrow,
        Cursor.kCursor_NoDrop : CursorCode.dc_arrow,
        Cursor.kCursor_Copy : CursorCode.dc_arrow,
        Cursor.kCursor_None : CursorCode.dc_blank,
        Cursor.kCursor_NotAllowed : CursorCode.dc_arrow,
        Cursor.kCursor_ZoomIn : CursorCode.dc_arrow,
        Cursor.kCursor_ZoomOut : CursorCode.dc_arrow,
        Cursor.kCursor_Custom : CursorCode.dc_arrow,
    }
    
    def OnChangeCursor(self, cursor):
        self.SetCursor(self.cursormap.get(cursor, self.GetCursor()))
            
    def OnChangeFocus(self, focused_type):
        print('Focus change: %s' % (focused_type))
        # by default, change keyboard input on focus change
        if focused_type == kFocusedElementType_None:
            self.SetKeyBoardInputEnabled(False) 
        else:
            self.SetKeyBoardInputEnabled(True) 
            
    '''
    def OnWebViewCrashed(self):
        PrintWarning('Webview crashed :(\n')

    def OnJavascriptConsoleMessage(self, message, linenumber, source):
        PrintWarning('%d: %s -> %s\n' % (linenumber, source, message))
        
    def OnShowJavascriptDialog(self, requestID, dialogFlags, message, defaultPrompt, frameURL):
        self.CloseJavascriptDialog(requestID, True, u'') # Must close, otherwise the page is frozen!
    '''
    
    refself = None
    
    
class Viewport(DefaultWebView):
    ''' Viewport. Covers the whole screen.'''
    def __init__(self):
        super(Viewport, self).__init__()
        
        self.panels = []
        self.objects = {}
    
    def Load(self):
        self.LoadFile('ui/viewport.html')
        
    def OnSizeChanged(self, newwidth, newtall):
        self.ReloadViewport()

    def PerformLayout(self):
        w, h = surface().GetScreenSize()
        #print('Initialized webview viewport with size: %d %d' % (w, h))
        self.SetSize(w, h)

    def ReloadViewport(self):
        self.Reload(False)
        #self.Load()
        
        panels = list(self.panels)
        self.panels = []
        
        for p in panels:
            print('Reloading %s' % (p.name))
            try:
                self.AddElement(p)
                p.OnReloaded()
            except:
                traceback.print_exc()
                self.panels.append(p) # Add panel anyway, otherwise we lose it if we reload again
    
    def OnDocumentReady(self, url):
        super(Viewport, self).OnDocumentReady(url)
        
        self.SetTransparent(True)
        
    def OnMethodCall(self, remote_object_id, methodname, args):
        #print 'Viewport method call %s. Args: %s' % (methodname, str(args))
        if remote_object_id in self.objects:
            fn = getattr(self.objects[remote_object_id], methodname)
            return fn(*args)
        return super(Viewport, self).OnMethodCall(remote_object_id, methodname, args)
        
    def AddElement(self, e):
        e.LoadCode()
    
        e.obj = self.CreateGlobalJavascriptObject(e.name+'_obj')
        e.obj.SetCustomMethod('getJSCode', True)
        e.obj.SetCustomMethod('getHTMLCode', True)
        
        self.objects[e.obj.remote_id()] = e
        
        self.panels.append(e)
        
        e.element = self.ExecuteJavascriptWithResult("insertElement('%s');" % (e.name), '')
        
        e.OnLoaded()
        e.SetVisible(e.visible) # Make sure it's set to the correct vibility state

    def RemoveElement(self, e):
        assert(e.element)
        
        self.panels.remove(e)
        
        self.ExecuteJavascript("removeElement('%s');" % (e.name), '')
        
    def InsertCSSFile(self, filename):
        self.ExecuteJavascript("insertCss('%s');" % (filename), '')
        
    def InsertJSFile(self, filename):
        self.ExecuteJavascript("insertJavascript('%s');" % (filename), '')
        
class WPanel(object):
    htmlfile = ''
    jsfile = ''
    element = None
    obj = None
    selfref = None
    visible = False
    
    def __init__(self, viewport, name, htmlfile=None, jsfile=None):
        super(WPanel, self).__init__()
        
        if htmlfile: self.htmlfile = htmlfile
        if jsfile: self.jsfile = jsfile
        
        self.name = name
        self.viewport = viewport

        viewport.AddElement(self)
        
        self.selfref = self

    def Remove(self):
        viewport.RemoveElement(self)
        self.selfref = None
        
    def LoadCode(self):
        try:
            fp = open(self.htmlfile, 'rb')
            self.htmlcode = fp.read()
            fp.close()
        except IOError:
            PrintWarning('%s: invalid html file specified (%s)\n' % (self.name, self.htmlfile))
            self.htmlcode = ''
                
        if self.jsfile:
            try:
                fp = open(self.jsfile, 'rb')
                self.jscode = fp.read()
                fp.close()
            except IOError:
                PrintWarning('%s: invalid js file specified (%s)\n' % (self.name, self.jsfile))
                self.jscode = ''
        else:
            self.jscode = ''
        
    def OnLoaded(self):
        pass
        
    def OnReloaded(self):
        pass
        
    def getHTMLCode(self):
        return self.htmlcode
        
    def getJSCode(self):
        return self.jscode
       
    def SetVisible(self, visible):
        #if self.visible == visible:
        #    return
        if visible:
            self.viewport.ExecuteJavascript('%s.content.show()' % (self.name), '')
        else:
            self.viewport.ExecuteJavascript('%s.content.hide()' % (self.name), '')
        self.visible = visible
        
    def IsVisible(self):
        return self.visible
        
    # TODO:
    def SetEnabled(self, enabled):
        pass
        
    def RequestFocus(self):
        pass
        
    def MoveToFront(self):
        pass
    
# Create the viewport
from vgui import surface
viewport = Viewport()
viewport.Load()

@concommand('awe_reload_viewport')
def CCReloadViewport(args):
    viewport.ReloadViewport()
    
# Test code
testelements = []

@concommand('awe_test_insert_draggable')
def CCTestInsertDraggable(args):
    testelements.append(WPanel(viewport, 'draggable_%d' % (len(testelements)), 
                               htmlfile='ui/testelement.html', jsfile='ui/testelement.js'))

@concommand('awe_test_remove_draggable')
def CCTestRemoveDraggable(args):
    e = testelements.pop()
    e.Remove()