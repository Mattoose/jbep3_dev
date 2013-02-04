from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity

@entity('build_reb_munitiondepot', networked=True)
class RebelsMunitionDepot(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -350, 32)    
    
# Register unit
class MuntionDepotInfo(WarsBuildingInfo):
    name        = "build_reb_munitiondepot" 
    displayname = "#BuildRebMunDepot_Name"
    description = "#BuildRebMunDepot_Description"
    cls_name    = "build_reb_munitiondepot"
    image_name  = 'vgui/rebels/buildings/build_reb_munitiondepot'
    modelname = 'models/structures/resistance/Armory.mdl'
    costs = [('requisition', 5), ('scrap', 2)]
    health = 500
    buildtime = 50.0
    techrequirements = ['build_reb_barracks']
    abilities   = {
        0 : 'grenade_unlock',
        1 : 'combine_mine_unlock',
        2 : 'weaponsg_unlock',
        3 : 'weaponar2_unlock',
        8 : 'cancel',
        10 : 'rebel_rpg_unlock',
        11 : 'rebel_veteran_unlock',
    } 
    sound_select = 'build_reb_munitiondepot'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_research'])