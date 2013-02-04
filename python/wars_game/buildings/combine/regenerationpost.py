#from wars_game.buildings.baseregeneration import BaseRegeneration
from core.buildings import WarsBuildingInfo

class CombineRegenerationPostInfo(WarsBuildingInfo):
    name = "build_comb_regenerationpost"
    displayname = "#BuildCombMedStation_Name"
    description = "#BuildCombMedStation_Description"
    cls_name = "build_baseregeneration"
    image_name  = "vgui/abilities/medstation.vmt"
    image_dis_name = "vgui/abilities/medstation_dis.vmt"
    modelname = 'models/props_combine/combine_generator01.mdl'
    health = 300
    buildtime = 25.0
    placemaxrange = 96.0
    costs = [[('requisition', 5)], [('kills', 5)]]
    techrequirements = ['build_comb_specialops']
    abilities   = {
        8 : 'cancel',
    } 
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_aid'])
    
class OverrunCombineRegenerationPostInfo(CombineRegenerationPostInfo):
    name = 'overrun_build_comb_regenerationpost'
    techrequirements = ['or_tier2_research']
    hidden = True