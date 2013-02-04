from srcbase import Color
from vgui import GetClientMode, scheme
from vgui.controls import Panel
from utils import ScreenWidth, ScreenHeight

from gamelobby_loadingpanel import glloadingdialog

class GLWaitForPlayersPanel(Panel):
    def __init__(self):
        super(GLWaitForPlayersPanel, self).__init__(None, "WaitingForPlayersPanel")
        
        self.SetParent( GetClientMode().GetViewport() )
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme( schemeobj )
        
        self.SetVisible(False)

        self.SetSize( ScreenWidth(), ScreenHeight() )
        
    def ApplySchemeSettings(self, scheme_obj):
        super(GLWaitForPlayersPanel, self).ApplySchemeSettings(scheme_obj)
        
        self.SetBgColor( Color(50, 50, 50, 150) )
        
    def Paint(self):
        super(GLWaitForPlayersPanel, self).Paint()
        
        # Lame HAX
        glloadingdialog.SetParent(self)
        glloadingdialog.SetVisible(True)
        
        glloadingdialog.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 250),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 380)) 
        glloadingdialog.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 100),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 40)) 
        
        
    def ShowPanel(self, show):
        if self.IsVisible() == show:
            return

        if show:
            self.SetVisible( True )

            glloadingdialog.SetParent(self)
            glloadingdialog.SetVisible(True)
            
            glloadingdialog.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 350)) 
            glloadingdialog.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 150),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 80))               
        else:
            self.SetVisible( False )
            glloadingdialog.SetParent(None)
            glloadingdialog.SetVisible(False)

wfp = GLWaitForPlayersPanel()