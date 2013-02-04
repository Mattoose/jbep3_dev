from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from core.abilities import AbilityUpgrade
from entities import entity

@entity('build_reb_hq', networked=True)
class RebelsHQ(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -350, 32)    
    
# Register unit
class RebelHQInfo(WarsBuildingInfo):
    name        = "build_reb_hq" 
    cls_name    = "build_reb_hq"
    displayname = '#BuildRebHQ_Name'
    description = '#BuildRebHQ_Description'
    image_name  = 'vgui/rebels/buildings/build_reb_hq'
    modelname = 'models/structures/resistance/hq.mdl'
    costs = [('requisition', 20)]
    health = 2000
    buildtime = 100.0
    unitenergy = 100
    abilities   = {
        0 : 'unit_rebel_engineer',
        1 : 'unit_rebel_scout',
        7 : 'scan',
        8 : 'cancel',
    }
    population = 0
    providespopulation = 20
    generateresources = ('requisition', 1, 10.0)
    sound_select = 'build_reb_hq'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (10, 100, 5, 6000) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_hq'])

# OVERRUN version
class OverrunRebelHQInfo(WarsBuildingInfo):
    name = 'build_reb_hq_overrun'
    cls_name    = "build_reb_hq"
    displayname = '#BuildRebHQ_Name'
    description = '#BuildRebHQ_Description'
    image_name  = 'vgui/rebels/buildings/build_reb_hq'
    modelname = 'models/structures/resistance/hq.mdl'
    costs = [('requisition', 20)]
    health = 2000
    buildtime = 100.0
    #unitenergy = 100
    abilities   = {
        0 : 'overrun_unit_rebel_partisan',
        1 : 'overrun_unit_rebel',
        2 : 'overrun_unit_rebel_engineer',
        3 : 'overrun_unit_rebel_sg',
        4 : 'overrun_unit_rebel_ar2',
        5 : 'overrun_unit_rebel_medic',
        6 : 'overrun_unit_rebel_veteran',
        7 : 'overrun_unit_rebel_rpg',
        11 : 'overrun_unit_vortigaunt',
        8 : 'or_tier2_research',
    }
    population = 0
    providespopulation = 200
    generateresources = ('kills', 1, 20.0)
    sound_select = 'build_reb_hq'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (10, 100, 5, 6000) # Amplitude, frequence, duration, radius