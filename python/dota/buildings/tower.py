from vmath import *
from core.buildings import UnitBaseAutoTurret, WarsTurretInfo
from core.ents.homingprojectile import HomingProjectile
import random
from entities import entity
if isserver:
    from wars_game.ents.grenade_spit import GrenadeSpit
    from entities import CreateEntityByName, DispatchSpawn
    from utils import UTIL_PredictedPosition
from gameinterface import *
    
sv_gravity = ConVarRef('sv_gravity')

@entity('npc_dota_tower')
@entity('dota_tower_good')
class TowerGood(UnitBaseAutoTurret):
    pitchturnspeed = 2000.0
    yawturnspeed = 2000.0
    firerate = 3.0
    
    def Precache(self):
        super(TowerGood, self).Precache()
        
        self.PrecacheSound('Tower.Fire.Attack')
    
    def Fire(self, bulletcount, attacker=None, ingorespread=False):
        if not self.enemy:
            return
        vFirePos = Vector()
        att = self.LookupAttachment('attach_attack1')
        self.GetAttachment(att, vFirePos)

        HomingProjectile.SpawnProjectile(self, vFirePos, self.enemy, 200.0, 300.0, particleeffect='ranged_tower_good')#, pexplosioneffect='ranged_tower_good_explosion')
        #HomingProjectile.SpawnProjectile(self, vFirePos, self.enemy, 100.0, 50.0, particleeffect='generic_projectile')
        self.EmitSound('Tower.Fire.Attack')
        
# Register unit
class TowerGoodInfo(WarsTurretInfo):
    name        = "build_tower_good"                            # unit_create name
    cls_name    = "dota_tower_good"                            # This entity is spawned and can be retrieved in the unit instance by GetUnitType()
    image_name  = "vgui/abilities/ability_rebelhq.vmt"      # Displayed in unit panel
    health      = 2000
    modelname   = 'models/props_structures/tower_good.mdl'
    sensedistance = 700.0
    
    