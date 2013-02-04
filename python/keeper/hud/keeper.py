from srcbase import HIDEHUD_STRATEGIC, Color
from vgui import CHudElement, GetClientMode, scheme
from vgui.controls import Panel, Button, Label
from core.hud import HudInfo
from core.resources import resources
from core.signals import resourceset, refreshhud
from core.abilities import GetAbilityInfo
from gameinterface import engine
from entities import CBasePlayer
from gamerules import gamerules

from awesomium import WPanel, viewport

class HudKeeper(WPanel):
    htmlfile = 'ui/keeper/keeper.html'
    jsfile = 'ui/keeper/keeper.js'
    
    goldamount = 0
    maxgold = 0
    
    def __init__(self):
        super(HudKeeper, self).__init__(viewport, 'HudKeeper')

        resourceset.connect(self.OnResourceSet)
        refreshhud.connect(self.OnRefreshHud)
        
    def Remove(self):
        super(HudKeeper, self).Remove()
        
        resourceset.disconnect(self.OnResourceSet)
        refreshhud.disconnect(self.OnRefreshHud)
        
    def OnLoaded(self):
        super(HudKeeper, self).OnLoaded()
    
        self.SetVisible(True)

        self.obj.SetCustomMethod('onCommand', False)
        
        self.buttons = [
            ('CreateImp', 'Create Imp', 'createimp', '#swarmkeeper_spells'),
            ('PossessCreature', 'Possess Creature', 'possesscreature', '#swarmkeeper_spells'),
            ('Lighting', 'Lighting', 'lighting', '#swarmkeeper_spells'),
            
            ('CreateTreasureRoom', 'Treasure', 'createtreasureroom', '#swarmkeeper_rooms'),
            ('CreateLair', 'Lair', 'createlair', '#swarmkeeper_rooms'),
            ('CreateHatchery', 'Hatchery', 'createhatchery', '#swarmkeeper_rooms'),
            ('CreateTraining', 'Training', 'createtraining', '#swarmkeeper_rooms'),
            ('CreateLibrary', 'Library', 'createlibrary', '#swarmkeeper_rooms'),
            ('CreateWorkshop', 'Workshop', 'createworkshop', '#swarmkeeper_rooms'),
            
            ('SellRoom', 'Sell', 'sellroom', '#swarmkeeper_rooms'),
        ]
        
        self.buttoninst = []
        for b in self.buttons:
            abi = GetAbilityInfo(b[2])
            if not abi:
                continue
            
            if abi.costs: gold = abi.costs[0][0][1]
            else: gold = None
            
            setattr(self, 'button%s' % (b[0].lower()), 
                self.element.Invoke("insertItem", [b[3], b[2], '%s (%s)' % (b[1], gold) if gold else b[1]]))
                
        player = CBasePlayer.GetLocalPlayer()
        self.maxgold = gamerules.maxgold
        if player: self.SetGold(resources[player.GetOwnerNumber()]['gold'])
    
    def OnResourceSet(self, ownernumber, type, amount, **kwargs):
        if type == 'gold':
            self.SetGold(amount)
            
    def OnRefreshHud(self, **kwargs):
        player = CBasePlayer.GetLocalPlayer()
        if not player:
            return
        self.maxgold = gamerules.maxgold
        self.RefreshGoldHud()
        self.buttoncreateimp.Invoke('html', ['%s (%s)' % ('Create Imp', 
                gamerules.GetCreateImpCost(player.GetOwnerNumber()))])
        
    def SetGold(self, goldamount):
        self.goldamount = goldamount
        self.RefreshGoldHud()
        
    def RefreshGoldHud(self):
        self.element.Invoke("setGold", [str(self.goldamount), str(self.maxgold)])
        
    def DoAbility(self, abiname):
        engine.ServerCommand('player_ability %s' % (abiname))
        
    def onCommand(self, command):
        command = command.encode('ascii', 'ignore')
        print command
        self.DoAbility(command)
        '''
        if command == 'createimp':
            self.DoAbility('createimp')
        elif command == 'possesscreature':
            self.DoAbility('possesscreature')
        elif command == 'lighting':
            self.DoAbility('lighting')  
        elif command == 'createtreasureroom':
            self.DoAbility('createtreasureroom')
        elif command == 'createlair':
            self.DoAbility('createlair')
        elif command == 'createtraining':
            self.DoAbility('createtraining')
        elif command == 'createhatchery':
            self.DoAbility('createhatchery')
        elif command == 'sellroom':
            self.DoAbility('sellroom')
        elif command == 'createlight':
            self.DoAbility('createlight')
        '''
class HudKeepersettings(WPanel):
    htmlfile = 'ui/keeper/settings.html'
    jsfile = 'ui/keeper/settings.js'
    
    def __init__(self):
        super(HudKeepersettings, self).__init__(viewport, 'HudKeeperSettings')

    def OnLoaded(self):
        super(HudKeepersettings, self).OnLoaded()
        
        self.SetVisible(True)
        
class KeeperHudInfo(HudInfo):
    name = 'keeper_hud'
    wcls = [HudKeeper, HudKeepersettings]

# Old VGUI based hud:
'''
class HudKeeper(CHudElement, Panel):
    def __init__(self):
        CHudElement.__init__(self, "HudKeeper")
        Panel.__init__(self, None, "HudKeeper")
        self.SetParent( GetClientMode().GetViewport() )
        self.SetHiddenBits( HIDEHUD_STRATEGIC )
        
        schemeobj = scheme().LoadSchemeFromFile("resource/SourceScheme.res", "SourceScheme")
        self.SetScheme(schemeobj)
        
        self.SetVisible(True)
        self.SetMouseInputEnabled(True)
        
        self.gold = Label(self, 'GoldLabel', 'gold: 0')
        self.gold.SetScheme(schemeobj)
        
        player = CBasePlayer.GetLocalPlayer()
        if player:
            self.SetGold(resources[player.GetOwnerNumber()]['gold'])
        
        self.buttons = [
            ('CreateImp', 'Create Imp', 'createimp'),
            ('PossessCreature', 'Possess Creature', 'possesscreature'),
            ('CreateTreasureRoom', 'Create Treasure Room', 'createtreasureroom'),
            ('CreateLair', 'Create Lair', 'createlair'),
            ('CreateHatchery', 'Create Hatchery', 'createhatchery'),
            ('CreateTraining', 'Create Training', 'createtraining'),
            
            ('SellRoom', 'Sell', 'sellroom'),
            #('CreateLight', 'Create Light', 'createlight'),
        ]
        
        self.buttoninst = []
        for b in self.buttons:
            abi = GetAbilityInfo(b[2])
            if not abi:
                continue
            
            if abi.costs: gold = abi.costs[0][0][1]
            else: gold = None
            
            binst = Button(self, b[0], '%s (%s)' % (b[1], gold) if gold else b[1])
            binst.SetCommand(b[2])
            binst.SetScheme(schemeobj)
            binst.AddActionSignalTarget(self)
            self.buttoninst.append(binst)
            
            setattr(self, 'button%s' % (b[0].lower()), binst)
            
        resourceset.connect(self.OnResourceSet)
        refreshhud.connect(self.OnRefreshHud)

    def UpdateOnDelete(self):
        resourceset.disconnect(self.OnResourceSet)
        refreshhud.disconnect(self.OnRefreshHud)
        
    def ApplySchemeSettings(self, schemeobj):
        super(HudKeeper, self).ApplySchemeSettings(schemeobj)

        hfontsmall = schemeobj.GetFont( "FriendsSmall" )
        
        self.gold.SetFont(hfontsmall)
        
        map(lambda b: b.SetFont(hfontsmall), self.buttoninst)
        
        self.SetBgColor( Color(0,0,205,0) ) 
        
    def PerformLayout(self):
        super(HudKeeper, self).PerformLayout()
        
        xinset = scheme().GetProportionalScaledValueEx(self.GetScheme(), 15)
        self.SetPos( scheme().GetProportionalScaledValueEx(self.GetScheme(), 0),
                     scheme().GetProportionalScaledValueEx(self.GetScheme(), 335))
                     
        wide = scheme().GetProportionalScaledValueEx(self.GetScheme(), 100)
        tall = scheme().GetProportionalScaledValueEx(self.GetScheme(), 145)
        self.SetSize(wide, tall)
        
        bwidth = scheme().GetProportionalScaledValueEx(self.GetScheme(), 80)
        bheight = scheme().GetProportionalScaledValueEx(self.GetScheme(), 15)
        
        self.gold.SetPos(xinset, 0)
        self.gold.SetSize(wide, bheight)
    
        y = bheight
        for b in self.buttoninst:
            b.SetPos(xinset, y)
            b.SetSize(bwidth, bheight)
            y += bheight
            
    def OnResourceSet(self, ownernumber, type, amount, **kwargs):
        if type == 'gold':
            self.SetGold(amount)
            
    def OnRefreshHud(self, **kwargs):
        player = CBasePlayer.GetLocalPlayer()
        if not player:
            return
        self.buttoncreateimp.SetText('%s (%s)' % ('Create Imp', 
                gamerules.GetCreateImpCost(player.GetOwnerNumber())))
        
    def SetGold(self, goldamount):
        self.gold.SetText('gold: %s' % (str(goldamount)))
        
    def DoAbility(self, abiname):
        engine.ServerCommand('player_ability %s' % (abiname))
        
    def OnCommand(self, command):
        if command == 'createimp':
            self.DoAbility('createimp')
        elif command == 'possesscreature':
            self.DoAbility('possesscreature')
        elif command == 'createtreasureroom':
            self.DoAbility('createtreasureroom')
        elif command == 'createlair':
            self.DoAbility('createlair')
        elif command == 'createtraining':
            self.DoAbility('createtraining')
        elif command == 'createhatchery':
            self.DoAbility('createhatchery')
        elif command == 'sellroom':
            self.DoAbility('sellroom')
        elif command == 'createlight':
            self.DoAbility('createlight')
        
        
class KeeperHudInfo(HudInfo):
    name = 'keeper_hud'
    cls = HudKeeper
'''