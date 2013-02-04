#from wars_game.buildings.baseregeneration import BaseRegeneration
from core.buildings import WarsBuildingInfo
from wars_game.buildings.baseregeneration import BaseRegeneration as BaseClass
from entities import entity

@entity('build_rebelregeneration')
class BaseRegeneration(BaseClass):
    healradius = 350.0
    
class RebelsAidStationInfo(WarsBuildingInfo):
    name = "build_reb_aidstation"
    displayname = "#BuildRebAidStation_Name"
    description = "#BuildRebAidStation_Description"
    cls_name = "build_rebelregeneration"
    image_name = 'vgui/rebels/buildings/build_reb_aidstation'
    modelname = 'models/structures/resistance/aidstation.mdl'
    health = 300
    buildtime = 25.0
    placemaxrange = 260.0
    costs = [[('requisition', 5)], [('kills', 5)]]
    techrequirements = []
    abilities   = {
        8 : 'cancel',
    } 
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_aid'])
    
class OverrunRebelsAidStationInfo(RebelsAidStationInfo):
    name = "overrun_build_reb_aidstation"
    techrequirements = ['or_tier2_research']
    hidden = True