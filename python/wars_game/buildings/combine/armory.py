from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from basepowered import PoweredBuildingInfo, BaseFactoryPoweredBuilding
from entities import entity 

@entity('build_comb_armory', networked=True)
class CombineArmory(BaseFactoryPoweredBuilding, BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -210, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -250, 32)    
    
# Register unit
class ArmoryInfo(PoweredBuildingInfo):
    name = 'build_comb_armory' 
    displayname = '#BuildCombArmory_Name'
    description = '#BuildCombArmory_Description'
    cls_name = 'build_comb_armory'
    image_name = 'vgui/combine/buildings/build_comb_armory'
    modelname = 'models/structures/combine/Armory.mdl'
    techrequirements = ['build_comb_garrison']
    costs = [('requisition', 10), ('power', 2)]
    health = 500
    buildtime = 50.0
    abilities = {
        0 : 'grenade_unlock',
        1 : 'combine_mine_unlock',
        2 : 'floor_turret_unlock',
        4 : 'weaponsg_unlock',
        5 : 'weaponar2_unlock',
        8 : 'cancel',
        10 : 'combine_elite_unlock',
        11 : 'combine_sniper_unlock',
    } 
    sound_select = 'build_comb_armory'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = PoweredBuildingInfo.sai_hint | set(['sai_building_research'])