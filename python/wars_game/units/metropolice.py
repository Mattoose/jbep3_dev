import random
from srcbase import *
from vmath import *
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass, EventHandlerAnimation, CreateUnitNoSpawn, PrecacheUnit
from entities import entity, Activity

@entity('unit_metropolice', networked=True)
class UnitMetroPolice(BaseClass):    
    """ Combine metro police. """
    if isserver:
        def Precache(self):
            super(UnitMetroPolice, self).Precache()
            
            PrecacheUnit('unit_manhack')

    def ReleaseManhacks(self):
        for manhack in self.manhacks:
            # Make us physical
            manhack.RemoveSpawnFlags(manhack.SF_MANHACK_CARRIED)

            # Release us
            manhack.RemoveSolidFlags(FSOLID_NOT_SOLID)
            manhack.SetParent(None)
            
            # Fix pitch/roll
            angles = manhack.GetAbsAngles()
            angles.x = 0.0
            angles.z = 0.0
            manhack.SetAbsAngles(angles)

            # Make us active
            manhack.DispatchEvent('Release')
    
    def StartDeployManhackHandler(self, event):
        # TODO
        '''
        if self.nummanhacks <= 0:
            DevMsg("Error: Throwing manhack but out of manhacks!\n")
            return

        self.nummanhacks -= 1

        # Turn off the manhack on our body
        if self.nummanhacks <= 0:
            SetBodygroup(METROPOLICE_BODYGROUP_MANHACK, false)
        '''
        
        self.manhacks = []
        
        for i in range(0, 1):
            # Create the manhack to throw
            manhack = CreateUnitNoSpawn("unit_manhack", owner_number=self.GetOwnerNumber())
            
            vecOrigin = Vector()
            vecAngles = QAngle()

            handAttachment = self.LookupAttachment( "LHand" )
            self.GetAttachment(handAttachment, vecOrigin, vecAngles)

            manhack.SetLocalOrigin(vecOrigin)
            manhack.SetLocalAngles(vecAngles)
            manhack.AddSpawnFlags(manhack.SF_MANHACK_PACKED_UP|manhack.SF_MANHACK_CARRIED)

            manhack.Spawn()
            manhack.behaviorgeneric.StartingAction = manhack.behaviorgeneric.ActionPreDeployed
            
            # Make us move with his hand until we're deployed
            manhack.SetParent(self, handAttachment)

            self.manhacks.append(manhack)
        
    def DeployManhackHandler(self, event):
        self.ReleaseManhacks()
        
        # todo
        for manhack in self.manhacks:
            forward = Vector()
            right = Vector()
            
            self.GetVectors(forward, right, None)
            
            yawOff = right * random.uniform(-1.0, 1.0)

            forceVel = (forward + yawOff * 16.0) + Vector(0, 0, 250)

            manhack.SetAbsVelocity(manhack.GetAbsVelocity() + forceVel)

        self.manhacks = []
        
    manhacks = None

    METROPOLICE_BODYGROUP_MANHACK = 1
        
    # Activity translation table
    acttables = dict(BaseClass.acttables)
    acttables.update( { 
        'default' : {
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
        },
        'weapon_pistol' : {
            Activity.ACT_IDLE : Activity.ACT_RANGE_ATTACK_PISTOL,
            Activity.ACT_WALK : Activity.ACT_WALK_AIM_PISTOL,
            Activity.ACT_RUN : Activity.ACT_RUN_AIM_PISTOL,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
        },
        'weapon_stunstick' : {
            Activity.ACT_MELEE_ATTACK1 : Activity.ACT_MELEE_ATTACK_SWING,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_MELEE_ATTACK_SWING,
        },
    } )
    
    # Custom activities
    activitylist = list(BaseClass.activitylist)
    activitylist.extend([
        'ACT_METROPOLICE_DRAW_PISTOL',
        'ACT_METROPOLICE_DEPLOY_MANHACK',
        'ACT_METROPOLICE_FLINCH_BEHIND',

        'ACT_WALK_BATON',
        'ACT_IDLE_ANGRY_BATON',
        'ACT_PUSH_PLAYER',
        'ACT_MELEE_ATTACK_THRUST',
        'ACT_ACTIVATE_BATON',
        'ACT_DEACTIVATE_BATON',
    ])
    
    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_DEPLOYMANHACK' : EventHandlerAnimation('ACT_METROPOLICE_DEPLOY_MANHACK'),
    } )
    
    # Ability sounds
    abilitysounds = {
        'grenade' : 'ability_combine_grenade',
        'deployturret' : 'ability_combine_deployturret',
        'deploymine' : 'ability_combine_deploymine',
        'deploymanhacks' : 'ability_combine_deploymanhacks',
    }

    if isserver:
        aetable = {
            'AE_METROPOLICE_BATON_ON' : None,
            'AE_METROPOLICE_BATON_OFF' : None,
            'AE_METROPOLICE_SHOVE' : None,
            'AE_METROPOLICE_START_DEPLOY' : StartDeployManhackHandler,
            'AE_METROPOLICE_DRAW_PISTOL' : None,
            'AE_METROPOLICE_DEPLOY_MANHACK' : DeployManhackHandler,
        }
    
    class AnimStateClass(BaseClass.AnimStateClass):
        def __init__(self, outer, animconfig):
            super(UnitMetroPolice.AnimStateClass, self).__init__(outer, animconfig)
            self.newjump = False
            
        def OnNewModel(self):
            super(UnitMetroPolice.AnimStateClass, self).OnNewModel()
            
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

class MetroPoliceInfo(UnitInfo):
    name = 'unit_metropolice'
    cls_name = 'unit_metropolice'
    hulltype = 'HULL_HUMAN'
    displayname = '#CombMetroPolice_Name'
    description = '#CombMetroPolice_Description'
    image_name = 'vgui/combine/units/unit_metropolice'
    portrait = 'resource/portraits/combineSMG.bik'
    costs = [[('requisition', 3)], [('kills', 1)]]
    buildtime = 25.0
    health = 180
    attributes = ['light', 'bullet']
    sound_select = 'unit_combine_select'
    sound_move = 'unit_combine_move'
    sound_attack = 'unit_combine_attack'
    modelname = 'models/police.mdl'
    abilities = {
        0 : 'combine_mine',
        1 : 'floor_turret',
        2 : 'deploymanhack',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_pistol']
    accuracy = 'low'
    
    sound_abilities = {
        'grenade' : 'ability_combine_grenade',
        'floor_turret' : 'ability_combine_deployturret',
    }
    
class OverrunMetroPoliceInfo(MetroPoliceInfo):
    name = 'overrun_unit_metropolice'
    hidden = True
    buildtime = 0
    abilities = {
        0 : 'overrun_combine_mine',
        1 : 'overrun_floor_turret',
        2 : 'deploymanhack',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    accuracy = 'low'
    