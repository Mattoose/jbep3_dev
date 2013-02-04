from srcmgr import ImportSubMods, ReloadSubMods
from gamemgr import RegisterGamePackage
from core.factions import FactionInfo
from core.resources import resource_types

from vmath import Vector
from core.units import CreateUnit, CreateUnitNoSpawn
if isserver: from entities import DispatchSpawn
from utils import UTIL_FindPosition, FindPositionInfo

RESOURCE_GRUB = 'grubs'
RESOURCE_KILLS = 'kills'
RESOURCE_REQUISITION = 'requisition'
RESOURCE_POWER = 'power'
RESOURCE_SCRAP = 'scrap'

__all__ = ['gamerules']
if isclient:
    __all__ += ['hud']
    
RegisterGamePackage(
        name=__name__,
        dependencies=['core'],
)  

def LoadFactions():
    class FactionAntlionInfo(FactionInfo):
        name = 'antlions'
        displayname = 'Antlions'
        hud_name = 'classic_hud'
        startbuilding = 'build_ant_colony'
        startunit = 'unit_antlionguard'
        resources = ['grubs']
        
        @staticmethod
        def PopulateStartSpot(info, gamerules, startspot, ownernumber, playerSteamID=None):
            if not info.startbuilding or not info.startunit:
                PrintWarning('Faction %s has no start building or unit specified! Unable to populate start spot.\n')
                return
                
            # Spawn start building
            if info.startbuilding:
                unit = CreateUnitNoSpawn(info.startbuilding)
                unit.SetAbsOrigin(startspot.GetAbsOrigin())
                unit.SetAbsAngles(startspot.GetAbsAngles())
                unit.SetOwnerNumber(ownernumber)
                unit.KeyValue('startgrubs', gamerules.startgrubs) # TODO: move to antlion gamerules
                DispatchSpawn(unit)
                unit.Activate()  
            
            # Spawn a start unit (todo: offset?)
            if info.startunit:
                unit = CreateUnit( 'unit_antlionguardcavern', startspot.GetAbsOrigin()+Vector(270, 0, 48), startspot.GetAbsAngles(), ownernumber)
                if unit:
                    findinfo = UTIL_FindPosition(FindPositionInfo(startspot.GetAbsOrigin()+Vector(270, 0, 48), unit.WorldAlignMins(), unit.WorldAlignMaxs(), 0, 128, ignore=unit))
                    unit.SetAbsOrigin(findinfo.position)
            
    class FactionCombineInfo(FactionInfo):
        name = 'combine'
        displayname = 'Combine'
        hud_name = 'rebels_hud'
        startbuilding = 'build_comb_hq'
        startunit = 'unit_stalker'
        resources = ['requisition', 'power']
        soundcpcaptured = 'combine_cp_captured'
        soundcplost = 'combine_cp_lost'
        soundunitcomplete = 'combine_unit_complete'
        soundresearchcomplete = 'combine_unit_researchcomplete'
        
    class FactionRebelsInfo(FactionInfo):
        name = 'rebels'
        displayname = 'Rebels'
        hud_name = 'rebels_hud'
        startbuilding = 'build_reb_hq'
        startunit = 'unit_rebel_engineer'
        resources = ['requisition', 'scrap']
        
    class FactionCombineOverrunInfo(FactionCombineInfo):
        name = 'overrun_combine'
        displayname = 'Combine'
        hud_name = 'rebels_hud'
        startbuilding = 'build_comb_hq_overrun'
        startunit = 'overrun_unit_stalker'
        resources = ['kills']
        
    class FactionRebelsOverrunInfo(FactionRebelsInfo):
        name = 'overrun_rebels'
        displayname = 'Rebels'
        hud_name = 'rebels_hud'
        startbuilding = 'build_reb_hq_overrun'
        startunit = 'overrun_unit_rebel_engineer'
        resources = ['kills']
        

        
def LoadGame():
    """ Called on 'load_gamepackage wars_game' """    
    # Import
    import hud
    import ents
    import abilities
    import weapons
    import units
    import buildings
    import gamerules

    if isserver:
        import strategicai
    
    # Initialize resources
    resource_types[RESOURCE_GRUB]
    resource_types[RESOURCE_KILLS]
    resource_types[RESOURCE_REQUISITION]
    resource_types[RESOURCE_POWER]
    resource_types[RESOURCE_SCRAP]
    
    # Include all sub packages here from which we import all modules.
    # The modules will register info like the entity factory, gamerules, etc
    if isclient:
        ImportSubMods(hud)
    ImportSubMods(ents)
    ImportSubMods(abilities)
    ImportSubMods(abilities.powers)
    ImportSubMods(weapons)
    ImportSubMods(units)
    ImportSubMods(buildings)
    ImportSubMods(buildings.combine)
    ImportSubMods(buildings.rebels)
    ImportSubMods(gamerules)
    
    LoadFactions()
    
def ReloadGame():
    """ Called on 'reload_gamepackage wars_game'. For development. """   
    # In case we are not loaded
    LoadGame()
    
    # Reload the hud
    if isclient:
        ReloadSubMods(hud)
    reload(hud)
    
    # Reload ents
    ReloadSubMods(ents)
        
    # Reload abilities
    ReloadSubMods(abilities.powers)
    ReloadSubMods(abilities)
    
    # Buildings
    reload(buildings.pheromone_marker)
    reload(buildings.dynmountableturret)
    reload(buildings.baseregeneration)
    
    reload(buildings.combine.basepowered)
    ReloadSubMods(buildings.combine, [buildings.combine.basepowered])
    reload(buildings.combine)
    ReloadSubMods(buildings.rebels)
    reload(buildings.rebels)

    ReloadSubMods(buildings, [buildings.pheromone_marker, buildings.dynmountableturret, buildings.baseregeneration])
    reload(buildings)

    # Weapons
    ReloadSubMods(weapons)
    reload(weapons)
    
    # Units
    reload(units.basezombie)
    reload(units.basehelicopter)
    reload(units.citizen)
    ReloadSubMods(units, [units.basezombie, units.basehelicopter, units.citizen])
    
    # Gamerules
    ReloadSubMods(gamerules)

    if isserver:
        reload(strategicai)
    
    LoadFactions()
        
     