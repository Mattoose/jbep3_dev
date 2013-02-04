from vmath import Vector
from wars_game.buildings.dynmountableturret import UnitDynMountableTurret, WarsDynMountTurretInfo
from entities import entity

# TODO: Make different from the combine one
@entity('rebels_mountableturret', networked=True)
class UnitRebelsMountableTurret(UnitDynMountableTurret):
    def GetTracerType(self): return "AR2Tracer"

    autoconstruct = False
    aimtype = UnitDynMountableTurret.AIMTYPE_POSE
    barrelattachmentname = 'muzzle'
    ammotype = 'AR2'
    firesound = "NPC_FloorTurret.ShotSounds"
    muzzleoptions = 'COMBINE muzzle'

class MountableTurretInfo(WarsDynMountTurretInfo):
    # Info
    name = "rebels_mountableturret"
    cls_name = "rebels_mountableturret"
    displayname = "#BuildRebMountTurret_Name"
    description = "#BuildRebMountTurret_Description"
    modelname = 'models/props_combine/bunker_gun01.mdl'
    image_name  = "vgui/abilities/ability_combmountgun.vmt"
    image_dis_name = "vgui/abilities/ability_combmountgun_dis.vmt"
    health = 400
    buildtime = 25.0
    costs = [[('requisition', 5)], [('kills', 5)]]
    techrequirements = ['build_reb_barracks']
    zoffset = 28.0
    population = 0
    manpoint = Vector(-38, 0, 0)
    
    abilities = {
        8 : 'cancel',
    }
    
    dummies = [{
        'modelname' : 'models/props_combine/combine_barricade_short01a.mdl',
        'offset' : Vector(0, 0, -2),
    }]
    
    # Ability
    infoprojtextures = [
        {'texture' : 'decals/turret_cone_120',
         'mins' : Vector(16, -1039, 0),
         'maxs' : Vector(1216, 1039, 128)},
        {'texture' : 'decals/ycircle',
         'offset' : manpoint,
         'mins' : -Vector(16, 16, 0),
         'maxs' : Vector(16, 16, 48)},
    ]
    
    class AttackTurret(WarsDynMountTurretInfo.AttackTurret):
        damage = 10
        attackspeed = 0.1
    attacks = 'AttackTurret'
    
class OverrunMountableTurretInfo(MountableTurretInfo):
    name = "overrun_reb_mountableturret"
    techrequirements = ['or_tier3_research']
    hidden = True
    