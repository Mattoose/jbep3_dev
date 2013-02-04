from citizen import UnitInfo, UnitCitizen, GenerateModelList
from entities import entity
from core.abilities import AbilityTransformUnit, AbilityUpgrade, AbilityUpgradeValue, SubMenu

# Rebel engineer
@entity('unit_rebel_engineer')
class UnitRebelEngineer(UnitCitizen):
    carryingscrap = None
    
# Rebel scout
@entity('unit_rebel_scout')
class UnitRebelScout(UnitCitizen):
    maxspeed = 300.0
    
class RebelShared(UnitInfo):
    cls_name = 'unit_citizen'
    health = 160
    attributes = ['light', 'bullet']
    modellist = GenerateModelList('REBEL')
    hulltype = 'HULL_HUMAN'
    abilities = {
        0 : 'grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class RebelScoutInfo(RebelShared):
    name = 'unit_rebel_scout'
    displayname = '#RebScout_Name'
    description = '#RebScout_Description'
    cls_name = 'unit_rebel_scout'
    health = 35
    buildtime = 15.0
    costs = [('requisition', 1)]
    image_name  = 'vgui/rebels/units/unit_rebel_scout'
    abilities = {
        0 : 'infiltrate',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_pistol']
    sai_hint = set(['sai_unit_scout'])
    accuracy = 'low'

class RebelPartisanInfo(RebelShared):
    name = 'unit_rebel_partisan'
    displayname = '#RebPartisan_Name'
    description = '#RebPartisan_Description'
    buildtime = 15.0
    health = 40
    modellist = GenerateModelList('DEFAULT')
    costs = [[('requisition', 1)], [('kills', 1)]]
    image_name  = 'vgui/rebels/units/unit_rebel_partisan'
    abilities = {
        0 : 'revolutionaryfervor',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_smg1']
    accuracy = 'low'
    
class RebelInfo(RebelShared):
    name = 'unit_rebel'
    buildtime = 25.0
    costs = [[('requisition', 3)], [('kills', 1)]]
    displayname = '#RebSMG_Name'
    description = '#RebSMG_Description'
    image_name  = 'vgui/rebels/units/unit_rebel'
    weapons = ['weapon_smg1']
    abilities = {
        0 : 'grenade',
        4 : 'rebel_transform_sg',
        5 : 'rebel_transform_ar2',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class RebelSGInfo(RebelShared):
    name = 'unit_rebel_sg'
    displayname = '#RebSG_Name'
    description = '#RebSG_Description'
    buildtime = 25.0
    costs = [[('requisition', 2)], [('kills', 2)]]
    weapons = ['weapon_shotgun']
    image_name  = 'vgui/rebels/units/unit_rebel_sg'
    
class RebelAR2Info(RebelShared):
    name = 'unit_rebel_ar2'
    displayname = '#RebAR2_Name'
    description = '#RebAR2_Description'
    buildtime = 25.0
    costs = [[('requisition', 4)], [('kills', 3)]]
    weapons = ['weapon_ar2']
    image_name  = 'vgui/rebels/units/unit_rebel_ar2'
    
class RebelMedicInfo(RebelShared):
    name = 'unit_rebel_medic'
    buildtime = 45.0
    unitenergy = 100
    costs = [[('requisition', 4), ('scrap', 2)], [('kills', 2)]]
    displayname = '#RebMedic_Name'
    description = '#RebMedic_Description'
    image_name  = 'vgui/rebels/units/unit_rebel_medic'
    modellist = GenerateModelList('MEDIC')
    abilities = {
        0 : 'heal',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_pistol']
    
class RebelEngineerInfo(RebelShared):
    name = 'unit_rebel_engineer'
    cls_name = 'unit_rebel_engineer'
    buildtime = 20.0
    health = 95
    costs = [[('requisition', 2)], [('kills', 2)]]
    displayname = '#RebEngineer_Name'
    description = '#RebEngineer_Description'
    image_name  = 'vgui/rebels/units/unit_rebel_engineer'
    abilities = {
        10 : 'salvage',
        11 : 'construct',
        8 : 'attackmove',
        9 : 'holdposition',
        6 : 'mountturret',
        
        7 : SubMenu(name='engie_menu', displayname='#RebMenu_Name', description='#RebMenu_Description', abilities={
            0 : 'build_reb_hq',
            1 : 'build_reb_billet',
            2 : 'build_reb_barracks',
            3 : 'build_reb_munitiondepot',
            4 : 'build_reb_triagecenter',
            5 : 'rebels_mountableturret',
            6 : 'build_reb_vortigauntden',
            7 : 'build_reb_aidstation',
            8 : 'build_reb_specialops',
            11 : 'menuup',
        } )
    }
    weapons = ['weapon_smg1']
    sai_hint = set(['sai_unit_builder', 'sai_unit_combat'])
    
class RebelRPGUnlock(AbilityUpgrade):
    name = 'rebel_rpg_unlock'
    displayname = '#RebRPGUnlock_Name'
    description = '#RebRPGUnlock_Description'
    image_name = 'vgui/rebels/abilities/rebel_rpg_unlock'
    buildtime = 120.0
    costs = [('requisition', 10), ('scrap', 5)]
    
class RebelRPGInfo(RebelShared):
    name = 'unit_rebel_rpg'
    buildtime = 70.0
    costs = [[('requisition', 10), ('scrap', 4)], [('kills', 5)]]
    displayname = '#RebRPG_Name'
    description = '#RebRPG_Description'
    image_name  = 'vgui/rebels/units/unit_rebel_rpg'
    abilities = {
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_rpg']
    techrequirements = ['rebel_rpg_unlock']
    population = 2
    attributes = ['light', 'rpg']
    
class RebelVeteranUnlock(AbilityUpgrade):
    name = 'rebel_veteran_unlock'
    displayname = '#RebVeteranUnlock_Name'
    description = '#RebVeteranUnlock_Description'
    image_name = 'vgui/rebels/abilities/rebel_veteran_unlock'
    buildtime = 120.0
    costs = [('requisition', 10), ('scrap', 5)]
    
class RebelVeteran(RebelShared):
    name = 'unit_rebel_veteran'
    buildtime = 60.0
    health = 240
    attributes = ['heavy', 'bullet']
    costs = [[('requisition', 6), ('scrap', 1)], [('kills', 4)]]
    displayname = '#RebVeteran_Name'
    description = '#RebVeteran_Description'
    image_name  = 'vgui/rebels/units/unit_rebel_veteran'
    abilities = {
        0 : 'grenade',
        2 : 'weaponswitch_ar2',
        3 : 'weaponswitch_shotgun',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    weapons = ['weapon_shotgun', 'weapon_ar2']
    techrequirements = ['rebel_veteran_unlock']
    accuracy = 'high'
    population = 2

# Transform abilities Rebel soldier
class TransformToRebelSG(AbilityTransformUnit):
    name = 'rebel_transform_sg'
    displayname = '#RebTransSG_Name'
    description = '#RebTransSG_Description'
    transformtype = 'unit_rebel_sg'
    replaceweapons = True
    techrequirements = ['weaponsg_unlock']
    costs = [('scrap', 2)]
    image_name = 'vgui/rebels/abilities/rebel_transform_sg'
    
class TransformToRebelAR2(AbilityTransformUnit):
    name = 'rebel_transform_ar2'
    displayname = '#RebTransAR2_Name'
    description = '#RebTransAR2_Description'
    transformtype = 'unit_rebel_ar2'
    replaceweapons = True
    techrequirements = ['weaponar2_unlock']
    costs = [('scrap', 2)]
    image_name = 'vgui/rebels/abilities/rebel_transform_ar2'
    
# Medic upgrades
class MedicHealRateUpgrade(AbilityUpgradeValue):
    name = 'medic_healrate_upgrade'
    displayname = '#RebMedHealRateUpgr_Name'
    description = '#RebMedHealRateUpgr_Description'
    buildtime = 150.0
    costs = [('requisition', 5)]
    upgradevalue = 75.0
    image_name = 'vgui/rebels/abilities/medic_healrate_upgrade'
    
class MedicEnergyRegenRateUpgrade(AbilityUpgradeValue):
    name = 'medic_regenerate_upgrade'
    displayname = '#MedEnRegRateUpgr_Name'
    description = '#MedEnRegRateUpgr_Description'
    buildtime = 150.0
    costs = [('requisition', 5)]
    upgradevalue = 5.0
    image_name = 'vgui/rebels/abilities/medic_regenerate_upgrade'
    
class MedicMaxEnergyUpgrade(AbilityUpgradeValue):
    name = 'medic_maxenergy_upgrade'
    displayname = '#MedMaxEnUpgr_Name'
    description = '#MedMaxEnUpgr_Description'
    buildtime = 150.0
    costs = [('requisition', 5)]
    upgradevalue = 150
    image_name = 'vgui/rebels/abilities/medic_maxenergy_upgrade'
    
# Overrun versions
class OverrunRebelPartisanInfo(RebelPartisanInfo):
    name = 'overrun_unit_rebel_partisan'
    hidden = True
    buildtime = 0

class OverrunRebelInfo(RebelInfo):
    name = 'overrun_unit_rebel'
    hidden = True
    buildtime = 0
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunRebelSGInfo(RebelSGInfo):
    name = 'overrun_unit_rebel_sg'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunRebelEngineerInfo(RebelEngineerInfo):
    name = 'overrun_unit_rebel_engineer'
    hidden = True
    buildtime = 0
    abilities = {
        2 : 'overrun_floor_turret',
        3 : 'overrun_combine_mine',
        4 : 'overrun_reb_mountableturret',
        5 : 'overrun_build_reb_aidstation',
        8 : 'attackmove',
        9 : 'holdposition',
        10 : 'construct',
    }
    
class OverrunRebelAR2Info(RebelAR2Info):
    name = 'overrun_unit_rebel_ar2'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    abilities = {
        0 : 'overrun_grenade',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunRebelMedicInfo(RebelMedicInfo):
    name = 'overrun_unit_rebel_medic'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    abilities = {
        0 : 'heal',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    
class OverrunRebelRPGInfo(RebelRPGInfo):
    name = 'overrun_unit_rebel_rpg'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    
class OverrunRebelVeteranInfo(RebelVeteran):
    name = 'overrun_unit_rebel_veteran'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    abilities = {
        0 : 'overrun_grenade',
        2 : 'weaponswitch_ar2',
        3 : 'weaponswitch_shotgun',
        7 : 'mountturret',
        8 : 'attackmove',
        9 : 'holdposition',
    }
    