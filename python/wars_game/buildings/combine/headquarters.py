from vmath import Vector, QAngle
from core.abilities import AbilityUpgrade, AbilityUpgradePopCap
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity

@entity('build_comb_hq', networked=True)
class CombineHQ(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(0, -350, 32)
    
@entity('build_comb_hq_overrun', networked=True)
class CombineHQOverrun(BaseClass):
    # Settings     
    buildtarget = Vector(400, 0, 48)
    buildangle = QAngle(0, 0, 0)   
    rallypoint = Vector(500, 0, 48)
    
# Normal gamemode
class CombineHQInfo(WarsBuildingInfo):
    name = 'build_comb_hq'
    displayname = '#BuildComHQ_Name'
    description = '#BuildComHQ_Description'
    cls_name = "build_comb_hq"
    image_name = 'vgui/combine/buildings/build_comb_hq'
    modelname = 'models/structures/combine/hq.mdl'
    costs = [('requisition', 20)]
    health = 2000
    buildtime = 100.0
    abilities = {
        0 : 'unit_stalker',
        1 : 'unit_metropolice',
        3 : 'unit_observer',
        8 : 'cancel',
        11 : 'comb_popupgrade1',
    }
    population = 0
    providespopulation = 20
    generateresources = ('requisition', 1, 10.0)
    sound_select = 'build_comb_hq'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (10, 100, 5, 6000) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_hq'])
    
class CombPopUpgrade1(AbilityUpgradePopCap):
    name = 'comb_popupgrade1'
    displayname = '#CombPopUpgr1_Name'
    description = '#CombPopUpgr1_Description'
    image_name = 'vgui/combine/abilities/comb_popupgrade1'
    successorability = 'comb_popupgrade2'
    popincrease = 20
    costs = [('requisition', 20)]
    
class CombPopUpgrade2(AbilityUpgradePopCap):
    name = 'comb_popupgrade2'
    displayname = '#CombPopUpgr2_Name'
    description = '#CombPopUpgr2_Description'
    image_name = 'vgui/combine/abilities/comb_popupgrade2'
    successorability = 'comb_popupgrade3'
    popincrease = 40
    costs = [('requisition', 20)]
    
class CombPopUpgrade3(AbilityUpgradePopCap):
    name = 'comb_popupgrade3'
    displayname = '#CombPopUpgr3_Name'
    description = '#CombPopUpgr3_Description'
    image_name = 'vgui/combine/abilities/comb_popupgrade3'
    popincrease = 60
    costs = [('requisition', 20)]
    
# OVERRUN version
class OverrunCombineHQInfo(WarsBuildingInfo):
    name = 'build_comb_hq_overrun'
    displayname = '#BuildComHQ_Name'
    description = '#BuildComHQ_Description'
    cls_name = 'build_comb_hq_overrun'
    image_name = 'vgui/combine/buildings/build_comb_hq'
    modelname = 'models/structures/combine/hq.mdl'
    health = 2000
    abilities   = {
        0 : 'overrun_unit_combine', 
        1 : 'overrun_unit_combine_sg',
        2 : 'overrun_unit_combine_ar2',
        3 : 'overrun_unit_combine_elite',
        4 : 'overrun_unit_combine_sniper',
        5 : 'overrun_unit_hunter',
        8 : 'or_tier2_research',
        10 : 'overrun_unit_metropolice',
        11 : 'overrun_unit_stalker',
    }
    population = 0
    providespopulation = 200
    generateresources = ('kills', 1, 20.0)
    hidden = True
    sound_select = 'build_comb_hq_overrun'
    sound_death = 'build_generic_explode1'
    explodeparticleeffect = 'building_explosion'
    explodeshake = (10, 100, 5, 6000) # Amplitude, frequence, duration, radius