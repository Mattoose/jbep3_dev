from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity

@entity('build_reb_triagecenter', networked=True)
class RebelsTriageCenter(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -350, 32)    
    
# Register unit
class TriageCenterInfo(WarsBuildingInfo):
    name        = "build_reb_triagecenter" 
    displayname = "#BuildRebTriCent_Name"
    description = "#BuildRebTriCent_Description"
    cls_name    = "build_reb_triagecenter"
    image_name  = 'vgui/rebels/buildings/build_reb_triagecenter'
    modelname = 'models/structures/resistance/triagecenter.mdl'
    costs = [('requisition', 5), ('scrap', 2)]
    health = 500
    buildtime = 50.0
    techrequirements = ['build_reb_barracks']
    abilities   = {
        0 : 'medic_healrate_upgrade',
        1 : 'medic_regenerate_upgrade',
        2 : 'medic_maxenergy_upgrade',
        8 : 'cancel',
    } 
    sound_select = 'build_reb_triagecenter'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_research'])