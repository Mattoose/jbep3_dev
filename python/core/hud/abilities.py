from srcbase import Color
from vgui import surface, AddTickSignal, HudIcons, scheme
from vgui.controls import Panel
from entities import C_HL2WarsPlayer
from gameinterface import engine
from abilitybutton import AbilityButton
from input import MOUSE_RIGHT

from core.abilities import DoAbility, SendAbilityMenuChanged, ClientDoAbility
from core.units import GetUnitInfo
from core.signals import selectionchanged, abilitymenuchanged, refreshhud, resourceset

from profiler import profile

class AbilitySectionButton(AbilityButton):
    def ApplySchemeSettings(self, scheme):
        super(AbilitySectionButton, self).ApplySchemeSettings(scheme)
        
        self.SetBorder(None)
    
    #@profile('AbilitySectionButton.Paint')
    def Paint(self):
        super(AbilitySectionButton,self).Paint()
        if not self.rechargecomplete or self.rechargetime == 0:
            return
            
        w, h = self.GetSize()
        
        weight = (self.rechargecomplete-gpGlobals.curtime) / self.rechargetime

        # draw how much health we still got
        surface().DrawSetColor(Color(0, 0, 200, 100))
        surface().DrawFilledRect(0, 0, int(w*weight), h)  
            
    def OnCursorEntered(self):
        super(AbilitySectionButton, self).OnCursorEntered()
        self.ShowAbility()
        self.GetParent().OnTick() # Do an extra tick to update infobox for now 
        
    def OnCursorExited(self):
        super(AbilitySectionButton, self).OnCursorExited()
        self.HideAbility()
        
    def ShowAbility(self):
        if self.info:
            infopanel = self.GetParent().infopanel
            infopanel.MoveToDefault()
            infopanel.ShowAbility(self.info, self.slot)

    def HideAbility(self):
        self.GetParent().infopanel.HideAbility()
        
    rechargecomplete = None
    rechargetime = None
    
    info = None

class BaseHudAbilities(Panel):
    def __init__(self, parent, infopanel):
        super(BaseHudAbilities, self).__init__(parent, "HudAbilities")
        
        self.EnableSBuffer(True)
        self.SetProportional(True)
        self.SetPaintBackgroundEnabled(False)
        self.SetKeyBoardInputEnabled(False)
        self.SetMouseInputEnabled(True)    

        self.infopanel = infopanel
        
        # Create buttons
        self.slots = []
        nslots = self.nslotsx * self.nslotsy
        for i in range(0, nslots):
            namecommand = 'abilityslot_'+ str(i)
            namecommand2 = 'abilityslotright_'+ str(i)
            slot = AbilitySectionButton(self, namecommand)
            slot.iconcoords = self.buttoniconcoords
            slot.SetAllImages(HudIcons().GetIcon(self.buttontexture), Color(255, 255, 255, 255))
            if self.buttontexturehover:
                slot.SetImage(slot.BUTTON_ENABLED_MOUSE_OVER, HudIcons().GetIcon(self.buttontexturehover), Color(255, 255, 255, 255))
            if self.buttontextureselected:
                slot.SetImage(slot.BUTTON_PRESSED, HudIcons().GetIcon(self.buttontextureselected), Color(255, 255, 255, 255))
            slot.SetCommand(namecommand)
            slot.SetCommandRightClick(namecommand2)
            slot.SetMouseClickEnabled(MOUSE_RIGHT, True) # Default is left only
            slot.AddActionSignalTarget(self)
            slot.SetMouseInputEnabled(True)
            slot.SetVisible(False)
            slot.slot = i
            self.slots.append(slot)
            
        selectionchanged.connect(self.OnSelectionChanged)
        abilitymenuchanged.connect(self.OnAbilityMenuChanged)
        refreshhud.connect(self.OnRefreshHud)
        resourceset.connect(self.OnRefreshHud)
            
        AddTickSignal(self.GetVPanel(), 350)
        
    def SetVisible(self, visible):
        super(BaseHudAbilities, self).SetVisible(visible)
        if not visible and self.infopanel:
            self.infopanel.HideAbility()
        
    def UpdateOnDelete(self):
        selectionchanged.disconnect(self.OnSelectionChanged)
        abilitymenuchanged.disconnect(self.OnAbilityMenuChanged)
        refreshhud.disconnect(self.OnRefreshHud)
        resourceset.disconnect(self.OnRefreshHud)
        self.infopanel = None
        
    def PerformLayout(self):      
        """ Setup the abilities buttons """
        super(BaseHudAbilities, self).PerformLayout()
        
        margintop = scheme().GetProportionalScaledValueEx(self.GetScheme(), self.margintop) 
        marginbottom = scheme().GetProportionalScaledValueEx(self.GetScheme(), self.marginbottom) 
        marginleft = scheme().GetProportionalScaledValueEx(self.GetScheme(), self.marginleft) 
        marginright = scheme().GetProportionalScaledValueEx(self.GetScheme(), self.marginright) 
        
        w, h = self.GetSize()
        sizex = (w-marginleft-marginright) / self.nslotsx
        sizey = (h-margintop-marginbottom) / self.nslotsy

        # Set size and position for each button
        for y in range(0, self.nslotsy):
            for x in range(0, self.nslotsx):
                self.slots[x+y*self.nslotsx].SetSize(sizex, sizey)
                self.slots[x+y*self.nslotsx].SetPos(marginleft+x*sizex, margintop+y*sizey)
                
    #@profile('BaseHudAbilities.OnTick')
    def OnTick(self):
        if not self.IsVisible():
            return
            
        super(BaseHudAbilities, self).OnTick()
        
        if not self.activeunitinfo:
            return
        
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer() 
        if not player:
            return

        # Set abilities
        # TODO: only need to do this per tick atm because of the recharge time
        #       Would be nice to make it signal based.
        for slot in self.slots:
            info = slot.info
            if not info:
                continue
            
            # Can we do this ability? Set enabled/disabled
            # The image depends on it
            cando, rechargecomplete = self.CalculateCanDoAbility(info, player, self.hlmin, self.hlmax)
            if cando:
                slot.SetEnabled(True)
                slot.rechargecomplete = None
            else:
                slot.SetEnabled(False)
                slot.rechargecomplete = rechargecomplete
                slot.rechargetime = info.rechargetime

    def GetActiveUnitInfo(self):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer() 
        if not player:
            return None
        # Should always have unit info ( fallback is unit_unknown )
        highlight_unittype = player.GetSelectedUnitType()
        if not highlight_unittype:
            return None
        unitinfo = GetUnitInfo(highlight_unittype, fallback=None)
        return unitinfo
        
    def AbilityInUnits(self, info, units):
        for unit in units:
            if info.name in unit.abilitiesbyname:
                return True
        return False
        
    def RefreshSlots(self):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer() 
        if not player:
            return
        
        self.activeunitinfo = self.GetActiveUnitInfo()
        self.hlmin, self.hlmax = player.GetSelectedUnitTypeRange()
        units = player.GetSelection(self.hlmin, self.hlmax)
        unit = units[0] if units else None #player.GetUnit(self.hlmin) if self.hlmin >= 0 else None
        self.activeownernumber = player.GetOwnerNumber()

        # Hide everything if there is no unit type or if we selected another player's unit
        if not self.activeunitinfo or not unit or unit.GetOwnerNumber() != player.GetOwnerNumber():
            for slot in self.slots:
                slot.SetVisible(False)
                slot.info = None
            return
            
        # Retrieve the active hud abilities map
        try:
            abilitiesmap = player.hudabilitiesmap[-1]
        except (AttributeError, IndexError):
            abilitiesmap = self.activeunitinfo.abilities
            
        # Set abilities
        for i, slot in enumerate(self.slots):
            try:
                info = self.activeunitinfo.GetAbilityInfo(abilitiesmap[i], self.activeownernumber)
            except KeyError:
                slot.SetVisible(False)
                continue
                
            if not info or not self.AbilityInUnits(info, units):
                slot.SetVisible(False)
                continue
                
            slot.SetVisible(True)
            slot.info = info
            
            # Can we do this ability? Set enabled/disabled
            # The image depends on it
            cando, rechargecomplete = self.CalculateCanDoAbility(info, player, self.hlmin, self.hlmax)
            if cando:
                slot.SetEnabled(True)
                if slot.IsCursorOver(): slot.SetArmed(True)
                slot.iconimage = info.image
                slot.rechargecomplete = None
            else:
                slot.SetEnabled(False)
                if slot.IsCursorOver(): slot.SetArmed(False)
                slot.iconimage = info.image_dis
                slot.rechargecomplete = rechargecomplete
                slot.rechargetime = info.rechargetime
                    
            if slot.IsCursorOver():
                slot.ShowAbility()
                
        
    def CalculateCanDoAbility(self, info, player, hlmin, hlmax):
        minrechargecomplete = float('inf')
        
        for unit in player.GetSelection():
            if info.name not in unit.abilitiesbyname:
                continue
            if info.CanDoAbility(player, unit=unit):
                return True, 0.0
            try:
                if unit.abilitynexttime[info.uid] < minrechargecomplete:
                    minrechargecomplete = unit.abilitynexttime[info.uid]
            except KeyError:
                minrechargecomplete = 0
        return False, minrechargecomplete    
    
    def OnCommand(self, command):
        player = C_HL2WarsPlayer.GetLocalHL2WarsPlayer() 
        highlight_unittype = player.GetSelectedUnitType()
        hlmin, hlmax = player.GetSelectedUnitTypeRange()
        splitted = command.split('_')
        unit = player.GetUnit(hlmin)
        unitinfo = unit.unitinfo
        slot = int(splitted[1])
        
        # Retrieve the active hud abilities map
        try:
            abilitiesmap = player.hudabilitiesmap[-1]
        except (AttributeError, IndexError):
            abilitiesmap = unitinfo.abilities
        info = unitinfo.GetAbilityInfo(abilitiesmap[slot], unit.GetOwnerNumber())

        if splitted[0] == 'abilityslot':
            ClientDoAbility(player, info, unitinfo.name)
            return
        elif splitted[0] == 'abilityslotright':
            engine.ServerCommand('player_abilityautocast %s %s' % (info.name, unitinfo.name))
            return
        raise Exception('Unknown command ' + command)
        
    def OnSelectionChanged(self, player, **kwargs):
        # Update highlighted units area
        unitcount = player.CountUnits()
        if unitcount == 0:
            if player.GetSelectedUnitType():
                player.SetSelectedUnitType(None)
            try: del player.hudabilitiesmap
            except AttributeError: pass
            SendAbilityMenuChanged()
        else:
            if player.GetSelectedUnitType() != player.GetUnit(0).GetUnitType():
                player.SetSelectedUnitType(player.GetUnit(0).GetUnitType()) 
                try: del player.hudabilitiesmap
                except AttributeError: pass
                SendAbilityMenuChanged()
        
        self.RefreshSlots()
        self.OnTick() # Extra tick to make changes look smooth
        
    def OnAbilityMenuChanged(self, **kwargs):
        self.RefreshSlots()
        self.OnTick() # Extra tick to make changes look smooth
        
    def OnRefreshHud(self, **kwargs):
        self.RefreshSlots()
        self.OnTick() # Extra tick to make changes look smooth
        
    buttonhoverimage = 'VGUI/button_hover'
    buttonselectedimage = 'VGUI/button_selected'
    
    buttontexture = 'hud_rebels_button_enabled'
    buttontextureselected = 'hud_rebels_button_pressed'
    buttontexturehover = 'hud_rebels_button_hover'
    buttoniconcoords = (0.1, 0.1, 0.8, 0.8) # X, Y, Wide, Tall 
    
    margintop = 0
    marginbottom = 0
    marginleft = 0
    marginright = 0
    
    nslotsx = 4
    nslotsy = 3
    
    activeunitinfo = None
    activeownernumber = None
    
    