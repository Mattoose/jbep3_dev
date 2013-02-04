from srcbase import Color, HIDEHUD_STRATEGIC
from vgui import surface, GetClientMode, CHudElement, CHudElementHelper, scheme, FontDrawType_t
from vgui.controls import Panel
from utils import GetVectorInScreenSpace, ScreenWidth, ScreenHeight
from gamerules import GameRules
    
class HudResourceIndicator(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudResourceIndicator")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudResourceIndicator")
        self.SetHiddenBits(HIDEHUD_STRATEGIC) 
        
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(False)
        self.SetPaintBackgroundEnabled(False)
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
        self.displaying = []
        
    def LevelInit(self):
        # Reset
        self.displaying = []
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudResourceIndicator, self).ApplySchemeSettings(schemeobj)
        
        self.hfontsmall = schemeobj.GetFont( "HeadlineLarge" )
        
    def PerformLayout(self):
        super(HudResourceIndicator, self).PerformLayout()
        
        self.SetSize(ScreenWidth(), ScreenHeight())
            
    def Add(self, origin, num):
        self.displaying.append( (gpGlobals.curtime, origin, num) )

    def Paint(self):
        if not self.displaying:
            return
        for k in list(self.displaying):
            lifetime = gpGlobals.curtime - k[0]
            weight = max(0.0, 1.0 - lifetime/self.LIFE_TIME)
            
            result, x, y = GetVectorInScreenSpace(k[1]) 
        
            s = surface()
            s.DrawSetTextFont(self.hfontsmall)
            s.DrawSetTextColor(255, 255, 255, int(weight*255))
            s.DrawSetTextPos(x, int(y-(1.0-weight)*scheme().GetProportionalScaledValueEx(self.GetScheme(), 20)) )
            s.DrawUnicodeString('%s' % (k[2]), FontDrawType_t.FONT_DRAW_DEFAULT)
            
            if lifetime > self.LIFE_TIME:
                self.displaying.remove(k)
                
    LIFE_TIME = 2.5

hudresourceindicator = CHudElementHelper(HudResourceIndicator())
