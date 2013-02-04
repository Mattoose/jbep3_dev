from core.buildings import WarsBuildingInfo, UnitBaseBuilding as BaseClass
from entities import entity

@entity('build_comb_barricade')
class CombineBarricade(BaseClass):
    autoconstruct = False

class CombineBarricadeInfo(WarsBuildingInfo):
    name        = 'build_comb_barricade'
    displayname = '#BuildCombBarricade_Name'
    description = '#BuildCombBarricade_Description'
    cls_name    = 'build_comb_barricade'
    image_name  = 'vgui/abilities/ability_combbarracks.vmt'
    modelname = 'models/props_combine/combine_barricade_short01a.mdl'
    health = 100
    buildtime = 5.0
    placemaxrange = 96.0
    abilities   = {
        8 : 'cancel',
    } 
    