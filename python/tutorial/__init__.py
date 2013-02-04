from gamemgr import RegisterGamePackage
from srcmgr import ImportSubMods, ReloadSubMods

RegisterGamePackage(
        name=__name__,
        dependencies=['core']
)

def LoadGame():
    import gamerules
    import units
    import abilities
    
    ImportSubMods(gamerules)
    ImportSubMods(units)
    ImportSubMods(abilities)
    
def UnloadGame():  
    pass 
    
def ReloadGame():
    ReloadSubMods(gamerules)
    ReloadSubMods(units)
    ReloadSubMods(abilities)
        