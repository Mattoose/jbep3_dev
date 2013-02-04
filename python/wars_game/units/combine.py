from vmath import Vector
from core.abilities import AbilityUpgrade, AbilityTransformUnit
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass, EventHandlerAnimation
from entities import entity, Activity
import ndebugoverlay

if isserver:
    from animation import Animevent
    from unit_helper import BaseAnimEventHandler, TossGrenadeAnimEventHandler

# from fields import UpgradeField, OutputField
# from core.abilities.upgrade import AbilityUpgradeValue

# class TestUpgrade(AbilityUpgradeValue):
    # name = 'testupgrade'
    # upgradevalue = 25
    # successorability = 'testupgrade2'
    
# class TestUpgrade2(AbilityUpgradeValue):
    # name = 'testupgrade2'
    # upgradevalue = 50

@entity('unit_combine', networked=True)
class UnitCombine(BaseClass):    
    """ Combine soldier. """
    if isserver:
        def DeathSound(self):
            self.expresser.SpeakRawSentence('COMBINE_DIE', 0.0)
            
    def Spawn(self):
        super(UnitCombine, self).Spawn()
        
        self.animstate.usecombatstate = True
        
        if isserver:
            if self.activeweapon and self.activeweapon.GetClassname() == 'weapon_shotgun':
                self.skin = self.COMBINE_SKIN_SHOTGUNNER

    # Anim event handlers
    if isserver:
        class CombineThrowGrenade(TossGrenadeAnimEventHandler):
            def HandleEvent(self, unit, event):
                if not unit.curorder:
                    return

                vStartPos = Vector()
                unit.GetAttachment( "lefthand", vStartPos )

                vTarget = unit.curorder.position
                #UTIL_PredictedPosition( enemy, 0.5, vTarget ) 

                grenade = self.TossGrenade(unit, vStartPos, vTarget, unit.CalculateIgnoreOwnerCollisionGroup())

                if grenade:
                    grenade.SetVelocity(grenade.GetAbsVelocity(), Vector(0, 0, 0))
                    grenade.SetTimer( 2.0, 2.0 - grenade.FRAG_GRENADE_WARN_TIME )
                    
    maxspeed = 214.78
    cantakecover = True
    
    COMBINE_SKIN_DEFAULT = 0
    COMBINE_SKIN_SHOTGUNNER = 1
    
    COMBINE_GRENADE_THROW_SPEED = 650
    
    attackrange1act = Activity.ACT_RANGE_ATTACK_SMG1
    
    #test = UpgradeField(abilityname='testupgrade')
    
    # Activity list
    activitylist = list(BaseClass.activitylist)
    activitylist.extend([
        'ACT_IDLE_UNARMED',
        'ACT_WALK_UNARMED',
        'ACT_COMBINE_THROW_GRENADE',
    ])
    
    # Activity translation table
    acttables = dict(BaseClass.acttables)
    acttables.update( { 
        'default' : {
            Activity.ACT_IDLE : 'ACT_IDLE_UNARMED',
            Activity.ACT_WALK : 'ACT_WALK_UNARMED',
            Activity.ACT_RUN : Activity.ACT_RUN_AIM_RIFLE,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SMG1_LOW, 
        },
        'weapon_smg1' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SMG1_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        },
        'weapon_shotgun' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SHOTGUN_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_SHOTGUN,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_SHOTGUN,
        },
        'weapon_ar2' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_AR2_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        },
        
        'weapon_sniperrifle' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_AR2_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        }
    } )
    
    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_THROWGRENADE' : EventHandlerAnimation('ACT_COMBINE_THROW_GRENADE'),
    } )
    
    # Ability sounds
    abilitysounds = {
        'grenade' : 'ability_combine_grenade',
        'deployturret' : 'ability_combine_deployturret',
    }
    
    if isserver:
        # Animation Events
        COMBINE_AE_GREN_TOSS = 7
        
        aetable = {
            Animevent.AE_NPC_BODYDROP_HEAVY : BaseAnimEventHandler(),
            COMBINE_AE_GREN_TOSS : CombineThrowGrenade('grenade_frag', COMBINE_GRENADE_THROW_SPEED),
        }
    
    # Anims
    class AnimStateClass(BaseClass.AnimStateClass):
        def __init__(self, outer, animconfig):
            super(UnitCombine.AnimStateClass, self).__init__(outer, animconfig)
            self.newjump = False
            
@entity('unit_combinesniper', networked=True)
class UnitCombineSniper(UnitCombine):    
    canshootmove = False
    
# Register unit
class CombineSharedInfo(UnitInfo):
    cls_name = 'unit_combine'
    population = 1
    hulltype = 'HULL_HUMAN'
    attributes = ['light', 'bullet']
    
class CombineInfo(CombineSharedInfo):
    name = 'unit_combine'
    displayname = '#CombSMG_Name'
    description = '#CombSMG_Description'
    image_name = 'vgui/combine/units/unit_combine'
    portrait = 'resource/portraits/combineSMG.bik'
    costs = [[('requisition', 4)], [('kills', 1)]]
    buildtime = 40.0
    health = 200
    sound_select = 'unit_combine_select'
    sound_move = 'unit_combine_move'
    sound_attack = 'unit_combine_attack'
    modelname = 'models/combine_soldier.mdl'
    abilities = {
        0 : 'grenade',
        4 : 'combine_transform_sg',
        5 : 'combine_transform_ar2',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
        -1 : 'garrison',
    }
    weapons = ['weapon_smg1']
    
class CombineSGInfo(CombineSharedInfo):
    name = 'unit_combine_sg'
    displayname = '#CombSG_Name'
    description = '#CombSG_Description'
    image_name = 'vgui/combine/units/unit_combine_sg'
    portrait = 'resource/portraits/combineShotgun.bik'
    costs = [[('requisition', 2)], [('kills', 2)]]
    buildtime = 30.0
    health = 200
    sound_select = 'unit_combine_sg_select'
    sound_move = 'unit_combine_sg_move'
    sound_attack = 'unit_combine_sg_attack'
    modelname = 'models/combine_soldier.mdl'
    abilities = {
        0 : 'grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_shotgun']
    
class CombineAR2Info(CombineSharedInfo):
    name = 'unit_combine_ar2'
    displayname = '#CombAR2_Name'
    description = '#CombAR2_Description'
    image_name = 'vgui/combine/units/unit_combine_ar2'
    portrait = 'resource/portraits/combineAR2.bik'
    costs = [[('requisition', 4)], [('kills', 3)]]
    buildtime = 30.0
    health = 200
    sound_select = 'unit_combine_ar2_select'
    sound_move = 'unit_combine_ar2_move'
    sound_attack = 'unit_combine_ar2_attack'
    modelname = 'models/combine_soldier.mdl'
    abilities = {
        0 : 'grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_ar2']
    
class CombineEliteUnlock(AbilityUpgrade):
    name = 'combine_elite_unlock'
    displayname = '#CombEliteUnlock_Name'
    description = '#CombEliteUnlock_Description'
    image_name = "vgui/combine/abilities/combine_elite_unlock"
    buildtime = 120.0
    costs = [[('requisition', 5)], [('kills', 5)]]
    
class CombineEliteInfo(CombineSharedInfo):
    name = 'unit_combine_elite'
    displayname = '#CombElite_Name'
    description = '#CombElite_Description'
    image_name = 'vgui/combine/units/unit_combine_elite'
    portrait = 'resource/portraits/combineAR2.bik'
    costs = [[('requisition', 6), ('power', 1)], [('kills', 7)]]
    buildtime = 70.0
    health = 300
    attributes = ['heavy', 'bullet']
    techrequirements = ['combine_elite_unlock']
    selectionpriority = 1
    sound_select = 'unit_combine_elite_select'
    sound_move = 'unit_combine_elite_move'
    sound_attack = 'unit_combine_elite_attack'
    modelname = 'models/combine_super_soldier.mdl'
    abilities = {
        0 : 'weaponswitch_ar2',
        1 : 'weaponswitch_shotgun',
        3 : 'combineball',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_shotgun', 'weapon_ar2']
    accuracy = 'high'
    population = 2
    
class CombineSniperUnlock(AbilityUpgrade):
    name = 'combine_sniper_unlock'
    displayname = '#CombSniperUnlock_Name'
    description = '#CombSniperUnlock_Description'
    image_name = 'vgui/combine/abilities/combine_sniper_unlock'
    buildtime = 120.0
    costs = [[('requisition', 5)], [('kills', 5)]]
    
class CombineSniperInfo(CombineSharedInfo):
    name = 'unit_combine_sniper'
    cls_name = 'unit_combinesniper'
    displayname = '#CombSniper_Name'
    description = '#CombSniper_Description'
    image_name = 'vgui/combine/units/unit_combine_sniper'
    portrait = 'resource/portraits/combineSMG.bik'
    costs = [[('requisition', 12), ('power', 4)], [('kills', 5)]]
    buildtime = 60.0
    health = 105
    sensedistance = 2048.0
    techrequirements = ['combine_sniper_unlock']
    sound_select = 'unit_combine_select'
    sound_move = 'unit_combine_move'
    sound_attack = 'unit_combine_attack'
    modelname = 'models/combine_soldier.mdl'
    abilities = {
        0 : 'marksmanshot',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_sniperrifle']
    accuracy = 'high'
    population = 3

# OVERRUN VERSIONS
class OverrunCombineInfo(CombineInfo):
    name = 'overrun_unit_combine'
    hidden = True
    buildtime = 0
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunCombineSGInfo(CombineSGInfo):
    name = 'overrun_unit_combine_sg'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunCombineAR2Info(CombineAR2Info):
    name = 'overrun_unit_combine_ar2'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunCombineEliteInfo(CombineEliteInfo):
    name = 'overrun_unit_combine_elite'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    abilities = {
        0 : 'combineball',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunCombineSniperInfo(CombineSniperInfo):
    name = 'overrun_unit_combine_sniper'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    
# Transform abilities combine soldier
class TransformToCombineSG(AbilityTransformUnit):
    name = 'combine_transform_sg'
    displayname = '#CombTransSG_Name'
    description = '#CombTransSG_Description'
    image_name = 'vgui/combine/abilities/combine_transform_sg'
    transformtype = 'unit_combine_sg'
    replaceweapons = True
    techrequirements = ['weaponsg_unlock']
    costs = [('requisition', 1), ('power', 2)]
    activatesoundscript = 'ability_combine_shotgun_upgrade'

class TransformToCombineAR2(AbilityTransformUnit):
    name = 'combine_transform_ar2'
    displayname = '#CombTransAR2_Name'
    description = '#CombTransAR2_Description'
    image_name = 'vgui/combine/abilities/combine_transform_ar2'
    transformtype = 'unit_combine_ar2'
    replaceweapons = True
    techrequirements = ['weaponar2_unlock']
    costs = [('requisition', 2), ('power', 2)]
    activatesoundscript = 'ability_combine_ar2_upgrade'
