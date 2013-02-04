from srcbase import Color, HIDEHUD_STRATEGIC
from vgui import GetClientMode, CHudElement, CHudElementHelper, scheme, AddTickSignal
from vgui.controls import Panel, Label
from utils import ScreenWidth

from core.usermessages import usermessage

class HudOverrun(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudOverrun")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudOverrun")
        self.SetHiddenBits( HIDEHUD_STRATEGIC ) 
        
        self.SetPaintBackgroundEnabled(True)
        
        schemeobj = scheme().LoadSchemeFromFile("resource/GameLobbyScheme.res", "GameLobbyScheme")
        self.SetScheme(schemeobj)
        
        self.waveinfo = Label(self, "WaveInfo", 'Hai')
        self.waveinfo.SetContentAlignment(Label.a_west)
        self.UpdateWaveMessage()
        
        # Register UpdateWaveInfo as usermessage
        self.UpdateWaveInfo = usermessage('overrun.waveupdate')(self.UpdateWaveInfo)
        
        AddTickSignal(self.GetVPanel(), 250)
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudOverrun, self).ApplySchemeSettings(schemeobj)
        hfontmedium = schemeobj.GetFont( 'HeadlineLarge' )
        self.waveinfo.SetFont(hfontmedium)
        
    def PerformLayout(self):
        super(HudOverrun, self).PerformLayout()
        
        self.waveinfo.SizeToContents()
        
        self.SetSize( self.waveinfo.GetWide(),
            scheme().GetProportionalScaledValueEx( self.GetScheme(), 20 ) )

        offset = scheme().GetProportionalScaledValueEx( self.GetScheme(), 5 )
        self.SetPos( ScreenWidth()-self.waveinfo.GetWide()-offset, offset ) 
        
    def OnTick(self):
        super(HudOverrun, self).OnTick()
        
        self.UpdateWaveMessage()
            
    def UpdateWaveMessage(self):
        if self.nextwavetime < gpGlobals.curtime:
            self.waveinfo.SetText('Wave %d in progress!' % (self.wave+1))
        elif not self.wave:
            self.waveinfo.SetText('First wave in %d seconds!' % (int(self.nextwavetime - gpGlobals.curtime)))
        else:
            self.waveinfo.SetText('Next wave in %d seconds!' % (int(self.nextwavetime - gpGlobals.curtime)))
            
    def UpdateWaveInfo(self, wave, nextwavetime, **kwargs):
        self.wave = wave
        self.nextwavetime = nextwavetime
        
        self.UpdateWaveMessage()
        self.PerformLayout()

    wave = 0
    nextwavetime = 0.0
