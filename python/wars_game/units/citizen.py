from srcbase import DMG_GENERIC
from vmath import Vector
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass, EventHandlerAnimation
from fields import UpgradeField
from entities import entity, Activity
from unit_helper import UnitAnimConfig, LegAnimType_t, TranslateActivityMap
from gameinterface import CPASAttenuationFilter

if isserver:
    from unit_helper import BaseAnimEventHandler, TossGrenadeAnimEventHandler
    from animation import Animevent

@entity('unit_citizen', networked=True)
class UnitCitizen(BaseClass):    
    """ Citizen """
    def __init__(self):
        super(UnitCitizen, self).__init__()
    
    def Precache(self):
        super(UnitCitizen, self).Precache() 
        
        self.PrecacheScriptSound("NPC_Citizen.FootstepLeft")
        self.PrecacheScriptSound("NPC_Citizen.FootstepRight")
        self.PrecacheScriptSound("NPC_Citizen.Die")
        self.PrecacheScriptSound('HealthKit.Touch')
        
    def Spawn(self):
        super(UnitCitizen, self).Spawn() 
        
        self.animstate.usecombatstate = True
        
    def Heal(self, event=None):
        if not self.curorder or not self.curorder.ability:
            return
        target = self.curorder.target
        if not target:
            return
            
        if target.health == target.maxhealth:
            return
            
        if not self.curorder.ability.TakeEnergy(self):
            return
    
        timefullheal = 2.0
        timerecharge = 0.5
        #maximumhealamount = self.maxheal
        healamt = self.maxheal #(maximumhealamount * (1.0 - ( timefullheal - gpGlobals.curtime) / timerecharge))
        
        #print 'healamt: %f, energyregenrate: %f, maxenergy: %f' % (healamt, self.energyregenrate, self.maxenergy)
        
        #if healamt > maximumhealamount:
        #    healamt = maximumhealamount
        #else:
        healamt = int(round(healamt))
            
        filter = CPASAttenuationFilter(target, "HealthKit.Touch")
        self.EmitSoundFilter(filter, target.entindex(), "HealthKit.Touch")

        target.TakeHealth(healamt, DMG_GENERIC)
        target.RemoveAllDecals()
        
    # Anim event handlers
    if isserver:
        class RebelThrowGrenade(TossGrenadeAnimEventHandler):
            def HandleEvent(self, unit, event):
                if not unit.curorder:
                    return

                vStartPos = Vector()
                unit.GetAttachment( "anim_attachment_LH", vStartPos )

                vTarget = unit.curorder.position
                #UTIL_PredictedPosition( enemy, 0.5, vTarget ) 

                grenade = self.TossGrenade(unit, vStartPos, vTarget, unit.CalculateIgnoreOwnerCollisionGroup())
                
                if grenade:
                    grenade.SetVelocity(grenade.GetAbsVelocity(), Vector(0, 0, 0))
                    grenade.SetTimer(2.0, 2.0 - grenade.FRAG_GRENADE_WARN_TIME)
                    
    maxspeed = 209.0
    cantakecover = True
    
    maxheal = UpgradeField(value=50.0, abilityname='medic_healrate_upgrade')
    energyregenrate = UpgradeField(value=1.0, abilityname='medic_regenerate_upgrade')
    maxenergy = UpgradeField(abilityname='medic_maxenergy_upgrade', cppimplemented=True)
    
    REBEL_GRENADE_THROW_SPEED = 650
    
    # Activity list
    activitylist = list(BaseClass.activitylist)
    activitylist.extend([
        'ACT_CIT_HANDSUP',
        'ACT_CIT_BLINDED', # Blinded by scanner photo
        'ACT_CIT_SHOWARMBAND',
        'ACT_CIT_HEAL',
        'ACT_CIT_STARTLED', # Startled by sneaky scanner
        'ACT_RANGE_ATTACK_THROW',
        'ACT_WALK_AR2',
        'ACT_RUN_AR2',
        'ACT_WALK_AIM_AR2',
        'ACT_RUN_AIM_AR2',
    ])
    
    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_HEAL' : EventHandlerAnimation('ACT_CIT_HEAL'),
        'ANIM_THROWGRENADE' : EventHandlerAnimation('ACT_RANGE_ATTACK_THROW'),
    } )
    
    REBEL_AE_GREN_TOSS = 3005

    if isserver:
        aetable = {
            #'AE_CITIZEN_HEAL' : Heal, # ATM broken in asw, see heal.py
            REBEL_AE_GREN_TOSS : RebelThrowGrenade('grenade_frag', REBEL_GRENADE_THROW_SPEED),
            Animevent.AE_NPC_LEFTFOOT : BaseAnimEventHandler(),
        }
    
    # Activity translation table
    acttables = dict(BaseClass.acttables)
    acttables.update( { 
        'default' : {
            Activity.ACT_MP_JUMP_START : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_GLIDE,
            Activity.ACT_MP_JUMP_LAND : Activity.ACT_LAND,
        },
        'weapon_default' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_MP_JUMP_START : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_GLIDE,
            Activity.ACT_MP_JUMP_LAND : Activity.ACT_LAND,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER_LOW,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_AIM_SMG1_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        },
        'weapon_ar2' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE, #'ACT_WALK_AR2', # Broken, steve: fix model
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE, #'ACT_RUN_AR2', # Broken, steve: fix model
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_MP_JUMP_START : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_GLIDE,
            Activity.ACT_MP_JUMP_LAND : Activity.ACT_LAND,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER_LOW,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_AIM_SMG1_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE, # 'ACT_WALK_AIM_AR2', # TODO: Missing?
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE, # 'ACT_RUN_AIM_AR2', # TODO: Missing?
        },
        'weapon_rpg' : {
            Activity.ACT_IDLE : Activity.ACT_IDLE_RPG,
            Activity.ACT_WALK : Activity.ACT_WALK_RPG,
            Activity.ACT_RUN : Activity.ACT_RUN_RPG,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_RPG,
            Activity.ACT_MP_JUMP_START : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_GLIDE,
            Activity.ACT_MP_JUMP_LAND : Activity.ACT_LAND,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER_LOW,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_AIM_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_AIM_SMG1_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_RPG,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_RPG,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_RPG,
        }
    } )
    
    animconfig = UnitAnimConfig(
        maxbodyyawdegrees=60.0,
        leganimtype=LegAnimType_t.LEGANIM_8WAY,
        useaimsequences=False,
    )
    class AnimStateClass(BaseClass.AnimStateClass):
        def OnNewModel(self):
            super(UnitCitizen.AnimStateClass, self).OnNewModel()
            
            studiohdr = self.outer.GetModelPtr()
            
            self.bodyyaw = self.outer.LookupPoseParameter("body_yaw")
            self.bodypitch = self.outer.LookupPoseParameter("aim_pitch")
            
            aimyaw = self.outer.LookupPoseParameter(studiohdr, "aim_yaw")
            if aimyaw < 0:
                return
            self.outer.SetPoseParameter(studiohdr, aimyaw, 0.0)
            
            headpitch = self.outer.LookupPoseParameter(studiohdr, "head_pitch")
            if headpitch < 0:
                return
            headyaw = self.outer.LookupPoseParameter(studiohdr, "head_yaw")
            if headyaw < 0:
                return
            headroll = self.outer.LookupPoseParameter(studiohdr, "head_roll")
            if headroll < 0:
                return
                
            self.outer.SetPoseParameter(studiohdr, headpitch, 0.0)
            self.outer.SetPoseParameter(studiohdr, headyaw, 0.0)
            self.outer.SetPoseParameter(studiohdr, headroll, 0.0)
            
            spineyaw = self.outer.LookupPoseParameter(studiohdr, "spine_yaw")
            if spineyaw < 0:
                return
                
            self.outer.SetPoseParameter(studiohdr, spineyaw, 0.0)

usesinglemodel = False

if not usesinglemodel:
    randomheads = [
        "male_01.mdl",
        "male_02.mdl",
        "female_01.mdl",
        "male_03.mdl",
        "female_02.mdl",
        "male_04.mdl",
        "female_03.mdl",
        "male_05.mdl",
        "female_04.mdl",
        "male_06.mdl",
        "female_06.mdl",
        "male_07.mdl",
        "female_07.mdl",
        "male_08.mdl",
        "male_09.mdl",
    ]
    '''

    '''
    modellocs = {
        'DEFAULT' : 'Group01',
        'DOWNTRODDEN' : 'Group01',
        'REFUGEE' : 'Group02',
        'REBEL' : 'Group03',
        'MEDIC' : 'Group03m',
    }
    
else:
    randomheads = ['male_01.mdl']

    modellocs = {
        'DEFAULT' : 'Group03',
        'DOWNTRODDEN' : 'Group03',
        'REFUGEE' : 'Group03',
        'REBEL' : 'Group03',
        'MEDIC' : 'Group03',
    }

def GenerateModelList(type):
    modellist = []
    for head in randomheads:
        modellist.append( 'models/Humans/%s/%s' % (modellocs[type], head) )
    return modellist
    
# Register unit
class CitizenInfo(UnitInfo):
    name        = 'unit_citizen'
    cls_name    = 'unit_citizen'
    displayname = '#Citizen_Name'
    description = '#Citizen_Description'
    image_name = 'vgui/units/unit_shotgun.vmt'
    health = 50
    attributes = ['light']
    modellist = GenerateModelList('DEFAULT')
    hulltype = 'HULL_HUMAN'
    abilities = {
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
