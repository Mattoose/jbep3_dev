from srcbase import SOLID_BBOX, FSOLID_NOT_SOLID, FSOLID_TRIGGER
from vmath import Vector, QAngle
from core.buildings import UnitBaseBuilding as BaseClass

from entities import entity
if isserver:
    from entities import D_LI, CreateEntityByName, DispatchSpawn, CTriggerArea
    from particles import PrecacheParticleSystem, DispatchParticleEffect, ParticleAttachment_t
    from utils import UTIL_SetSize, UTIL_SetOrigin, UTIL_Remove
    
if isserver:
    @entity('trigger_heal_area')
    class HealArea(CTriggerArea):
        def Precache(self):
            super(HealArea, self).Precache()
            PrecacheParticleSystem('striderbuster_shotdown_trail')
        
        def Spawn(self):
            self.Precache()
            
            super(HealArea, self).Spawn()

            self.SetThink(self.HealThink, gpGlobals.curtime, 'HealThink')

        def HealThink(self):
            for entity in self.touchingents:
                if not entity or not entity.IsUnit() or entity.isbuilding or entity.IRelationType(self) != D_LI:
                    continue
                    
                if entity.health < entity.maxhealth:
                    entity.health += min(2, (entity.maxhealth-entity.health))
                    DispatchParticleEffect("striderbuster_shotdown_trail", ParticleAttachment_t.PATTACH_ABSORIGIN_FOLLOW, entity)

            self.SetNextThink(gpGlobals.curtime + 0.5, 'HealThink')
            
@entity('build_baseregeneration')
class BaseRegeneration(BaseClass):
    def Spawn(self):
        super(BaseRegeneration, self).Spawn()

        zmin = self.WorldAlignMins().z
        zmax = self.WorldAlignMaxs().z
        origin = self.GetAbsOrigin()
        origin.z += zmin
        
        self.healarea = CreateEntityByName('trigger_heal_area')
        self.healarea.startdisabled = True
        self.healarea.SetOwnerNumber(self.GetOwnerNumber())
        UTIL_SetOrigin(self.healarea, origin)
        UTIL_SetSize(self.healarea, -Vector(self.healradius, self.healradius, -zmin), Vector(self.healradius, self.healradius, zmax))
        DispatchSpawn(self.healarea)
        self.healarea.SetOwnerEntity(self)
        self.healarea.SetParent(self)
        self.healarea.Activate()
        self.UpdateHealAreaState()
        
        #import ndebugoverlay
        #ndebugoverlay.EntityBounds(self.healarea, 255, 0, 0, 255, 10.0)

    def UpdateOnRemove(self):
        super(BaseRegeneration, self).UpdateOnRemove()
        
        UTIL_Remove(self.healarea)
        
    def SetConstructionState(self, state):
        super(BaseRegeneration, self).SetConstructionState(state) 
        
        self.UpdateHealAreaState()
        
    def UpdateHealAreaState(self):
        if self.healarea:
            if self.constructionstate == self.BS_CONSTRUCTED:
                self.healarea.Enable()
            else:
                self.healarea.Disable()
        
    def OnChangeOwnerNumber(self, oldownernumber):
        super(BaseRegeneration, self).OnChangeOwnerNumber(oldownernumber)
        
        if self.healarea:
            self.healarea.SetOwnerNumber(self.GetOwnerNumber())
        
    healarea = None
    autoconstruct = False
    healradius = 256
