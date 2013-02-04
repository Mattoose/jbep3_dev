from srcbase import *
from vmath import *
from core.units import UnitInfo, UnitBaseCombat as BaseClass
from unit_helper import UnitAnimConfig, LegAnimType_t
from entities import entity, Activity, ACT_INVALID

class UnitDota(BaseClass):
    def CanBecomeRagdoll(self): return False

    # Vars
    maxspeed = 290.0
    yawspeed = 40.0
    jumpheight = 40.0
    attackmelee1act = 'ACT_DOTA_ATTACK'
    
    # Activity list
    activitylist = list(BaseClass.activitylist)
    activitylist.extend( [
        'ACT_DOTA_IDLE',
        'ACT_DOTA_IDLE_RARE',
        'ACT_DOTA_ATTACK',
        'ACT_DOTA_RUN',
        'ACT_DOTA_CAST_ABILITY_1',
        'ACT_DOTA_CAST_ABILITY_2',
        'ACT_DOTA_CAST_ABILITY_3',
        'ACT_DOTA_CAST_ABILITY_4',
        'ACT_DOTA_CAST_ABILITY_5',
        'ACT_DOTA_CAST_ABILITY_6',
        'ACT_DOTA_DISABLED',
        'ACT_DOTA_DIE',
        'ACT_DOTA_CAPTURE',
        'ACT_DOTA_FLAIL',
        'ACT_DOTA_CHANNEL_ABILITY_1',
        'ACT_DOTA_CHANNEL_ABILITY_2',
        'ACT_DOTA_CHANNEL_ABILITY_3',
        'ACT_DOTA_CHANNEL_ABILITY_4',
        'ACT_DOTA_CHANNEL_ABILITY_5',
        'ACT_DOTA_CHANNEL_ABILITY_6',
    ] )

    # Animation translation table
    acttables = {
        Activity.ACT_IDLE : 'ACT_DOTA_IDLE',
        Activity.ACT_RUN : 'ACT_DOTA_RUN',
        Activity.ACT_MELEE_ATTACK1 : 'ACT_DOTA_ATTACK',
        Activity.ACT_DIESIMPLE : 'ACT_DOTA_DIE',
        #Activity.ACT_MP_JUMP : 'ACT_',
        #Activity.ACT_MP_JUMP_FLOAT : 'ACT_',
    }
    
    animconfig = UnitAnimConfig(
        maxbodyyawdegrees=0.0,
        leganimtype=LegAnimType_t.LEGANIM_9WAY,
        #useaimsequences=True,
        invertposeparameters=False,
    )
    class AnimStateClass(BaseClass.AnimStateClass):
        def __init__(self, outer, animconfig):
            super(UnitDota.AnimStateClass, self).__init__(outer, animconfig)
            self.newjump = False
            
        def OnNewModel(self):
            super(UnitDota.AnimStateClass, self).OnNewModel()

            self.turn = self.outer.LookupPoseParameter("turn")
            if self.turn >= 0:
                self.outer.SetPoseParameter(self.turn, 0.0)
                
# Register unit
class UnitDotaInfo(UnitInfo):
    abilities = {
        8 : "attackmove",
        9 : "holdposition",
    }
    
    class AttackMelee(UnitInfo.AttackMelee):
        maxrange = 150.0
        damage = 50
        damagetype = DMG_SLASH
        attackspeed = 1.6
    attacks = 'AttackMelee'
    