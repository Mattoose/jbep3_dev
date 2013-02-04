from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from basepowered import PoweredBuildingInfo, BaseFactoryPoweredBuilding
from entities import entity 

@entity('build_comb_specialops', networked=True)
class CombineSpecialOps(BaseFactoryPoweredBuilding, BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -210, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -250, 32)    
    
# Register unit
class SpecialOpsInfo(PoweredBuildingInfo):
    name = 'build_comb_specialops'
    displayname = '#BuildCombSpecOps_Name'
    description = '#BuildCombSpecOps_Description'
    cls_name = 'build_comb_specialops'
    image_name = 'vgui/combine/buildings/build_comb_specialops'
    modelname = 'models/structures/combine/SpecOps.mdl'
    techrequirements = ['build_comb_armory']
    costs = [('requisition', 12), ('power', 5)]
    health = 500
    buildtime = 60.0
    abilities   = {
        0 : 'unit_combine_elite',
        1 : 'unit_combine_sniper',
        8 : 'cancel',
    } 
    sound_select = 'build_comb_specialops'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = PoweredBuildingInfo.sai_hint | set(['sai_building_barracks'])