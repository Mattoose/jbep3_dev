from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from basepowered import PoweredBuildingInfo, BaseFactoryPoweredBuilding
from entities import entity 

@entity('build_comb_garrison', networked=True)
class CombineGarrison(BaseFactoryPoweredBuilding, BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -210, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -250, 32)    
    
# Register unit
class GarrisonInfo(PoweredBuildingInfo):
    name        = 'build_comb_garrison'
    displayname = '#BuildCombGar_Name'
    description = '#BuildCombGar_Description'
    cls_name    = 'build_comb_garrison'
    image_name  = 'vgui/combine/buildings/build_comb_garrison'
    modelname = 'models/structures/combine/barracks.mdl'
    techrequirements = ['build_comb_hq']
    costs = [('requisition', 5)]
    health = 600
    buildtime = 50.0
    abilities   = {
        0 : "unit_metropolice",
        1 : "unit_combine",
        8 : 'cancel',
    } 
    sound_select = 'build_comb_garrison'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = PoweredBuildingInfo.sai_hint | set(['sai_building_barracks'])