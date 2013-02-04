
from vgui.controls import WebView, DefaultWebView
from vgui import GetPanel, PANEL_GAMEUIDLL, ipanel
from utils import ScreenWidth, ScreenHeight
from gameinterface import ConVarRef

g_debug_webview = ConVarRef('g_debug_webview')
g_debug_webview.SetValue("2")

class MainMenu(DefaultWebView):
    #def __init__(self, *args, **kwargs):
    #    super(MainMenu, self).__init__(*args, **kwargs)
    #    
    #    self.SetViewListener(self)

    def OnChangeCursor(self, webview, cursor):
        super(MainMenu, self).OnChangeCursor(webview, cursor)
        print 'change cursor: ' + str(cursor)
        
gameuiroot = GetPanel(PANEL_GAMEUIDLL)
gameuibasepanel = gameuiroot
for i in range(0, ipanel().GetChildCount(gameuiroot)):
    vp = ipanel().GetChild(gameuiroot, i)
    print ipanel().GetName(vp)
    if ipanel().GetName(vp) == 'CBaseModPanel':
        gameuibasepanel = vp
        print 'found game base panel'
        break
        
gameuimenu = gameuibasepanel
for i in range(0, ipanel().GetChildCount(gameuibasepanel)):
    vp = ipanel().GetChild(gameuibasepanel, i)
    print ipanel().GetName(vp)
    if ipanel().GetName(vp) == 'MainMenu':
        gameuimenu = vp
        print 'found game menu'
        break
        
#ipanel().SetVisible(gameuibasepanel, False)
        
webview = MainMenu(None, 'TestWebView')
webview.SetParent(gameuimenu)
webview.SetMouseInputEnabled(True)
webview.SetKeyBoardInputEnabled(True)
webview.SetSize(ScreenWidth(), ScreenHeight())
webview.SetPos(0, 0)
webview.SetPassMouseTruIfAlphaZero(True)
webview.LoadFile('ui/mainmenu.html')