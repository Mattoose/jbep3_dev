from srcbase import Color
from vgui import GetClientMode, scheme
from vgui.controls import Panel, Label, Button
from utils import ScreenWidth
from gameinterface import engine

class VoteDialog(Panel):
    def __init__(self):
        super(VoteDialog, self).__init__(GetClientMode().GetViewport(), "VoteDialog")
       
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        
        self.SetPaintBackgroundEnabled(True)
        self.SetVisible(True)
        self.SetMouseInputEnabled(True)
        
        self.yesvotes = 0
        self.novotes = 0

        self.question = Label(self, "Question", "Return to lobby? (yes: %d, no: %d)" % (self.yesvotes, self.novotes))
        
        # Vote buttons
        self.yes = Button(self, "Yes", "Yes")
        self.yes.SetCommand('yes')
        self.yes.SetScheme(schemeobj)
        self.yes.AddActionSignalTarget(self)
        
        self.no = Button(self, "No", "No")
        self.no.SetCommand('no')
        self.no.SetScheme(schemeobj)
        self.no.AddActionSignalTarget(self)
        
    def ApplySchemeSettings(self, schemeobj):
        super(VoteDialog, self).ApplySchemeSettings(schemeobj)
        hfontmedium = schemeobj.GetFont('MenuLarge')
        
        self.SetBorder( schemeobj.GetBorder('ButtonBorder') )
        self.SetBgColor( schemeobj.GetColor('TransparentGray', Color(255, 255, 255 ) ) )

        self.question.SetFont(hfontmedium)
        self.yes.SetFont(hfontmedium)
        self.no.SetFont(hfontmedium)
        
    def PerformLayout(self):
        super(VoteDialog, self).PerformLayout()
        
        self.SetPos( ScreenWidth() - scheme().GetProportionalScaledValueEx( self.GetScheme(), 210 ),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 15 ) )
        self.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 200 ),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 100 ) )

        self.question.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 25 ), 
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 10 ) )
        self.question.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 150 ),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 40 ) )
            
        self.yes.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 13 ), 
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 70 ) )
        self.yes.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 75 ),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ) )
            
        self.no.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 113 ), 
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 70 ) )
        self.no.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 75 ),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ) )
            
    def OnCommand(self, command):
        self.yes.SetEnabled(False)
        self.no.SetEnabled(False)
        
        engine.ServerCommand('gl_vote %s' % (command))
