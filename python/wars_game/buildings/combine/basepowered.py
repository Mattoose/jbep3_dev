""" Building that requires power. 

Must be placed near a power generator to function.
"""
from srcbase import Color, RenderMode_t, RenderFx_t
from vmath import Vector
from utils import UTIL_EntitiesInSphere
from core.buildings import WarsBuildingInfo, UnitBaseBuilding as BaseClass
from core.units import CreateUnitList, UnitListHandle, unitlistpertype
from core.dispatch import receiver
from core.signals import prelevelinit
from core.resources import GiveResources, HasEnoughResources
from playermgr import OWNER_LAST
from fields import BooleanField
from entities import entity, networked

if isclient:
    from utils import ProjectedTexture
else:
    from core.usermessages import CRecipientFilter, SendUserMessage
    from utils import UTIL_ListPlayersForOwnerNumber
    
from collections import defaultdict

# List of buildings that require a nearby powergenerator
poweredlist = CreateUnitList()

# Power generator building
if isclient:
    @receiver(prelevelinit)
    def LevelInit(sender, **kwargs):
        PowerGeneratorBuilding.showpoweroverlaycount = defaultdict(lambda: 0)

@entity('build_comb_powergenerator', networked=True)
class PowerGeneratorBuilding(BaseClass):  
    def UpdateOnRemove(self):
        if isclient:
            self.DisablePowerOverlay()
            
        if isserver:
            # Notify powered buildings in range
            map(lambda p: p.UpdatePoweredState(), poweredlist[self.GetOwnerNumber()])
        
        # ALWAYS CHAIN BACK!
        super(PowerGeneratorBuilding, self).UpdateOnRemove()
        
    if isserver:
        def OnConstructed(self):
            super(PowerGeneratorBuilding, self).OnConstructed()
            
            # Notify powered buildings in range
            map(lambda p: p.UpdatePoweredState(), poweredlist[self.GetOwnerNumber()])
    
    if isclient:
        # Power overlays, show the range of each power generator
        # TODO: Ensure counts are correct when the unit dies or when the owner number changes.
        poweroverlay = None
        showpoweroverlaycount = defaultdict(lambda: 0)
        
        def EnablePowerOverlay(self):
            if self.poweroverlay:
                return
            projorigin = self.GetAbsOrigin()
            color = Color(255, 255, 255, 255)
            powerrange = self.unitinfo.powerrange
            self.poweroverlay = ProjectedTexture('decals/testeffect', 
                    -Vector(powerrange, powerrange, 0), 
                    Vector(powerrange, powerrange, 0), 
                    projorigin, self.GetAbsAngles(), color.r(), color.g(), color.b(), color.a())
            
        def DisablePowerOverlay(self):
            if not self.poweroverlay:
                return
            self.poweroverlay.Shutdown()
            self.poweroverlay = None

        @staticmethod
        def EnableAllPowerOverlays(ownernumber):
            if PowerGeneratorBuilding.showpoweroverlaycount[ownernumber]:
                PowerGeneratorBuilding.showpoweroverlaycount[ownernumber] += 1
                return
                
            PowerGeneratorBuilding.showpoweroverlaycount[ownernumber] += 1
            
            for powergen in unitlistpertype[ownernumber]['build_comb_powergenerator']:
                powergen.EnablePowerOverlay()
                
        @staticmethod
        def DisableAllPowerOverlays(ownernumber):
            PowerGeneratorBuilding.showpoweroverlaycount[ownernumber] -= 1
            if PowerGeneratorBuilding.showpoweroverlaycount[ownernumber]:
                return

            for powergen in unitlistpertype[ownernumber]['build_comb_powergenerator']:
                powergen.DisablePowerOverlay()
            
        def OnSelected(self, player):
            super(PowerGeneratorBuilding, self).OnSelected(player)
            
            self.EnableAllPowerOverlays(self.GetOwnerNumber())
        
        def OnDeSelected(self, player):
            super(PowerGeneratorBuilding, self).OnDeSelected(player)
            
            self.DisableAllPowerOverlays(self.GetOwnerNumber())

class PoweredGeneratorInfo(WarsBuildingInfo):
    name = 'build_comb_powergenerator'
    displayname = '#BuildCombPowGen_Name'
    description = '#BuildCombPowGen_Description'
    image_name = 'vgui/combine/buildings/build_comb_powergenerator'
    cls_name = 'build_comb_powergenerator'
    modelname = 'models/props_combine/combine_generator01.mdl'
    costs = [('requisition', 2)]
    health = 200
    buildtime = 12.0
    generateresources = ('power', 1, 30.0)
    powerrange = 720.0
    infoprojtextures = [ {
            'texture' : 'decals/testeffect',
            'mins' : -Vector(powerrange, powerrange, 0),
            'maxs' : Vector(powerrange, powerrange, 64),
    } ]
    sound_select = 'build_comb_powergenerator'
    abilities = {
        8 : 'cancel',
    }
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_powergen'])

# Base building for powered buildings
class BasePoweredBuilding(object):
    def __init__(self):
        super(BasePoweredBuilding, self).__init__()
        
        self.poweredlisthandle = self.CreateUnitListHandle(poweredlist)
    
    def Spawn(self):
        super(BasePoweredBuilding, self).Spawn()
        
        self.poweredlisthandle.Enable()
        
        if isserver:
            self.UpdatePoweredState()
            #self.SetThink(self.PowerThink, gpGlobals.curtime+0.5, 'PowerThink')
        else:
            self.OnPoweredChanged()
        
    def UpdateOnRemove(self):
        super(BasePoweredBuilding, self).UpdateOnRemove()
        
        self.poweredlisthandle.Disable()

    if isserver:
        #def PowerThink(self):
        #    HasEnoughResources...
        #    self.SetNextThink(gpGlobals.curtime+0.5, 'PowerThink')
    
        def UpdatePoweredState(self):
            self.powered = self.unitinfo.IsPoweredAt(self.GetAbsOrigin(), self.GetOwnerNumber())
            self.OnPoweredChanged()
        
        def OnChangeOwnerNumber(self, oldownernumber):
            super(BasePoweredBuilding, self).OnChangeOwnerNumber(oldownernumber)
            if self.poweredlisthandle.disabled:
                return
            self.UpdatePoweredState()

    if isclient:
        def OnConstructionStateChanged(self):
            super(BasePoweredBuilding, self).OnConstructionStateChanged()
            if self.constructionstate == self.BS_CONSTRUCTED:
                self.OnPoweredChanged()
    
    def OnPoweredChanged(self):
        if self.powered:
            self.SetRenderMode(RenderMode_t.kRenderNormal)
            self.SetRenderAlpha(255)
            self.SetRenderColor(255, 255, 255)
        else:
            self.SetRenderMode(RenderMode_t.kRenderTransColor)
            self.SetRenderAlpha(255)
            self.SetRenderColor(48, 48, 48)
        
    powered = BooleanField(value=False, networked=True, clientchangecallback='OnPoweredChanged')
    
class BaseFactoryPoweredBuilding(BasePoweredBuilding):
    if isserver:
        def OnPoweredChanged(self):
            super(BaseFactoryPoweredBuilding, self).OnPoweredChanged()
            self.onhold = not self.powered
        
class PoweredBuildingInfo(WarsBuildingInfo):
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_powered'])

    @staticmethod
    def IsPoweredAt(pos, ownernumber):
        # Check nearby a power generator
        inrange = False
        '''
        ents = UTIL_EntitiesInSphere(512, pos, PoweredGeneratorInfo.powerrange, 0)
        for ent in ents:
            if ent.GetOwnerNumber() != ownernumber:
                continue
            try:
                if not issubclass(ent.unitinfo, PoweredGeneratorInfo):
                    continue
                if ent.constructionstate != ent.BS_CONSTRUCTED:
                    continue
            except AttributeError:s
                continue
            inrange = True
            break
        '''
        
        # Probably faster to iterate the power generator list
        for p in unitlistpertype[ownernumber]['build_comb_powergenerator']:
            if p.constructionstate != p.BS_CONSTRUCTED or p.IsMarkedForDeletion():
                continue
            if p.GetAbsOrigin().DistTo(pos) < PoweredGeneratorInfo.powerrange:
                inrange = True
                break
                
        return inrange
    
    def IsValidPosition(self, pos):
        return self.IsPoweredAt(pos, self.ownernumber) and super(PoweredBuildingInfo, self).IsValidPosition(pos)

    if isclient:
        def CreateVisuals(self):
            super(PoweredBuildingInfo, self).CreateVisuals()
            
            PowerGeneratorBuilding.EnableAllPowerOverlays(self.ownernumber)

        def ClearVisuals(self): 
            super(PoweredBuildingInfo, self).ClearVisuals()

            PowerGeneratorBuilding.DisableAllPowerOverlays(self.ownernumber)
            