from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from basepowered import PoweredBuildingInfo, BaseFactoryPoweredBuilding
from entities import entity 

@entity('build_comb_synthfactory', networked=True)
class CombineSynthFactory(BaseFactoryPoweredBuilding, BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -210, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -250, 32)    
    
# Register unit
class SynthFactoryInfo(PoweredBuildingInfo):
    name = "build_comb_synthfactory" 
    displayname = "#BuildCombSyntFact_Name"
    description = "#BuildCombSyntFact_Description"
    cls_name = "build_comb_synthfactory"
    image_name = "vgui/abilities/ability_combbarracks.vmt"
    modelname = 'models/structures/combine/synthfac.mdl'
    techrequirements = ['build_comb_armory']
    costs = [('requisition', 12), ('power', 5)]
    health = 400
    buildtime = 60.0
    abilities   = {
        0 : 'unit_hunter',
        1 : 'unit_strider',
        2 : 'strider_unlock',
        8 : 'cancel',
    } 
    sound_select = 'build_comb_synthfactory'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = PoweredBuildingInfo.sai_hint | set(['sai_building_barracks'])