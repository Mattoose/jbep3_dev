from srcbase import HIDEHUD_STRATEGIC, Color
from vgui import CHudElement, GetClientMode, scheme
from vgui.controls import Panel
from core.hud import HudInfo

class HudCombine(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudCombine")
        Panel.__init__(self, None, "HudCombine")
        self.SetParent( GetClientMode().GetViewport() )
        self.SetHiddenBits( HIDEHUD_STRATEGIC )

    def ApplySchemeSettings(self, scheme_obj):
        super(HudCombine, self).ApplySchemeSettings(scheme_obj)

        self.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 0),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 380))
        wide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 640)
        tall = scheme().GetProportionalScaledValueEx(self.GetScheme(), 100)
        self.SetSize(wide, tall)
        
        self.SetBgColor( Color(0,0,205,200) )        
        
class CombineHudInfo(HudInfo):
    name = 'combine_hud'
    cls = HudCombine