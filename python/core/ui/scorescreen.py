from vgui import surface, GetClientMode
from awesomium import DefaultWebView
import re

class ScoreWebView(DefaultWebView):
    matchfilename = 'test.xml'
    
    def __init__(self):
        super(ScoreWebView, self).__init__()
        
        self.SetZPos(5)

        self.SetVisible(False)
        #self.SetKeyBoardInputEnabled(True)
        self.SetMouseInputEnabled(True)
        
        w, h = surface().GetScreenSize()
        self.SetSize(int(w*0.8), int(h*0.7))
        self.SetPos(int(w*0.1), int(h*0.1))
        
    def OnDocumentReady(self, url):
        super(ScoreWebView, self).OnDocumentReady(url)
    
        self.SetTransparent(True)
        
        fp = open(self.matchfilename, 'rb')
        content = fp.read()
        fp.close()
        #self.CallJavascriptFunction(u'', u'showgraph', [content])
        content = re.escape(content)
        self.ExecuteJavascript("showgraph('%s');" % (content), '')
        print "showgraph('%s');" % (content)
        
    def ShowScores(self, matchfilename='test.xml'):
        self.matchfilename = matchfilename
        self.LoadFile('ui/scorescreen.html')
        self.SetMouseInputEnabled(True)
        self.SetVisible(True)
    
    '''
    def PerformLayout(self):
        super(ScoreWebView, self).PerformLayout()

        w, h = surface().GetScreenSize()

        self.SetSize(int(w*0.8), int(h*0.7))
        self.SetPos(int(w*0.1), int(h*0.1))
    '''
    
scorescreeninst = ScoreWebView()
#scorescreeninst.ShowScores()