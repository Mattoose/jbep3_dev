from srcmgr import ImportSubMods, ReloadSubMods
from gamemgr import RegisterGamePackage
from core.factions import FactionInfo
from core.resources import resource_types
from gameinterface import AddSearchPath

RegisterGamePackage(
        name=__name__,
        dependencies=['core'],
)  


def LoadGame():
    """ Called on 'load_gamepackage zm' """
    AddSearchPath('zmcontent', 'GAME')
    
    # Import
    import player
    import gamerules
    import units
    import ents
    if isclient:
        import hud
        
    resource_types['zombiepool']
        
    # Include all sub packages here from which we import all modules.
    # The modules will register info like the entity factory, gamerules, etc
    ImportSubMods(player)
    ImportSubMods(gamerules)
    ImportSubMods(units)
    ImportSubMods(ents)
    if isclient:
        ImportSubMods(hud)
    
def ReloadGame():
    """ Called on 'reload_gamepackage zm'. For development. """   
    # In case we are not loaded
    LoadGame()
    
    reload(shared)
    ReloadSubMods(player)
    ReloadSubMods(gamerules)
    ReloadSubMods(units)
    ReloadSubMods(ents)
    
    if isclient:
        ReloadSubMods(hud)
        reload(hud)
        
'''
if isserver:
    from gameinterface import concommand
    from utils import UTIL_GetCommandClient
    @concommand('zm_test')
    def Test(args):
        from entities import RespawnPlayer
        
        RespawnPlayer(UTIL_GetCommandClient(), 'zm_player_survivor')
'''