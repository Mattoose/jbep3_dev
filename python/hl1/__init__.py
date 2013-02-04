from srcmgr import ImportSubMods, ReloadSubMods
from gamemgr import RegisterGamePackage

from srcbase import DMG_BULLET
from gamerules import GetAmmoDef, BULLET_IMPULSE

RegisterGamePackage(
        name=__name__,
        dependencies=['core'],
)  

def LoadGame():
    """ Called on 'load_gamepackage asw' """ 
    import units
     
    ImportSubMods(units)
    
    #TRACER_LINE_AND_WHIZ = 4
    #GetAmmoDef().AddAmmoType("ASW_R", DMG_BULLET, TRACER_LINE_AND_WHIZ, 10, 10, 40, BULLET_IMPULSE(200, 1225), 0 )
     
def ReloadGame():
    """ Called on 'reload_gamepackage asw'. For development. """   
    # In case we are not loaded
    LoadGame()
    
    ReloadSubMods(units)