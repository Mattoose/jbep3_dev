from srcbase import SOLID_NONE
from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseBuilding as BaseClass
from entities import entity
from core.units import CreateUnit

import keeperworld

@entity('dk_heart', networked=True)
class Heart(BaseClass):
    def __init__(self):
        super(Heart, self).__init__()
        
        self.hearttiles = []
        
    def Precache(self):
        super(Heart, self).Precache()
        
        self.PrecacheScriptSound('Heart.Beat')
        
    if isserver:
        def Spawn(self):
            super(Heart, self).Spawn()
            
            self.SetThink(self.HeartBeat, gpGlobals.curtime + 1.0, 'HeartBeat')
            
        def HeartBeat(self):
            self.EmitSound('Heart.Beat')
            self.SetNextThink(gpGlobals.curtime + self.heartbeatrate, 'HeartBeat')
            
            if self.health < self.maxhealth:
                # Also regen health per heartbeat
                self.health = self.health + 1
            
    def OnTakeDamage_Alive(self, info):
        self.lastenemyattack = gpGlobals.curtime
        return super(Heart, self).OnTakeDamage_Alive(info)
        
    heartbeatrate = 2.0
    lastenemyattack = 0.0
    
# Register unit
class HeartInfo(WarsBuildingInfo):
    name = "dk_heart" 
    cls_name = "dk_heart"
    modelname = 'models/keeper/Heart.mdl'
    health = 1500
    population = 0
    sound_death = 'Heart.Die'
    generateresources = ('gold', 1, 5.0) # Get one gold free per second