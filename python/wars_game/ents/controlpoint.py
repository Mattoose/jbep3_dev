from srcbase import DAMAGE_NO, Color
from vmath import Vector
from gamerules import GameRules
from playermgr import OWNER_LAST
import playermgr
from core.resources import GiveResources
from core.units import UnitInfo
from core.hud import NotifierInsertMessage, InsertResourceIndicator
from core.factions import PlayFactionSound
from entities import entity, networked, Disposition_t, FOWFLAG_BUILDINGS_NEUTRAL_MASK
from core.buildings import UnitBaseBuilding as BaseClass, WarsBuildingInfo
from fields import StringField, OutputField, GenericField, FloatField, FlagsField
from utils import UTIL_ListPlayersForOwnerNumber, UTIL_ListForOwnerNumberWithDisp

if isserver:
    from entities import CTriggerMultiple, COutputEvent, gEntList
    from core.usermessages import CRecipientFilter
    from core.signals import playerdefeated
else:
    from vgui.entitybar import UnitBarScreen
    
if isclient:    
    controlpoints = []
    
    
if isserver:
    @entity('trigger_capture_area')
    class CaptureArea(CTriggerMultiple):
        def Spawn(self):
            super(CaptureArea, self).Spawn()
            
            if not self.controlpoint:
                if not self.controlpointname:
                    PrintWarning('CaptureArea: No control point name set!\n')
                    return
                self.controlpoint = gEntList.FindEntityByName(None, self.controlpointname)
                if not self.controlpoint:
                    PrintWarning('CaptureArea: No control point named %s!\n' % (self.controlpointname))
                    return
            
            self.SetThink(self.CaptureThink, gpGlobals.curtime, self.CAPTURE_THINK_CONTEXT)

        def CaptureThink(self):
            if not self.controlpoint:
                return
                
            if not self.controlpoint.enabled:
                self.SetNextThink(gpGlobals.curtime + 0.5, self.CAPTURE_THINK_CONTEXT)
                return
                
            # get the teamid capturing, update if necessary
            playercapturing = self.UpdatePlayerCapturing()
            if playercapturing != self.controlpoint.playercapturing:
                self.controlpoint.Get().playercapturing = playercapturing
                self.controlpoint.Get().nextcapturetime = gpGlobals.curtime + self.controlpoint.CAPTURE_TIME

            # if a teamid is capturing, check if captured
            if self.controlpoint.playercapturing:
                if self.controlpoint.nextcapturetime < gpGlobals.curtime:
                    player_lost = self.controlpoint.GetOwnerNumber()
                    self.controlpoint.SetOwnerNumber( self.controlpoint.playercapturing )
                    self.controlpoint.Get().playercapturing = None
                    
            self.SetNextThink(gpGlobals.curtime + 0.5, self.CAPTURE_THINK_CONTEXT)
            
        def UpdatePlayerCapturing(self):
            team_capturing = None
            controlpoint = self.controlpoint
            for entity in self.GetTouchingEntities():
                if not entity or not entity.IsUnit() or entity == controlpoint:
                    continue
                    
                # Cloaked units cannot capture a control point
                try:
                    if entity.cloaked:
                        continue
                except AttributeError:
                    pass
                    
                # Check if we are allowed to capture the point
                try:
                    cancappcontrolpoint = entity.cancappcontrolpoint
                except AttributeError:
                    cancappcontrolpoint = True
                if not cancappcontrolpoint:
                    continue
                    
                # Must be a player (not a special ownernumber like neutral or enemy)
                if entity.GetOwnerNumber() < OWNER_LAST:
                    continue
                    
                # we are already capturing it
                if entity.GetOwnerNumber() == team_capturing:
                    continue

                # owners need to be removed before this point can be captured
                if entity.GetOwnerNumber() == controlpoint.GetOwnerNumber():
                    return None

                # Don't capture a point of somebody we like or against we are neutral
                if playermgr.relationships[(entity.GetOwnerNumber(), controlpoint.GetOwnerNumber())] == Disposition_t.D_LI:
                    continue

                # Nobody is capturing it, so we are going to capture it
                if not team_capturing:
                    team_capturing = entity.GetOwnerNumber()
                    continue

                # this means multiple npcs of different owner numbers are on the point and we must hate the other owner number
                if team_capturing != entity.GetOwnerNumber() and playermgr.relationships[(entity.GetOwnerNumber(), team_capturing)] == Disposition_t.D_HT:
                    return None

            return team_capturing
                
        CAPTURE_THINK_CONTEXT = "CaptureThinkContext"
        controlpointname = StringField(value='', keyname='control_point')
        
        controlpoint = None
        
        spawnflags = FlagsField(keyname='spawnflags', flags=[
                ('TRIGGER_ALLOW_CLIENTS', 0x01, True), # Players can fire this trigger
                ('TRIGGER_ALLOW_NPCS', 0x02, True), # NPCS can fire this trigger
                ('TRIGGER_ALLOW_PUSHABLES', 0x04, False), # Pushables can fire this trigger
                ('TRIGGER_ALLOW_PHYSICS', 0x08, False), # Physics objects can fire this trigger
                ('TRIGGER_ONLY_PLAYER_ALLY_NPCS', 0x10, False), # *if* NPCs can fire this trigger, this flag means only player allies do so
                ('TRIGGER_ONLY_CLIENTS_IN_VEHICLES', 0x20, False), # *if* Players can fire this trigger, this flag means only players inside vehicles can 
                ('TRIGGER_ALLOW_ALL', 0x40, False), # Everything can fire this trigger EXCEPT DEBRIS!
                ('TRIGGER_ONLY_CLIENTS_OUT_OF_VEHICLES', 0x200, False), # *if* Players can fire this trigger, this flag means only players outside vehicles can 
                ('TRIG_PUSH_ONCE', 0x80, False), # trigger_push removes itself after firing once
                ('TRIG_PUSH_AFFECT_PLAYER_ON_LADDER', 0x100, False), # if pushed object is player on a ladder, then this disengages them from the ladder (HL2only)
                ('TRIG_TOUCH_DEBRIS', 0x400, False), # Will touch physics debris objects
                ('TRIGGER_ONLY_NPCS_IN_VEHICLES', 0X800, False), # *if* NPCs can fire this trigger, only NPCs in vehicles do so (respects player ally flag too)
                ('TRIGGER_PUSH_USE_MASS', 0x1000, False), # Correctly account for an entity's mass (CTriggerPush::Touch used to assume 100Kg)
            ],
        )
        
if isclient:
    class ControlCaptureBarScreen(UnitBarScreen):
        """ Draws the unit health bar. """
        def __init__(self, unit):
            super(ControlCaptureBarScreen, self).__init__(unit,
                Color(), Color(40, 40, 40, 250), Color(150, 150, 150, 0), 
                offsety=16.0, worldsizey=16.0, worldbloatx=128.0)
            
        def Draw(self):
            panel = self.GetPanel()
            panel.weight = (self.unit.nextcapturetime - gpGlobals.curtime) / self.unit.CAPTURE_TIME
            panel.barcolor = playermgr.dbplayers[self.unit.playercapturing].color
                    
            super(ControlCaptureBarScreen, self).Draw()

@networked
class BaseControlPoint(BaseClass):
    if isclient:
        oldplayercapturing = None
        showingcapturebar = False
        
        def __init__(self):
            super(BaseControlPoint, self).__init__()

            controlpoints.append(self)
        
        def Spawn(self):
            super(BaseControlPoint, self).Spawn()
            
            self.buildinglisthandle.Disable() # Don't list us in the building list of the player
            
        def UpdateOnRemove(self):
            try:
                controlpoints.remove(self)
            except ValueError:
                PrintWarning('#%d Control Point not in global control point list!\n' % (self.entindex()))

            super(BaseControlPoint, self).UpdateOnRemove()

        def ShowCaptureBar(self):
            if self.showingcapturebar:
                return
                
            self.capturebarscreen = ControlCaptureBarScreen(self)
                
            self.showingcapturebar = True
            
        def HideCaptureBar(self):
            if not self.showingcapturebar:
                return
                
            self.capturebarscreen.Shutdown()
            self.capturebarscreen = None
                
            self.showingcapturebar = False
            
        def OnDataChanged(self, type):
            super(BaseControlPoint, self).OnDataChanged(type)
            
            if self.oldplayercapturing != self.playercapturing:
                if self.playercapturing:
                    self.ShowCaptureBar()
                else:
                    self.HideCaptureBar()
                self.oldplayercapturing = self.playercapturing
            
    if isserver:
        def __init__(self):
            super(BaseControlPoint, self).__init__()

            self.viewdistance = 1024.0
            playerdefeated.connect(self.OnPlayerDefeated)
    
        def Enable(self):
            self.enabled = True
            
        def Disable(self):
            self.enabled = False
            
        def Precache(self):
            super(BaseControlPoint, self).Precache()
            
        def Spawn(self):
            self.SetUnitType('control_point')
        
            super(BaseControlPoint, self).Spawn()
            
            self.buildinglisthandle.Disable() # Don't list us in the building list of the player
            
            self.Precache()
            
            self.takedamage = DAMAGE_NO
            self.SetCanBeSeen(False)
            
            # Make viewoffset higher, so the fog of war is not hidden at low points
            self.SetViewOffset(Vector(0, 0, 128.0))
            
        def UpdateOnRemove(self):
            playerdefeated.disconnect(self.OnPlayerDefeated)
            
            super(BaseControlPoint, self).UpdateOnRemove()
            
        def OnPlayerDefeated(self, ownernumber, *args, **kwargs):
            # Become neutral if the defeated player owns us
            if ownernumber == self.GetOwnerNumber():
                self.SetOwnerNumber(0)
            
        def OnChangeOwnerNumber(self, oldownernumber):
            super(BaseControlPoint, self).OnChangeOwnerNumber(oldownernumber)
            
            #self.oncaptured[GetOwnerNumber() - DEFAULT_TEAMS].FireOutput(self, self)
            self.oncapturedall.FireOutput(self, self)
            #self.onlost[oldownernumber - DEFAULT_TEAMS].FireOutput(self, self)
            
            # Notify new owner players
            players = UTIL_ListPlayersForOwnerNumber(self.GetOwnerNumber())
            filter = CRecipientFilter()
            filter.MakeReliable()
            map(filter.AddRecipient, players)
            NotifierInsertMessage('Control Point Captured', filter=filter)
            PlayFactionSound('soundcpcaptured', filter=filter)
            
            # Notify old owner players
            players = UTIL_ListPlayersForOwnerNumber(oldownernumber)
            filter = CRecipientFilter()
            filter.MakeReliable()
            map(filter.AddRecipient, players)
            NotifierInsertMessage('Control Point Lost', filter=filter)
            PlayFactionSound('soundcplost', filter=filter)

            # Push one update for old players (otherwise the control point might keep showing up as "theirs")
            players = UTIL_ListForOwnerNumberWithDisp(oldownernumber, d=Disposition_t.D_LI)
            for player in players:
                self.FOWForceUpdate(player.entindex()-1)
            
    enabled = True   
    CAPTURE_TIME = 30.0
    
    oncapturedall = OutputField(keyname='OnCapturedAll')
    playercapturing = GenericField(value=None, networked=True)
    nextcapturetime = FloatField(value=0.0, networked=True)
    
    fowflags = FOWFLAG_BUILDINGS_NEUTRAL_MASK

class BaseControlPointInfo(WarsBuildingInfo):
    name        = "control_point"
    cls_name    = "control_point"
    image_name = "vgui/units/unit_shotgun.vmt"
    modelname = 'models/cat-props/capture_point.mdl'    
    displayname = '#ControlPoint_Name'
    description = '#ControlPoint_Description'
    #minimapicon_name = 'icon_capturepoint' # TODO: Fix alpha icons
    minimaphalfwide = 2
    minimaphalftall = 2
            
if isserver:
    @entity('capturetheflag_point',
            studio='models/cat-props/capture_point.mdl')
    class CaptureTheFlagPoint(BaseControlPoint):
        def Spawn(self):
            super(CaptureTheFlagPoint, self).Spawn()
            
        def OnChangeOwnerNumber(self, oldownernumber):
            super(CaptureTheFlagPoint, self).OnChangeOwnerNumber(oldownernumber)
            
            GameRules().OnFlagOwnerChanged(self.GetOwnerNumber(), oldownernumber)
        enabled = False
        
    @entity('control_point',
            studio='models/cat-props/capture_point.mdl')
    class ControlPoint(BaseControlPoint):
        def Spawn(self):
            super(ControlPoint, self).Spawn()
            
            self.SetThink(self.ResourceThink, gpGlobals.curtime)
            
        def ResourceThink(self):
            if self.GetOwnerNumber() >= OWNER_LAST:
                players = UTIL_ListPlayersForOwnerNumber(self.GetOwnerNumber())
                filter = CRecipientFilter()
                filter.MakeReliable()
                map(filter.AddRecipient, players)
                
                origin = self.GetAbsOrigin()
                origin.x += 32.0
                origin.z += 256.0
                InsertResourceIndicator(origin, '+1', filter=filter)
            
                GiveResources(self.GetOwnerNumber(), [('requisition', 1)], firecollected=True)
        
            self.SetNextThink(gpGlobals.curtime+self.ADD_RESOURCE_INTERVAL)
            
        def OnChangeOwnerNumber(self, oldownernumber):
            super(ControlPoint, self).OnChangeOwnerNumber(oldownernumber)
        
        ADD_RESOURCE_INTERVAL = 12.0
    