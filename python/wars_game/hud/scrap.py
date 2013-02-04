from srcbase import Color
from entities import C_HL2WarsPlayer
from core.hud import BaseHudSingleUnit
from vgui.controls import Label

class HudBuildScrap(BaseHudSingleUnit):
    def __init__(self, parent):    
        super(HudBuildScrap, self).__init__(parent)
        
        self.scrap = Label(self, "ScrapLeft", "")
        
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudBuildScrap, self).ApplySchemeSettings(schemeobj)
        
        self.scrap.SetFgColor(Color(255,255,255,255))
        self.scrap.SetBgColor(Color(200,200,200,0))
        
    def PerformLayout(self):
        super(HudBuildScrap, self).PerformLayout()
        
        x, y = self.GetPos()
        w, h = self.GetSize()
        self.scrap.SetPos(int(w*0.01), int(h*0.35))
        self.scrap.SetSize(int(w*1.0), int(h*0.1))
        
    def Update(self):
        super(HudBuildScrap, self).Update()
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        if not player or player.CountUnits() != 1:
            return
            
        unit = player.GetUnit(0)
        
        self.scrap.SetText('Scrap Left: %d' % (unit.scrap))
