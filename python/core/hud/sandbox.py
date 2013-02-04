from vgui import surface, GetClientMode, CHudElement, CHudElementHelper, scheme, AddTickSignal, RemoveTickSignal
from vgui.controls import Panel, Button
from gameinterface import engine
from entities import C_HL2WarsPlayer
from utils import ScreenWidth, ScreenHeight
from core.signals import playercontrolunit, playerleftcontrolunit

class HudSandbox(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudSandbox")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudSandbox")

        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        
        self.SetPaintEnabled(False)
        self.SetPaintBackgroundEnabled(False)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)

        self.unitpanel = Button(self, "UnitPanelButton", 'Units')
        self.unitpanel.SetCommand('unitpanel')
        self.unitpanel.SetScheme(schemeobj)
        self.unitpanel.AddActionSignalTarget(self)
        self.abilitypanel = Button(self, "AbilityPanelButton", 'Abilities')
        self.abilitypanel.SetCommand('abilitypanel')
        self.abilitypanel.SetScheme(schemeobj)
        self.abilitypanel.AddActionSignalTarget(self)
        '''self.attributeeditor = Button(self, "AttributeEditorButton", 'Attribute Editor')
        self.attributeeditor.SetCommand('attributemodifiertool')
        self.attributeeditor.SetScheme(schemeobj)
        self.attributeeditor.AddActionSignalTarget(self)
        self.playereditor = Button(self, "PlayerEditorButton", 'Player Editor')
        self.playereditor.SetCommand('playermodifiertool')
        self.playereditor.SetScheme(schemeobj)
        self.playereditor.AddActionSignalTarget(self)'''
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudSandbox, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        
        self.unitpanel.SetFont(hfontsmall)
        self.abilitypanel.SetFont(hfontsmall)
        #self.attributeeditor.SetFont(hfontsmall)
        #self.playereditor.SetFont(hfontsmall)
        
    def PerformLayout(self):
        super(HudSandbox, self).PerformLayout()
        
        bwidth = scheme().GetProportionalScaledValueEx(self.GetScheme(), 60)
        bheight = scheme().GetProportionalScaledValueEx(self.GetScheme(), 15)
        
        self.SetPos(0, 0)
        self.SetSize(bwidth*4, bheight)
            
        self.unitpanel.SetSize(bwidth, bheight)

        self.abilitypanel.SetSize(bwidth, bheight)
        self.abilitypanel.SetPos(bwidth, 0)
            
        #self.attributeeditor.SetSize(bwidth, bheight)
        #self.attributeeditor.SetPos(bwidth*2, 0)
            
        #self.playereditor.SetSize(bwidth, bheight)
        #self.playereditor.SetPos(bwidth*3, 0)
            
    def OnCommand(self, command):
        engine.ClientCommand(command)
        
class HudDirectControl(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudDirectControl")
        Panel.__init__(self, GetClientMode().GetViewport(), "HudDirectControl")
        
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        
        self.SetPaintEnabled(False)
        self.SetPaintBackgroundEnabled(False)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)
        
        self.button = Button(self, 'DirectControlButton', 'Control Unit')
        self.button.SetCommand('controlunit')
        self.button.SetScheme(schemeobj)
        self.button.AddActionSignalTarget(self)

        playercontrolunit.connect(self.OnPlayerControlUnit)
        playerleftcontrolunit.connect(self.OnPlayerLeftControlUnit)
        
    def UpdateOnDelete(self):
        playercontrolunit.disconnect(self.OnPlayerControlUnit)
        playerleftcontrolunit.disconnect(self.OnPlayerLeftControlUnit)
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudDirectControl, self).ApplySchemeSettings(schemeobj)
        
        hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        self.button.SetFont(hfontsmall)
        self.button.SetContentAlignment(Button.a_center)
        
    def PerformLayout(self):
        super(HudDirectControl, self).PerformLayout()
 
        self.SetPos(ScreenWidth() - scheme().GetProportionalScaledValueEx(self.GetScheme(), 50), 0)
        self.SetSize( scheme().GetProportionalScaledValueEx(self.GetScheme(), 50),
            scheme().GetProportionalScaledValueEx(self.GetScheme(), 25))
            
        self.button.SetSize(scheme().GetProportionalScaledValueEx(self.GetScheme(), 50),
            scheme().GetProportionalScaledValueEx(self.GetScheme(), 20 ))
            
    def OnCommand(self, command):
        if command == 'controlunit':
            player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer()
            if not player:
                return
            engine.ClientCommand('wars_abi controlunit')
            
    def OnPlayerControlUnit(self, player, unit, **kwargs):
        self.button.SetText('Leave Control\n(hold shift)')
        
    def OnPlayerLeftControlUnit(self, player, unit, **kwargs):
        self.button.SetText('Control Unit')
            
