from srcbase import Color, HIDEHUD_UNIT
from vgui import CHudElement, scheme, GetClientMode, CHudElementHelper, surface
from vgui.controls import Panel
from utils import UTIL_EntitiesInSphere, ScreenWidth, ScreenHeight
from entities import C_HL2WarsPlayer
from core.signals import playercontrolunit, playerleftcontrolunit

# Displays health bar of units that are near
# However looks annoying most of the time...
# class HudUnitDisplay(CHudElement, Panel):
    # def __init__(self):
        # CHudElement.__init__(self, "HudUnitDisplay")
        # Panel.__init__(self, GetClientMode().GetViewport(), "HudUnitDisplay")
        # self.SetHiddenBits( HIDEHUD_UNIT ) 
        
        # self.SetKeyBoardInputEnabled(False)
        # self.SetMouseInputEnabled(False)
        # self.SetPaintBackgroundEnabled(False)
        
    # def PerformLayout(self):
        # super(HudUnitDisplay, self).PerformLayout()
        
        # self.SetSize(ScreenWidth(), ScreenHeight())

    # def Paint(self):
        # super(HudUnitDisplay, self).Paint()
        
        # player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
        # if not player or not player.GetControlledUnit():
            # return
        
        # unit = player.GetControlledUnit().Get()
        
        # unitsnear = UTIL_EntitiesInSphere(16, unit.GetAbsOrigin(), 256, 0)
        # for u in unitsnear:
            # if not u or not u.IsAlive():
                # continue
            # if u.IsUnit() and u != unit:
                # u.OnHoverPaint()

# hudunitdisplay = CHudElementHelper( HudUnitDisplay() )


class HudUnitDisplayHealth(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudUnitDisplayHealth")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudUnitDisplayHealth")
        self.SetHiddenBits( HIDEHUD_UNIT ) 
        
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(False)
        self.SetPaintEnabled(False)
        self.SetPaintBackgroundEnabled(False)
        
        playercontrolunit.connect(self.OnPlayerControlUnit)
        playerleftcontrolunit.connect(self.OnPlayerLeftControlUnit)
        
    def UpdateOnDelete(self):
        playercontrolunit.disconnect(self.OnPlayerControlUnit)
        playerleftcontrolunit.disconnect(self.OnPlayerLeftControlUnit)
        
    def PerformLayout(self):
        super(HudUnitDisplayHealth, self).PerformLayout()
        
        self.SetSize( scheme().GetProportionalScaledValueEx( self.GetScheme(), 200 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 30 ) )
        self.SetPos( scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ),
                scheme().GetProportionalScaledValueEx( self.GetScheme(), 420 ) )
                
    def OnPlayerControlUnit(self, player, unit, **kwargs):
        if player != C_HL2WarsPlayer.GetLocalHL2WarsPlayer():
            return
        self.SetPaintEnabled(True)
        self.controlledunit = unit
        
    def OnPlayerLeftControlUnit(self, player, unit, **kwargs):
        if player != C_HL2WarsPlayer.GetLocalHL2WarsPlayer():
            return
        self.SetPaintEnabled(False)
        self.controlledunit = None
            
    def Paint(self):
        super(HudUnitDisplayHealth, self).Paint()

        unit = self.controlledunit
        if not unit:
            return
        
        maxhealth = max(1, max(unit.maxhealth, unit.health)) 
        weight = float(unit.health)/maxhealth
        
        red = 255 - int(weight * 255.0)
        green = int(weight * 255.0)

        width, tall = self.GetSize()
        xpos = 0
        ypos = 0
        left = int(weight*width)
        
        # draw how much health we still got
        surface().DrawSetColor( Color( red, green, 0, 255 ) )
        surface().DrawFilledRect( 0, 0, left, tall )       
        surface().DrawSetColor( Color( 255, 255, 255, 255 ) )
        surface().DrawOutlinedRect(0, 0, width, tall)        

hudunitdisplayhealth = CHudElementHelper( HudUnitDisplayHealth() )