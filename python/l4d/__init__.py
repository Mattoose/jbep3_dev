from srcmgr import ImportSubMods, ReloadSubMods
from gamemgr import RegisterGamePackage

from srcbase import DMG_BULLET
from gamerules import GetAmmoDef, BULLET_IMPULSE

particles = [
    '!particles/error.pcf',
    'particles/steamworks.pcf',
    #'!particles/blood_fx.pcf',
    '!particles/boomer_fx.pcf',
    'particles/environmental_fx.pcf',
    'particles/fire_fx.pcf',
    '!particles/fire_infected_fx.pcf',
    '!particles/footstep_fx.pcf',
    '!particles/hunter_fx.pcf',
    '!particles/impact_fx.pcf',
    '!particles/infected_fx.pcf',
    'particles/rain_fx.pcf',
    '!particles/screen_fx.pcf',
    '!particles/smoker_fx.pcf',
    '!particles/survivor_fx.pcf',
    '!particles/tank_fx.pcf',
    '!particles/water_fx.pcf',
    '!particles/weapon_fx.pcf',
    'particles/environment_fx.pcf',
    'particles/burning_fx.pcf',
    'particles/fire_01.pcf',
    'particles/fire_01L4D.pcf',
    'particles/electrical_fx.pcf',
    'particles/steam_fx.pcf',
    'particles/locator_fx.pcf',
    '!particles/ui_fx.pcf',
    'particles/witch_fx.pcf',
    'particles/speechbubbles.pcf',
]
    
RegisterGamePackage(
    name=__name__,
    dependencies=['core'],
    #particles=particles,
)  

def LoadGame():
    """ Called on 'load_gamepackage l4d' """ 
    import units
    #import weapons
    
    ImportSubMods(units)
    
    #TRACER_LINE_AND_WHIZ = 4
    #GetAmmoDef().AddAmmoType("TF_AMMO_PRIMARY", DMG_BULLET, TRACER_LINE_AND_WHIZ, 10, 10, 40, BULLET_IMPULSE(200, 1225), 0 )
     
def ReloadGame():
    """ Called on 'reload_gamepackage l4d'. For development. """   
    # In case we are not loaded
    LoadGame()
    
    ReloadSubMods(units)
    #ReloadSubMods(weapons)
    