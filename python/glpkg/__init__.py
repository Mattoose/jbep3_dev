from gamemgr import RegisterGamePackage
    
# Register ( place this before registering gamerules/factions/abilities)
RegisterGamePackage( __name__ )    

import gamelobbyrules
import gamelobby_shared
if isclient:
    import ui.gamelobby_loadingpanel
    import ui.gamelobby_waitingforplayers
    import ui.gamelobby_minimap
    import ui.gamelobby_settings
    import ui.gamelobby
    
def LoadGame():
    """ Called on 'load_gamepackage wars_game' """
    pass
     
def ReloadGame():
    """ Called on 'reload_gamepackage wars_game'. For development. """  
    # Register again ( Clears all ability/factions/gamerules entries )
    RegisterGamePackage( __name__)
    
    reload(gamelobby_shared)
    
    # Reload gamelobby
    if isclient:
        reload(ui.gamelobby_loadingpanel)
        reload(ui.gamelobby_waitingforplayers)
        reload(ui.gamelobby_minimap)
        reload(ui.gamelobby_settings)
        reload(ui.gamelobby_playerentry)
        reload(ui.gamelobby)
    
    reload(gamelobbyrules)
    
    

    

