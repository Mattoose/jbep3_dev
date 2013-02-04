"""
Defines the loading screen.
"""

from srcbase import Color, KeyValues
from vgui import GetClientMode, SetLoadingBackgroundDialog, scheme
from vgui.controls import Panel, Label
from utils import ScreenWidth, ScreenHeight
from gameinterface import engine
import os

class BindingsPanel(Panel):
    def __init__(self, parent):
        super(BindingsPanel, self).__init__(parent, "BindingsPanel")
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
        self.title = Label(self, 'title', 'Configuration')
        
        self.bindinglabels = []
        for b in self.bindings:
            self.bindinglabels.append( 
                (Label(self, b[0], engine.Key_LookupBinding(b[0])), Label(self, '%s_description' % (b[0]), b[1])),
            )
            
    def ApplySchemeSettings(self, schemeobj):
        super(BindingsPanel, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont( "DefaultBold" )
        self.title.SetFont(schemeobj.GetFont( "MenuLarge" ))
        for b in self.bindinglabels:
            b[0].SetFont(hfontsmall)
            b[1].SetFont(hfontsmall)
            
    def PerformLayout(self):
        super(BindingsPanel, self).PerformLayout()
        
        y = scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
        dy = scheme().GetProportionalScaledValueEx(self.GetScheme(), 10)
        x1 = scheme().GetProportionalScaledValueEx(self.GetScheme(), 4)
        x2 = scheme().GetProportionalScaledValueEx(self.GetScheme(), 34)
        
        self.title.SizeToContents()
        self.title.SetPos(0, y)
        
        y += scheme().GetProportionalScaledValueEx(self.GetScheme(), 12)
        
        for b in self.bindinglabels:
            b[0].SizeToContents()
            b[0].SetPos(x1, y)
            b[1].SizeToContents()
            b[1].SetPos(x2, y)
            y += dy
            
        y += scheme().GetProportionalScaledValueEx(self.GetScheme(), 5)
            
        self.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 250), y)
        
    bindings = [
        ('+duck', 'Bind/select groups combined with numbers 1-9'),
        ('+speed', 'Queue unit orders'),
        ('gl_callvote', 'Call gamelobby vote'),
        ('+walk', 'Look around with the camera'),
    ]

class LoadingDialog(Panel):
    def __init__(self):
        super(LoadingDialog, self).__init__(None, "LoadingDialog")
        
        self.SetParent( GetClientMode().GetViewport() )
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
        self.SetVisible(False)
        self.MakePopup(False)

        self.SetSize( ScreenWidth(), ScreenHeight() )
        
        self.levelname = Label(self, 'LevelName', 'Loading....')
        
        self.bindingspanel = BindingsPanel(self)
        
    def ApplySchemeSettings(self, schemeobj):
        super(LoadingDialog, self).ApplySchemeSettings(schemeobj)
        
        self.SetBgColor( Color(50, 50, 50, 150) )
        self.levelname.SetFgColor( Color(255, 255, 255, 255) )
        self.levelname.SetFont( schemeobj.GetFont("MenuLarge", self.IsProportional() ) )

    def PerformLayout(self):
        super(LoadingDialog, self).PerformLayout()
        
        self.levelname.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 25),
             scheme().GetProportionalScaledValueEx(self.GetScheme(), 50))  
             
        halfw = int(round(ScreenWidth()/2.0))
        self.bindingspanel.SetPos( halfw + scheme().GetProportionalScaledValueEx(self.GetScheme(), 40),
             scheme().GetProportionalScaledValueEx(self.GetScheme(), 80))  

    def Paint(self):
        super(LoadingDialog, self).Paint()
        
        from glpkg import gamelobbyrules, ui # FIXME
        glloadingdialog = ui.gamelobby_loadingpanel.glloadingdialog
        if gamelobbyrules.state == gamelobbyrules.GAMELOBBY_WAITINGFORPLAYERS:
            glloadingdialog.SetParent(self)
            glloadingdialog.SetVisible(True)
            
            glloadingdialog.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 200),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 350)) 
            glloadingdialog.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 150),
                         scheme().GetProportionalScaledValueEx(self.GetScheme(), 80))   
        elif glloadingdialog.GetParent() == self:
            glloadingdialog.SetParent(None)
            glloadingdialog.SetVisible(False)
        
        mapname = os.path.splitext(os.path.basename(engine.GetLevelName()))[0]
        self.levelname.SetText('Loading %s....' % (mapname))
        self.levelname.SizeToContents()

loadingdialog = LoadingDialog()   
SetLoadingBackgroundDialog(loadingdialog)
   