from srcmgr import ImportSubMods, ReloadSubMods
from gamemgr import RegisterGamePackage
from particles import ReadParticleConfigFile

particles = [
    # Base
    'particles/rain_fx.pcf',
    #'particles/blood_impact.pcf',
    'particles/water_impact.pcf',
    '!particles/error.pcf',
    'particles/base_destruction_fx.pcf',
    'particles/base_attacks.pcf',
    '!particles/ui_mouseactions.pcf',
    '!particles/generic_hero_status.pcf',
    'particles/generic_gameplay.pcf',
    'particles/items_fx.pcf',
    'particles/items2_fx.pcf',
    '!particles/speechbubbles.pcf',
    'particles/world_creature_fx.pcf',
    '!particles/world_destruction_fx.pcf',
    'particles/world_environmental_fx.pcf',
    '!particles/status_fx.pcf',
    'particles/radiant_fx.pcf',
    'particles/radiant_fx2.pcf',
    'particles/dire_fx.pcf',
    '!particles/msg_fx.pcf',
    '!particles/siege_fx.pcf',
    '!particles/neutral_fx.pcf',
    
    # Heroes
    'particles/units/heroes/hero_doom_bringer.pcf',
    'particles/units/heroes/hero_skeletonking.pcf',
]
        
RegisterGamePackage(
        name=__name__,
        dependencies=['core'],
        #particles=particles.
)  

def LoadGame():
    """ Called on 'load_gamepackage dota' """ 
    # Read
    import units
    import buildings
    import ents
    
    ImportSubMods(units)
    ImportSubMods(buildings)
    ImportSubMods(ents)
    
def ReloadGame():
    """ Called on 'reload_gamepackage dota'. For development. """   
    # In case we are not loaded
    LoadGame()
    
    reload(units.basedota)
    ReloadSubMods(units, [units.basedota])
    ReloadSubMods(buildings)
    ReloadSubMods(ents)
    