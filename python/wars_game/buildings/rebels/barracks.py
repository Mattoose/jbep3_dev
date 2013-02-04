from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity 

@entity('build_reb_barracks')
class RebelsBarracks(BaseClass):
    # Settings     
    autoconstruct = False
    buildtarget = Vector(0, -210, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -250, 32)    

# Register unit
class RebelHQInfo(WarsBuildingInfo):
    name        = "build_reb_barracks"
    displayname = '#BuildRebBarracks_Name'
    description = '#BuildRebBarracks_Description'
    cls_name    = "build_reb_barracks"
    image_name  = 'vgui/rebels/buildings/build_reb_barracks'
    modelname = 'models/structures/resistance/barracks.mdl'
    techrequirements = ['build_reb_hq']
    costs = [('requisition', 5)]
    health = 600
    buildtime = 50.0
    abilities   = {
        0 : 'unit_rebel_partisan',
        1 : 'unit_rebel', 
        2 : 'unit_rebel_medic', 
        8 : 'cancel',
    } 
    sound_select = 'build_reb_barracks'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_barracks'])
